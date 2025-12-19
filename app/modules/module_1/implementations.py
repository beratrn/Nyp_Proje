"""
Hasta Yönetim Modülü - Implementation Sınıfları
Bu modül hasta tiplerinin somut implementasyonlarını ve servis katmanını içerir.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from base import Patient, PatientStatus, Gender, BloodType

# ENTITY CLASSES - Veri Modelleri
@dataclass
class VitalSigns:
    """
    Hayati bulguları tutan veri sınıfı
    """
    timestamp: datetime
    temperature: float  # Celsius
    blood_pressure_systolic: int  # mmHg
    blood_pressure_diastolic: int  # mmHg
    heart_rate: int  # bpm
    respiratory_rate: int  # breaths per minute
    oxygen_saturation: float  # percentage
    
    def is_critical(self) -> bool:
        """Hayati bulguların kritik seviyede olup olmadığını kontrol eder"""
        return (
            self.temperature > 39.0 or self.temperature < 35.0 or
            self.blood_pressure_systolic > 180 or self.blood_pressure_systolic < 90 or
            self.heart_rate > 120 or self.heart_rate < 50 or
            self.oxygen_saturation < 90
        )
    
    def __str__(self) -> str:
        return (f"Vital Signs: Temp={self.temperature}°C, "
                f"BP={self.blood_pressure_systolic}/{self.blood_pressure_diastolic}, "
                f"HR={self.heart_rate}bpm, SpO2={self.oxygen_saturation}%")


@dataclass
class BedAssignment:
    """
    Yatak atama bilgilerini tutan veri sınıfı
    """
    bed_number: str
    room_number: str
    ward: str
    assignment_date: datetime
    is_icu: bool = False
    
    def get_location(self) -> str:
        """Yatağın tam konumunu döndürür"""
        location_type = "ICU" if self.is_icu else "Ward"
        return f"{location_type} - {self.ward}, Room {self.room_number}, Bed {self.bed_number}"


@dataclass
class Insurance:
    """
    Sigorta bilgilerini tutan veri sınıfı
    """
    provider: str
    policy_number: str
    coverage_percentage: float
    expiry_date: datetime
    
    def is_valid(self) -> bool:
        """Sigortanın geçerli olup olmadığını kontrol eder"""
        return datetime.now() < self.expiry_date
    
    def calculate_coverage(self, total_amount: float) -> float:
        """Sigorta kapsamını hesaplar"""
        if not self.is_valid():
            return 0.0
        return total_amount * (self.coverage_percentage / 100)


@dataclass
class EmergencyCase:
    """
    Acil durum bilgilerini tutan veri sınıfı
    """
    case_id: str
    arrival_time: datetime
    triage_level: int  # 1-5 (1 en acil)
    chief_complaint: str
    ambulance_arrival: bool = False
    notes: List[str] = field(default_factory=list)
    
    def get_waiting_time_minutes(self) -> int:
        """Bekleme süresini dakika cinsinden hesaplar"""
        return int((datetime.now() - self.arrival_time).total_seconds() / 60)

# PATIENT SUBCLASSES - Hasta Tipleri

class Inpatient(Patient):
    """
    Yatan hasta sınıfı - hastanede yatarak tedavi gören hastalar için
    
    Bu sınıf uzun süreli hastanede kalış gerektiren hastaları temsil eder.
    Yatak ataması, günlük bakım ve sürekli izleme gerektiren durumlarda kullanılır.
    """
    
    # Sabit değerler - sınıf düzeyinde
    DAILY_BASE_COST = 500.0
    ICU_MULTIPLIER = 3.0
    
    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        diagnosis: str,
        bed_assignment: Optional[BedAssignment] = None,
        **kwargs
    ):
        """
        Inpatient constructor
        
        Args:
            patient_id: Hasta kimlik numarası
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            diagnosis: Teşhis bilgisi
            bed_assignment: Yatak atama bilgisi
            **kwargs: Ek parametreler
        """
        super().__init__(patient_id, name, age, gender, **kwargs)
        self.diagnosis = diagnosis
        self.bed_assignment = bed_assignment
        self.vital_signs_history: List[VitalSigns] = []
        self.expected_discharge_date: Optional[datetime] = None
        self.daily_care_notes: List[str] = []
        self.requires_surgery = False
        self.surgery_date: Optional[datetime] = None
        
        # Başlangıç durumu
        self.update_status(PatientStatus.IN_TREATMENT)
    
    def calculate_treatment_cost(self) -> float:
        """
        Yatan hasta için tedavi maliyetini hesaplar.
        
        Maliyet hesaplaması:
        - Günlük temel maliyet
        - Yoğun bakımda ise 3 kat fazla
        - Kalış süresine göre çarpım
        - Ameliyat varsa %50 ek maliyet
        
        Returns:
            float: Toplam tedavi maliyeti
        """
        days = self.get_admission_duration_days()
        if days == 0:
            days = 1  # En az 1 gün
        
        base_cost = self.DAILY_BASE_COST * days
        
        # ICU faktörü
        if self.bed_assignment and self.bed_assignment.is_icu:
            base_cost *= self.ICU_MULTIPLIER
        
        # Ameliyat ek maliyeti
        if self.requires_surgery:
            base_cost *= 1.5
        
        return round(base_cost, 2)
    
    def get_priority_level(self) -> int:
        """
        Yatan hasta için öncelik seviyesini belirler.
        
        Returns:
            int: Öncelik seviyesi (1-10)
        """
        priority = 5  # Orta seviye başlangıç
        
        # ICU hastası ise yüksek öncelik
        if self.bed_assignment and self.bed_assignment.is_icu:
            priority = 9
        
        # Ameliyat günü ise öncelik artar
        if self.surgery_date and self.surgery_date.date() == datetime.now().date():
            priority += 2
        
        # Kritik vital signs varsa öncelik artar
        if self.vital_signs_history and self.vital_signs_history[-1].is_critical():
            priority = 10
        
        return min(priority, 10)  # Maksimum 10
    
    def requires_special_care(self) -> bool:
        """
        Özel bakım gereksinimini kontrol eder.
        
        Returns:
            bool: Özel bakım gerekiyorsa True
        """
         # ICU hastası her zaman özel bakım gerektirir
        if self.bed_assignment and self.bed_assignment.is_icu:
            return True
        
        # 65 yaş üstü özel bakım gerektirir
        if self.age >= 65:
            return True
        
        # Ameliyat olan hasta özel bakım gerektirir
        if self.requires_surgery:
            return True
        
        return False
    
    def add_vital_signs(self, vital_signs: VitalSigns) -> None:
        """
        Hayati bulgu kaydı ekler.
        
        Args:
            vital_signs: Eklenecek hayati bulgular
        """
        self.vital_signs_history.append(vital_signs)
        self._add_note(f"Vital signs recorded: {vital_signs}")
        
        if vital_signs.is_critical():
            self._add_note("WARNING: Critical vital signs detected!")
    
    def schedule_surgery(self, surgery_date: datetime) -> None:
        """
        Ameliyat tarihi planlar.
        
        Args:
            surgery_date: Ameliyat tarihi
        """
        self.requires_surgery = True
        self.surgery_date = surgery_date
        self._add_note(f"Surgery scheduled for {surgery_date.strftime('%Y-%m-%d %H:%M')}")
    
    def add_daily_care_note(self, note: str) -> None:
        """
        Günlük bakım notu ekler.
        
        Args:
            note: Bakım notu
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.daily_care_notes.append(f"[{timestamp}] {note}")
    
    def assign_bed(self, bed_assignment: BedAssignment) -> None:
        """
        Yatak ataması yapar.
        
        Args:
            bed_assignment: Yatak atama bilgisi
        """
        self.bed_assignment = bed_assignment
        self._add_note(f"Bed assigned: {bed_assignment.get_location()}")
    
    @classmethod
    def create_icu_patient(
        cls,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        diagnosis: str,
        **kwargs
    ) -> 'Inpatient':
        """
        Yoğun bakım hastası oluşturur.
        
        Args:
            patient_id: Hasta ID
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            diagnosis: Teşhis
            **kwargs: Ek parametreler
            
        Returns:
            Inpatient: ICU hastası
        """
        # Otomatik ICU yatak ataması
        icu_bed = BedAssignment(
            bed_number="ICU-001",
            room_number="ICU",
            ward="Intensive Care",
            assignment_date=datetime.now(),
            is_icu=True
        )
        
        patient = cls(patient_id, name, age, gender, diagnosis, icu_bed, **kwargs)
        patient._add_note("Patient admitted to ICU")
        return patient
    
    @staticmethod
    def estimate_recovery_days(diagnosis: str) -> int:
        """
        Teşhise göre tahmini iyileşme süresi hesaplar.
        
        Args:
            diagnosis: Teşhis bilgisi
            
        Returns:
            int: Tahmini gün sayısı
        """
        diagnosis_lower = diagnosis.lower()
        
        if "surgery" in diagnosis_lower or "operation" in diagnosis_lower:
            return 7
        elif "fracture" in diagnosis_lower:
            return 14
        elif "pneumonia" in diagnosis_lower:
            return 10
        elif "appendicitis" in diagnosis_lower:
            return 5
        else:
            return 3  # Varsayılan
    
    def to_dict(self) -> Dict[str, Any]:
        """Hasta bilgilerini dictionary'ye çevirir"""
        data = super().to_dict()
        data.update({
            "type": "inpatient",
            "diagnosis": self.diagnosis,
            "bed_assignment": self.bed_assignment.get_location() if self.bed_assignment else None,
            "is_icu": self.bed_assignment.is_icu if self.bed_assignment else False,
            "requires_surgery": self.requires_surgery,
            "surgery_date": self.surgery_date.isoformat() if self.surgery_date else None,
            "vital_signs_count": len(self.vital_signs_history),
            "treatment_cost": self.calculate_treatment_cost()
        })
        return data
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
    class Outpatient(Patient):
     """
     Ayakta tedavi gören hasta sınıfı
    
    Bu sınıf hastaneye sadece muayene, kontrol veya kısa süreli tedavi için
    gelen ve yatış gerektirmeyen hastaları temsil eder.
    """
    
    # Sınıf düzeyinde sabitler
    CONSULTATION_COST = 150.0
    FOLLOW_UP_COST = 100.0
    
    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        reason_for_visit: str,
        referring_doctor: Optional[str] = None,
        **kwargs
    ):
        """
        Outpatient constructor
        
        Args:
            patient_id: Hasta kimlik numarası
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            reason_for_visit: Başvuru nedeni
            referring_doctor: Sevk eden doktor
            **kwargs: Ek parametreler
        """
        super().__init__(patient_id, name, age, gender, **kwargs)
        self.reason_for_visit = reason_for_visit
        self.referring_doctor = referring_doctor
        self.visit_history: List[Dict[str, Any]] = []
        self.prescriptions: List[str] = []
        self.next_appointment: Optional[datetime] = None
        self.requires_follow_up = False
        self.treatment_completed = False
        
        # İlk ziyaret kaydı
        self._record_visit("Initial consultation")
    
    def calculate_treatment_cost(self) -> float:
        """
        Ayakta tedavi için maliyet hesaplar.
        
        Maliyet hesaplaması:
        - İlk konsültasyon: 150 TL
        - Her takip ziyareti: 100 TL
        - Toplam ziyaret sayısına göre
        
        Returns:
            float: Toplam tedavi maliyeti
        """
        visit_count = len(self.visit_history)
        
        if visit_count == 0:
            return 0.0
        
        # İlk ziyaret tam ücret
        total_cost = self.CONSULTATION_COST
        
        # Takip ziyaretleri indirimli
        if visit_count > 1:
            follow_ups = visit_count - 1
            total_cost += (follow_ups * self.FOLLOW_UP_COST)
        
        return round(total_cost, 2)
    
    def get_priority_level(self) -> int:
        """
        Ayakta tedavi hastası için öncelik seviyesi.
        
        Returns:
            int: Öncelik seviyesi (1-10)
        """
        # Ayakta tedavi hastası genel olarak düşük öncelikli
        priority = 3
        
        # Yaşlı hastalar daha öncelikli
        if self.age >= 70:
            priority = 5
        elif self.age >= 60:
            priority = 4
        
        # Çocuklar öncelikli
        if self.age < 12:
            priority = 5
        
        return priority
    
    def requires_special_care(self) -> bool:
        """
        Özel bakım gereksinimini kontrol eder.
        
        Returns:
            bool: Özel bakım gerekiyorsa True
        """
        # Ayakta tedavi hastası genelde özel bakım gerektirmez
        # Sadece çok küçük çocuklar veya çok yaşlı hastalar
        return self.age < 5 or self.age >= 75
    
    def _record_visit(self, notes: str) -> None:
        """
        Ziyaret kaydı ekler (internal metod).
        
        Args:
            notes: Ziyaret notları
        """
        visit = {
            "date": datetime.now(),
            "notes": notes,
            "doctor": self.referring_doctor if self.referring_doctor else "General Practitioner"
        }
        self.visit_history.append(visit)
        self._add_note(f"Visit recorded: {notes}")
    
    def schedule_follow_up(self, appointment_date: datetime) -> None:
        """
        Takip randevusu planlar.
        
        Args:
            appointment_date: Randevu tarihi
        """
        self.next_appointment = appointment_date
        self.requires_follow_up = True
        self._add_note(f"Follow-up scheduled for {appointment_date.strftime('%Y-%m-%d %H:%M')}")
    
    def add_prescription(self, prescription: str) -> None:
        """
        Reçete ekler.
        
        Args:
            prescription: Reçete bilgisi
        """
        if prescription:
            self.prescriptions.append(prescription)
            self._add_note(f"Prescription added: {prescription}")
    
    def complete_treatment(self) -> None:
        """Tedaviyi tamamlanmış olarak işaretler"""
        self.treatment_completed = True
        self.requires_follow_up = False
        self.update_status(PatientStatus.RECOVERED)
        self._add_note("Treatment completed successfully")
    
    def get_visit_count(self) -> int:
        """
        Toplam ziyaret sayısını döndürür.
        
        Returns:
            int: Ziyaret sayısı
        """
        return len(self.visit_history)
    
    @classmethod
    def create_routine_checkup(
        cls,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        **kwargs
    ) -> 'Outpatient':
        """
        Rutin kontrol için hasta oluşturur.
        
        Args:
            patient_id: Hasta ID
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            **kwargs: Ek parametreler
            
        Returns:
            Outpatient: Oluşturulan hasta
        """
        return cls(
            patient_id,
            name,
            age,
            gender,
            reason_for_visit="Routine checkup",
            **kwargs
        )
    
    @staticmethod
    def calculate_estimated_wait_time(current_queue_size: int) -> int:
        """
        Kuyruk boyutuna göre tahmini bekleme süresi hesaplar.
        
        Args:
            current_queue_size: Mevcut kuyruk boyutu
            
        Returns:
            int: Tahmini bekleme süresi (dakika)
        """
        # Her hasta için ortalama 15 dakika
        return current_queue_size * 15
    
    def to_dict(self) -> Dict[str, Any]:
        """Hasta bilgilerini dictionary'ye çevirir"""
        data = super().to_dict()
        data.update({
            "type": "outpatient",
            "reason_for_visit": self.reason_for_visit,
            "referring_doctor": self.referring_doctor,
            "visit_count": self.get_visit_count(),
            "prescriptions": self.prescriptions,
            "next_appointment": self.next_appointment.isoformat() if self.next_appointment else None,
            "requires_follow_up": self.requires_follow_up,
            "treatment_completed": self.treatment_completed,
            "treatment_cost": self.calculate_treatment_cost()
        })
        return data

class EmergencyPatient(Patient):
    """
    Acil hasta sınıfı - acil servise gelen hastalar için
    
    Bu sınıf acil müdahale gerektiren, hayati tehlikesi olan veya
    ani bir sağlık problemi yaşayan hastaları temsil eder.
    """
    
    # Sınıf düzeyinde sabitler
    TRIAGE_COSTS = {
        1: 2000.0,  # En acil
        2: 1500.0,
        3: 1000.0,
        4: 750.0,
        5: 500.0   # En az acil
    }
    
    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        emergency_case: EmergencyCase,
        **kwargs
    ):
        """
        EmergencyPatient constructor
        
        Args:
            patient_id: Hasta kimlik numarası
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            emergency_case: Acil durum bilgisi
            **kwargs: Ek parametreler
        """
        super().__init__(patient_id, name, age, gender, **kwargs)
        self.emergency_case = emergency_case
        self.stabilized = False
        self.requires_hospitalization = False
        self.critical_interventions: List[str] = []
        self.emergency_contacts_notified = False
        self.transferred_to_ward = False
        
        # Acil durum başlangıç durumu
        self.update_status(PatientStatus.IN_TREATMENT)
        self._add_note(f"Emergency admission: {emergency_case.chief_complaint}")
    
    def calculate_treatment_cost(self) -> float:
        """
        Acil hasta için tedavi maliyetini hesaplar.
        
        Maliyet hesaplaması:
        - Triyaj seviyesine göre temel maliyet
        - Ambulans ile geliş ise %20 ek
        - Kritik müdahaleler için ekstra maliyet
        - Hastaneye yatış gerekiyorsa %50 ek
        
        Returns:
            float: Toplam tedavi maliyeti
        """
        triage_level = self.emergency_case.triage_level
        base_cost = self.TRIAGE_COSTS.get(triage_level, 1000.0)
        
        # Ambulans faktörü
        if self.emergency_case.ambulance_arrival:
            base_cost *= 1.2
        
        # Kritik müdahale maliyetleri
        intervention_cost = len(self.critical_interventions) * 500.0
        base_cost += intervention_cost
        
        # Hastaneye yatış gerekiyorsa
        if self.requires_hospitalization:
            base_cost *= 1.5
        
        return round(base_cost, 2)
    
    def get_priority_level(self) -> int:
        """
        Acil hasta için öncelik seviyesini belirler.
        
        Triyaj seviyesi doğrudan önceliği belirler:
        - Triyaj 1 (En acil) = Öncelik 10
        - Triyaj 5 (En az acil) = Öncelik 6
        
        Returns:
            int: Öncelik seviyesi (1-10)
        """
        # Triyaj seviyesi 1-5, önceliğe ters çevirerek dönüştür
        triage = self.emergency_case.triage_level
        priority = 11 - triage  # 1->10, 2->9, 3->8, 4->7, 5->6
        
        # Stabilize edilmemişse maksimum öncelik
        if not self.stabilized:
            priority = 10
        
        return priority
    
    def requires_special_care(self) -> bool:
        """
        Özel bakım gereksinimini kontrol eder.
        
        Returns:
            bool: Özel bakım gerekiyorsa True
        """
        # Acil hastalar her zaman özel bakım gerektirir
        # Özellikle triyaj 1-2 hastalar
        return self.emergency_case.triage_level <= 3 or not self.stabilized
    
    def stabilize_patient(self) -> None:
        """Hastayı stabilize edilmiş olarak işaretler"""
        self.stabilized = True
        self._add_note("Patient stabilized")
    
    def add_critical_intervention(self, intervention: str) -> None:
        """
        Kritik müdahale kaydı ekler.
        
        Args:
            intervention: Müdahale açıklaması
        """
        if intervention:
            self.critical_interventions.append(intervention)
            self._add_note(f"Critical intervention: {intervention}")
    
    def notify_emergency_contacts(self) -> None:
        """Acil durum kişilerini bilgilendirilmiş olarak işaretler"""
        if not self.emergency_contacts_notified:
            self.emergency_contacts_notified = True
            self._add_note("Emergency contacts notified")
    
    def transfer_to_ward(self, ward_name: str) -> None:
        """
        Hastayı servise transfer eder.
        
        Args:
            ward_name: Servis adı
        """
        self.transferred_to_ward = True
        self.requires_hospitalization = True
        self.update_status(PatientStatus.TRANSFERRED)
        self._add_note(f"Patient transferred to {ward_name}")
    
    def get_waiting_time(self) -> int:
        """
        Acil serviste bekleme süresini döndürür.
        
        Returns:
            int: Bekleme süresi (dakika)
        """
        return self.emergency_case.get_waiting_time_minutes()
    
    def is_critical_case(self) -> bool:
        """
        Kritik vaka olup olmadığını kontrol eder.
        
        Returns:
            bool: Kritik vaka ise True
        """
        return self.emergency_case.triage_level <= 2
    
    @classmethod
    def create_trauma_patient(
        cls,
        patient_id: str,
        name: str,
        age: int,
        gender: Gender,
        injury_description: str,
        **kwargs
    ) -> 'EmergencyPatient':
        """
        Travma hastası oluşturur (triyaj seviye 1).
        
        Args:
            patient_id: Hasta ID
            name: Hasta adı
            age: Hasta yaşı
            gender: Hasta cinsiyeti
            injury_description: Yaralanma açıklaması
            **kwargs: Ek parametreler
            
        Returns:
            EmergencyPatient: Travma hastası
        """
        emergency_case = EmergencyCase(
            case_id=f"TRAUMA-{patient_id}",
            arrival_time=datetime.now(),
            triage_level=1,  # En yüksek aciliyet
            chief_complaint=injury_description,
            ambulance_arrival=True
        )
        
        patient = cls(patient_id, name, age, gender, emergency_case, **kwargs)
        patient._add_note("TRAUMA CASE - Immediate attention required")
        return patient
    
    @staticmethod
    def determine_triage_level(symptoms: List[str]) -> int:
        """
        Semptomlara göre triyaj seviyesi belirler.
        
        Args:
            symptoms: Semptom listesi
            
        Returns:
            int: Triyaj seviyesi (1-5)
        """
        critical_symptoms = ["chest pain", "difficulty breathing", "unconscious", 
                           "severe bleeding", "stroke symptoms"]
        urgent_symptoms = ["high fever", "severe pain", "head injury"]
        
        symptoms_lower = [s.lower() for s in symptoms]
        
        # Kritik semptom varsa triyaj 1
        if any(cs in " ".join(symptoms_lower) for cs in critical_symptoms):
            return 1
        
        # Acil semptom varsa triyaj 2
        if any(us in " ".join(symptoms_lower) for us in urgent_symptoms):
            return 2
        
        # Varsayılan triyaj 3
        return 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Hasta bilgilerini dictionary'ye çevirir"""
        data = super().to_dict()
        data.update({
            "type": "emergency",
            "triage_level": self.emergency_case.triage_level,
            "chief_complaint": self.emergency_case.chief_complaint,
            "arrival_time": self.emergency_case.arrival_time.isoformat(),
            "waiting_time_minutes": self.get_waiting_time(),
            "ambulance_arrival": self.emergency_case.ambulance_arrival,
            "stabilized": self.stabilized,
            "critical_interventions": self.critical_interventions,
            "requires_hospitalization": self.requires_hospitalization,
            "emergency_contacts_notified": self.emergency_contacts_notified,
            "is_critical": self.is_critical_case(),
            "treatment_cost": self.calculate_treatment_cost()
        })
        return data
# SERVICE LAYER - İş Mantığı Katmanı

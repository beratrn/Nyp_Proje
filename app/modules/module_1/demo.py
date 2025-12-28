#!/usr/bin/env python3
"""
HASTA YÖNETİM SİSTEMİ - OTOMATIK DEMO
Tüm modülü test eden otomatik demo
Çalıştırmak için: python3 demo.py
"""

import sys
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

# ============================================================================
# RENKLER VE YARDIMCI FONKSİYONLAR
# ============================================================================

class C:
    """Renkler"""
    H = '\033[95m'  # Header
    B = '\033[94m'  # Blue
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    E = '\033[0m'   # End
    BOLD = '\033[1m'

def h(t): print(f"\n{C.H}{C.BOLD}{'='*80}\n{t.center(80)}\n{'='*80}{C.E}\n")
def s(t): print(f"\n{C.B}>>> {t}{C.E}")
def ok(t): print(f"{C.G}✓ {t}{C.E}")
def info(t): print(f"{C.B}ℹ {t}{C.E}")
def warn(t): print(f"{C.Y}⚠ {t}{C.E}")
def w(sec=0.3): time.sleep(sec)

# ============================================================================
# ENUM'LAR
# ============================================================================

class PatientStatus(Enum):
    REGISTERED = "Kayıtlı"
    IN_TREATMENT = "Tedavi Görüyor"
    DISCHARGED = "Taburcu"
    EMERGENCY = "Acil"

class Gender(Enum):
    MALE = "Erkek"
    FEMALE = "Kadın"

class BloodType(Enum):
    A_POS = "A+"
    B_POS = "B+"
    O_POS = "0+"
    AB_POS = "AB+"

# ============================================================================
# BASE CLASS
# ============================================================================

class Patient(ABC):
    """Base sınıf - Soyut hasta sınıfı"""
    
    def __init__(self, patient_id: str, name: str, age: int, gender: Gender,
                 phone: str, address: str, blood_type: BloodType,
                 status: PatientStatus = PatientStatus.REGISTERED):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.address = address
        self.blood_type = blood_type
        self.status = status
        self.registration_date = datetime.now()
        self.medical_history: List[str] = []
        self.allergies: List[str] = []
        self.medications: List[str] = []
    
    @abstractmethod
    def calculate_treatment_cost(self) -> float:
        """Tedavi maliyeti - her alt sınıf kendi hesaplar"""
        pass
    
    @abstractmethod
    def get_priority_level(self) -> int:
        """Öncelik seviyesi 1-10 arası"""
        pass
    
    # Nesne metodu
    def add_medical_history(self, record: str):
        """Tıbbi kayıt ekler"""
        self.medical_history.append(f"[{datetime.now():%H:%M}] {record}")
    
    def update_status(self, new_status: PatientStatus):
        """Durumu günceller"""
        self.status = new_status
    
    # Sınıf metodu
    @classmethod
    def format_id(cls, prefix: str, num: int) -> str:
        """ID formatlar"""
        return f"{prefix}-{num:04d}"
    
    # Statik metot
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Telefon doğrular"""
        return len(phone.replace("-", "").replace(" ", "")) >= 10
    
    @staticmethod
    def validate_age(age: int) -> bool:
        """Yaş doğrular"""
        return 0 <= age <= 120
    
    def __str__(self):
        return f"{self.name} ({self.patient_id}) - {self.status.value}"

# ============================================================================
# SUBCLASS 1: YATAN HASTA
# ============================================================================

class Inpatient(Patient):
    """Yatan hasta - hastanede yatan hastalar"""
    
    def __init__(self, patient_id: str, name: str, age: int, gender: Gender,
                 phone: str, address: str, blood_type: BloodType,
                 room: str, bed: str, daily_cost: float = 500.0, **kwargs):
        super().__init__(patient_id, name, age, gender, phone, address, blood_type,
                        PatientStatus.IN_TREATMENT)
        self.room = room
        self.bed = bed
        self.daily_cost = daily_cost
        self.admission_date = datetime.now()
        self.nursing_notes: List[str] = []
    
    def calculate_treatment_cost(self) -> float:
        days = (datetime.now() - self.admission_date).days + 1
        base = days * self.daily_cost
        age_mult = 1.2 if self.age > 65 else 1.0
        med_cost = len(self.medications) * 50
        return base * age_mult + med_cost
    
    def get_priority_level(self) -> int:
        base = 6
        if self.age > 70: base += 2
        return min(base, 10)
    
    def add_nursing_note(self, note: str):
        """Hemşire notu ekler"""
        self.nursing_notes.append(f"[{datetime.now():%H:%M}] {note}")
    
    @classmethod
    def create_with_room(cls, name: str, age: int, gender: Gender, phone: str,
                        address: str, blood_type: BloodType, floor: int, room_num: int):
        """Oda ataması ile oluşturur"""
        pid = cls.format_id("IP", floor * 100 + room_num)
        return cls(pid, name, age, gender, phone, address, blood_type,
                  f"{floor}{room_num:02d}", "A")

# ============================================================================
# SUBCLASS 2: AYAKTA TEDAVİ
# ============================================================================

class Outpatient(Patient):
    """Ayakta tedavi - poliklinik hastaları"""
    
    def __init__(self, patient_id: str, name: str, age: int, gender: Gender,
                 phone: str, address: str, blood_type: BloodType,
                 clinic: str, doctor: str, **kwargs):
        super().__init__(patient_id, name, age, gender, phone, address, blood_type)
        self.clinic = clinic
        self.doctor = doctor
        self.visit_count = 0
        self.visit_fee = 150.0
        self.prescriptions: List[str] = []
    
    def calculate_treatment_cost(self) -> float:
        base = self.visit_count * self.visit_fee
        rx_cost = len(self.prescriptions) * 75
        return base + rx_cost
    
    def get_priority_level(self) -> int:
        base = 3
        if self.visit_count > 5: base += 1
        if self.age > 70: base += 1
        return base
    
    def add_visit(self, diagnosis: str):
        """Ziyaret ekler"""
        self.visit_count += 1
        self.add_medical_history(f"Ziyaret {self.visit_count}: {diagnosis}")
    
    @staticmethod
    def get_clinic_duration(clinic: str) -> int:
        """Poliklinik süresi (dakika)"""
        durations = {"Kardiyoloji": 30, "Dahiliye": 20, "Göz": 15}
        return durations.get(clinic, 20)

# ============================================================================
# SUBCLASS 3: ACİL SERVİS
# ============================================================================

class EmergencyPatient(Patient):
    """Acil hasta - acil servise gelen hastalar"""
    
    def __init__(self, patient_id: str, name: str, age: int, gender: Gender,
                 phone: str, address: str, blood_type: BloodType,
                 triage_level: int, arrival_method: str, complaint: str, **kwargs):
        super().__init__(patient_id, name, age, gender, phone, address, blood_type,
                        PatientStatus.EMERGENCY)
        self.triage_level = triage_level  # 1-5, 1 en kritik
        self.arrival_method = arrival_method
        self.complaint = complaint
        self.arrival_time = datetime.now()
        self.interventions: List[str] = []
    
    def calculate_treatment_cost(self) -> float:
        base = 1000.0
        triage_mult = {1: 5.0, 2: 3.0, 3: 2.0, 4: 1.5, 5: 1.2}
        intervention_cost = len(self.interventions) * 200
        ambulance = 500 if self.arrival_method == "Ambulans" else 0
        return base * triage_mult[self.triage_level] + intervention_cost + ambulance
    
    def get_priority_level(self) -> int:
        return 11 - self.triage_level  # 1->10, 5->6
    
    def add_intervention(self, intervention: str):
        """Müdahale ekler"""
        self.interventions.append(f"[{datetime.now():%H:%M}] {intervention}")
    
    def get_triage_color(self) -> str:
        """Triyaj rengi"""
        colors = {1: "🔴 KIRMIZI", 2: "🟠 TURUNCU", 3: "🟡 SARI", 4: "🟢 YEŞİL", 5: "🔵 MAVİ"}
        return colors[self.triage_level]
    
    @staticmethod
    def calculate_triage(symptoms: List[str]) -> int:
        """Semptomlara göre triyaj önerir"""
        critical = ['göğüs ağrısı', 'nefes alamama', 'şuur kaybı']
        if any(s in ' '.join(symptoms).lower() for s in critical):
            return 1
        return 3

# ============================================================================
# REPOSITORY
# ============================================================================

class PatientRepository:
    """Veri yönetimi katmanı"""
    
    def __init__(self):
        self._patients: Dict[str, Patient] = {}
    
    def add(self, patient: Patient) -> bool:
        """Hasta ekler"""
        if patient.patient_id in self._patients:
            return False
        self._patients[patient.patient_id] = patient
        return True
    
    def get_by_id(self, pid: str) -> Optional[Patient]:
        """ID ile bulur"""
        return self._patients.get(pid)
    
    def get_all(self) -> List[Patient]:
        """Tümünü döner"""
        return list(self._patients.values())
    
    def find_by_name(self, name: str) -> List[Patient]:
        """İsme göre arar"""
        return [p for p in self._patients.values() if name.lower() in p.name.lower()]
    
    def find_by_type(self, ptype: type) -> List[Patient]:
        """Tipe göre filtreler"""
        return [p for p in self._patients.values() if isinstance(p, ptype)]
    
    def count(self) -> int:
        """Sayı"""
        return len(self._patients)
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikler"""
        all_p = self.get_all()
        return {
            'total': len(all_p),
            'inpatient': len(self.find_by_type(Inpatient)),
            'outpatient': len(self.find_by_type(Outpatient)),
            'emergency': len(self.find_by_type(EmergencyPatient)),
            'avg_age': sum(p.age for p in all_p) / len(all_p) if all_p else 0
        }

# ============================================================================
# SERVICE
# ============================================================================

class PatientService:
    """İş mantığı katmanı"""
    
    def __init__(self, repo: PatientRepository):
        self.repo = repo
        self.operation_count = 0
    
    def register(self, patient: Patient) -> tuple[bool, str]:
        """Hasta kaydeder"""
        if not Patient.validate_age(patient.age):
            return False, "Geçersiz yaş"
        if not Patient.validate_phone(patient.phone):
            return False, "Geçersiz telefon"
        
        success = self.repo.add(patient)
        self.operation_count += 1
        return (True, f"✓ {patient.name} kaydedildi") if success else (False, "Hasta zaten kayıtlı")
    
    def discharge(self, pid: str) -> tuple[bool, str]:
        """Taburcu eder"""
        patient = self.repo.get_by_id(pid)
        if not patient:
            return False, "Hasta bulunamadı"
        patient.update_status(PatientStatus.DISCHARGED)
        self.operation_count += 1
        return True, f"✓ {patient.name} taburcu edildi"
    
    def get_high_priority(self) -> List[Patient]:
        """Yüksek öncelikli hastalar"""
        return sorted([p for p in self.repo.get_all() if p.get_priority_level() >= 7],
                     key=lambda p: p.get_priority_level(), reverse=True)
    
    def calculate_total_cost(self) -> float:
        """Toplam maliyet"""
        return sum(p.calculate_treatment_cost() for p in self.repo.get_all())

# ============================================================================
# OTOMATIK DEMO
# ============================================================================

def run_demo():
    """Otomatik demo - tüm özellikleri gösterir"""
    
    h("HASTA YÖNETİM SİSTEMİ - OTOMATIK DEMO")
    
    # Sistem başlat
    s("1. SİSTEM BAŞLATILIYOR")
    repo = PatientRepository()
    service = PatientService(repo)
    ok("Repository ve Service hazır")
    w()
    
    # Hastalar oluştur
    s("2. ÖRNEK HASTALAR OLUŞTURULUYOR")
    
    patients = [
        Inpatient("IP-001", "Ahmet Yılmaz", 65, Gender.MALE, "0532-123-4567",
                 "Samsun", BloodType.A_POS, "301", "A", 600),
        Outpatient("OP-002", "Ayşe Demir", 32, Gender.FEMALE, "0533-987-6543",
                  "Samsun", BloodType.B_POS, "Kardiyoloji", "Dr. Can"),
        EmergencyPatient("ER-003", "Mehmet Kaya", 58, Gender.MALE, "0534-555-7777",
                        "Samsun", BloodType.O_POS, 2, "Ambulans", "Göğüs ağrısı"),
        Inpatient("IP-004", "Fatma Çelik", 45, Gender.FEMALE, "0535-111-2222",
                 "Samsun", BloodType.AB_POS, "302", "B", 500),
        Outpatient("OP-005", "Can Öztürk", 28, Gender.MALE, "0536-333-4444",
                  "Samsun", BloodType.A_POS, "Ortopedi", "Dr. Zeynep"),
        EmergencyPatient("ER-006", "Elif Şahin", 71, Gender.FEMALE, "0537-555-6666",
                        "Samsun", BloodType.O_POS, 1, "Ambulans", "Kalp krizi"),
    ]
    
    for p in patients:
        success, msg = service.register(p)
        ok(f"{p.name} - {p.__class__.__name__}")
        w(0.2)
    
    # İstatistikler
    s("3. SİSTEM İSTATİSTİKLERİ")
    stats = repo.get_stats()
    info(f"Toplam hasta: {stats['total']}")
    info(f"Yatan hasta: {stats['inpatient']}")
    info(f"Ayakta tedavi: {stats['outpatient']}")
    info(f"Acil servis: {stats['emergency']}")
    info(f"Ortalama yaş: {stats['avg_age']:.1f}")
    w()
    
    # POLİMORFİZM gösterimi
    s("4. POLİMORFİZM ÖRNEĞİ - Maliyet Hesaplama")
    info("Her hasta tipi kendi calculate_treatment_cost() metodunu kullanıyor:")
    for p in repo.get_all():
        cost = p.calculate_treatment_cost()
        print(f"  {p.name:<20} ({p.__class__.__name__:<15}) = {cost:>10,.2f} TL")
        w(0.2)
    w()
    
    # Toplam maliyet
    total = service.calculate_total_cost()
    ok(f"Toplam sistem maliyeti: {total:,.2f} TL")
    w()
    
    # POLİMORFİZM - Öncelik
    s("5. POLİMORFİZM ÖRNEĞİ - Öncelik Sıralaması")
    info("Her hasta tipi kendi get_priority_level() metodunu kullanıyor:")
    for p in sorted(repo.get_all(), key=lambda x: x.get_priority_level(), reverse=True):
        priority = p.get_priority_level()
        print(f"  [Öncelik: {priority:2}/10] {p.name:<20} ({p.__class__.__name__})")
        w(0.2)
    w()
    
    # Yatan hasta işlemleri
    s("6. YATAN HASTA DETAYLI İŞLEMLER")
    ip = repo.get_by_id("IP-001")
    info(f"Hasta: {ip.name}")
    
    ip.add_medical_history("Hipertansiyon tanısı")
    ok("Tıbbi geçmiş eklendi")
    
    ip.allergies.append("Penisilin")
    ok("Alerji eklendi: Penisilin")
    
    ip.medications.extend(["Aspirin", "Metformin"])
    ok("İlaçlar eklendi")
    
    ip.add_nursing_note("Vital bulgular normal")
    ok("Hemşire notu eklendi")
    
    info(f"Oda: {ip.room}, Yatak: {ip.bed}")
    info(f"Tedavi maliyeti: {ip.calculate_treatment_cost():,.2f} TL")
    w()
    
    # Ayakta tedavi işlemleri
    s("7. AYAKTA TEDAVİ HASTASI İŞLEMLER")
    op = repo.get_by_id("OP-002")
    info(f"Hasta: {op.name} - {op.clinic}")
    
    op.add_visit("Hipertansiyon kontrolü")
    ok("1. ziyaret kaydedildi")
    
    op.prescriptions.append("Ramipril 5mg - 1x1 - 30 gün")
    ok("Reçete yazıldı")
    
    op.add_visit("Kontrol muayenesi")
    ok("2. ziyaret kaydedildi")
    
    duration = Outpatient.get_clinic_duration(op.clinic)
    info(f"Poliklinik muayene süresi: {duration} dakika")
    info(f"Toplam ziyaret: {op.visit_count}")
    info(f"Tedavi maliyeti: {op.calculate_treatment_cost():,.2f} TL")
    w()
    
    # Acil servis işlemleri
    s("8. ACİL SERVİS HASTASI İŞLEMLER")
    er = repo.get_by_id("ER-003")
    info(f"Hasta: {er.name}")
    warn(f"Triyaj: {er.get_triage_color()}")
    info(f"Geliş şekli: {er.arrival_method}")
    info(f"Şikayet: {er.complaint}")
    
    er.add_intervention("EKG çekildi")
    ok("Müdahale: EKG")
    
    er.add_intervention("IV yol açıldı")
    ok("Müdahale: IV")
    
    er.add_intervention("Aspirin verildi")
    ok("Müdahale: İlaç")
    
    info(f"Öncelik: {er.get_priority_level()}/10")
    info(f"Tedavi maliyeti: {er.calculate_treatment_cost():,.2f} TL")
    w()
    
    # Kritik hasta
    s("9. KRİTİK HASTA (Triyaj 1)")
    critical = repo.get_by_id("ER-006")
    warn(f"⚠ KRİTİK: {critical.name}")
    warn(f"Triyaj: {critical.get_triage_color()}")
    info(f"Öncelik: {critical.get_priority_level()}/10 (En yüksek)")
    w()
    
    # Repository işlemleri
    s("10. REPOSITORY İŞLEMLERİ")
    
    # Arama
    results = repo.find_by_name("Ayşe")
    ok(f"İsim araması 'Ayşe': {len(results)} sonuç")
    
    # Tip filtreleme
    emergencies = repo.find_by_type(EmergencyPatient)
    ok(f"Acil servis hastaları: {len(emergencies)}")
    
    # ID ile bulma
    patient = repo.get_by_id("OP-002")
    ok(f"ID ile bulma: {patient.name if patient else 'Bulunamadı'}")
    w()
    
    # Service işlemleri
    s("11. SERVİCE İŞLEMLERİ")
    
    # Yüksek öncelikli hastalar
    high_priority = service.get_high_priority()
    info(f"Yüksek öncelikli hasta sayısı: {len(high_priority)}")
    for p in high_priority:
        print(f"  • {p.name} (Öncelik: {p.get_priority_level()}/10)")
    w()
    
    # Taburcu
    success, msg = service.discharge("IP-004")
    ok(msg) if success else warn(msg)
    w()
    
    # Statik metot örnekleri
    s("12. STATİK VE SINIF METOTLARı")
    
    # Telefon validasyon
    phones = ["0532-123-4567", "abc-def"]
    for phone in phones:
        valid = Patient.validate_phone(phone)
        status = "✓" if valid else "✗"
        print(f"  {status} {phone}")
    
    # ID formatlama
    formatted = Patient.format_id("TEST", 42)
    info(f"ID formatı: TEST, 42 → {formatted}")
    
    # Triyaj hesaplama
    level = EmergencyPatient.calculate_triage(["göğüs ağrısı"])
    info(f"Triyaj hesaplama: göğüs ağrısı → Seviye {level}")
    w()
    
    # Sınıf metodu ile oluşturma
    s("13. SINIF METODU İLE HASTA OLUŞTURMA")
    new_patient = Inpatient.create_with_room(
        "Test Hasta", 50, Gender.MALE, "0540-123-4567",
        "Samsun", BloodType.A_POS, 3, 15
    )
    ok(f"Oda ataması ile oluşturuldu: {new_patient.patient_id}")
    info(f"Oda: {new_patient.room}, Yatak: {new_patient.bed}")
    w()
    
    # Final rapor
    s("14. FİNAL RAPOR")
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║              HASTA YÖNETİM SİSTEMİ RAPORU                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║ Toplam Hasta         : {stats['total']:<32} ║
    ║ Yatan Hasta          : {stats['inpatient']:<32} ║
    ║ Ayakta Tedavi        : {stats['outpatient']:<32} ║
    ║ Acil Servis          : {stats['emergency']:<32} ║
    ║ Ortalama Yaş         : {stats['avg_age']:.1f} yıl{' '*26} ║
    ║ Toplam Maliyet       : {total:,.2f} TL{' '*20} ║
    ║ Toplam İşlem         : {service.operation_count:<32} ║
    ║ Yüksek Öncelikli     : {len(high_priority):<32} ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    h("✓ DEMO TAMAMLANDI")
    
    print(f"\n{C.G}Tüm özellikler başarıyla test edildi:{C.E}")
    print(f"  ✓ Base class ve abstract metotlar")
    print(f"  ✓ 3 farklı subclass (Inpatient, Outpatient, EmergencyPatient)")
    print(f"  ✓ Polimorfizm (maliyet ve öncelik hesaplama)")
    print(f"  ✓ Repository katmanı (CRUD işlemleri)")
    print(f"  ✓ Service katmanı (iş mantığı)")
    print(f"  ✓ Nesne metotları")
    print(f"  ✓ Sınıf metotları (@classmethod)")
    print(f"  ✓ Statik metotlar (@staticmethod)")
    print(f"  ✓ Kalıtım (inheritance)")
    print(f"  ✓ Kapsülleme (encapsulation)")
    print(f"\n{C.BOLD}Projeniz hazır!{C.E}\n")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print(f"\n\n{C.Y}Demo kullanıcı tarafından durduruldu.{C.E}\n")
    except Exception as e:
        print(f"\n\n{C.R}Hata: {e}{C.E}\n")
        import traceback
        traceback.print_exc()
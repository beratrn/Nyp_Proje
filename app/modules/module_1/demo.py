"""
Hasta Yönetim Modülü - Demo Senaryosu
Bu dosya modülün tüm özelliklerini göste bir demo içerir.
"""

from datetime import datetime, timedelta
from base import PatientStatus, Gender, BloodType
from implementations import (
    Inpatient, Outpatient, EmergencyPatient,
    VitalSigns, BedAssignment, Insurance, EmergencyCase,
    PatientRegistrationService, PatientManagementService
)
from repository import InMemoryPatientRepository


def print_section(title: str) -> None:
    """Bölüm başlığı yazdırır"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_patient_creation():
    """
    Farklı hasta tiplerinin oluşturulmasını gösterir.
    POLİMORFİZM ÖRNEĞİ: Aynı liste içinde farklı hasta tiplerini tutma.
    """
    print_section("DEMO 1: Hasta Oluşturma ve Polimorfizm")
    
    # Yatan hasta oluşturma
    print("\n1. Yatan Hasta (Inpatient) Oluşturuluyor...")
    bed = BedAssignment(
        bed_number="B-205",
        room_number="205",
        ward="Cardiology",
        assignment_date=datetime.now(),
        is_icu=False
    )
    
    inpatient = Inpatient(
        patient_id="P-10001",
        name="Ahmet Yılmaz",
        age=55,
        gender=Gender.MALE,
        diagnosis="Coronary Artery Disease",
        bed_assignment=bed,
        blood_type=BloodType.A_POSITIVE,
        phone="+905551234567"
    )
    
    inpatient.add_allergy("Penicillin")
    inpatient.add_medication("Aspirin 100mg")
    
    print(f"✓ Oluşturuldu: {inpatient}")
    print(f"  - Yatak: {bed.get_location()}")
    print(f"  - Maliyet: {inpatient.calculate_treatment_cost():.2f} TL")
    print(f"  - Öncelik: {inpatient.get_priority_level()}/10")
    
    # Ayakta tedavi hastası oluşturma
    print("\n2. Ayakta Tedavi Hastası (Outpatient) Oluşturuluyor...")
    outpatient = Outpatient(
        patient_id="P-10002",
        name="Fatma Demir",
        age=32,
        gender=Gender.FEMALE,
        reason_for_visit="Routine checkup and blood test",
        blood_type=BloodType.O_POSITIVE,
        phone="+905559876543"
    )
    
    outpatient.add_prescription("Vitamin D3 1000IU - Daily")
    outpatient.schedule_follow_up(datetime.now() + timedelta(days=30))
    
    print(f"✓ Oluşturuldu: {outpatient}")
    print(f"  - Ziyaret Nedeni: {outpatient.reason_for_visit}")
    print(f"  - Maliyet: {outpatient.calculate_treatment_cost():.2f} TL")
    print(f"  - Öncelik: {outpatient.get_priority_level()}/10")
    
    # Acil hasta oluşturma
    print("\n3. Acil Hasta (EmergencyPatient) Oluşturuluyor...")
    emergency_case = EmergencyCase(
        case_id="EM-2024-001",
        arrival_time=datetime.now() - timedelta(minutes=15),
        triage_level=2,
        chief_complaint="Severe chest pain and shortness of breath",
        ambulance_arrival=True
    )
    
    emergency_patient = EmergencyPatient(
        patient_id="P-10003",
        name="Mehmet Kaya",
        age=68,
        gender=Gender.MALE,
        emergency_case=emergency_case,
        blood_type=BloodType.B_POSITIVE
    )
    
    emergency_patient.add_critical_intervention("ECG performed - ST elevation detected")
    emergency_patient.add_critical_intervention("Oxygen therapy initiated")
    emergency_patient.notify_emergency_contacts()
    
    print(f"✓ Oluşturuldu: {emergency_patient}")
    print(f"  - Triyaj Seviyesi: {emergency_case.triage_level}")
    print(f"  - Bekleme Süresi: {emergency_patient.get_waiting_time()} dakika")
    print(f"  - Maliyet: {emergency_patient.calculate_treatment_cost():.2f} TL")
    print(f"  - Öncelik: {emergency_patient.get_priority_level()}/10")
    print(f"  - Kritik Vaka: {'Evet' if emergency_patient.is_critical_case() else 'Hayır'}")
    
    # POLİMORFİZM DEMONSTRASYONU
    print("\n" + "-"*70)
    print("POLİMORFİZM ÖRNEĞİ: Farklı hasta tipleri aynı listede")
    print("-"*70)
    
    patients_list = [inpatient, outpatient, emergency_patient]
    
    print("\nTüm Hastaların Ortak Özellikleri:")
    for i, patient in enumerate(patients_list, 1):
        print(f"\n{i}. Hasta: {patient.name} ({patient.__class__.__name__})")
        print(f"   - Tedavi Maliyeti: {patient.calculate_treatment_cost():.2f} TL")
        print(f"   - Öncelik Seviyesi: {patient.get_priority_level()}/10")
        print(f"   - Özel Bakım: {'Gerekli' if patient.requires_special_care() else 'Gerekli Değil'}")
        print(f"   - Durum: {patient.status.value}")
    
    return patients_list


def demo_repository_operations():
    """Repository işlemlerini gösterir"""
    print_section("DEMO 2: Repository İşlemleri")
    
    # Repository oluştur
    print("\n1. In-Memory Repository Oluşturuluyor...")
    repo = InMemoryPatientRepository()
    print(f"✓ Repository oluşturuldu")
    
    # Hasta kaydetme
    print("\n2. Hastalar Kaydediliyor...")
    
    patients = [
        Inpatient(
            "P-20001", "Ali Öztürk", 45, Gender.MALE,
            diagnosis="Appendicitis"
        ),
        Outpatient(
            "P-20002", "Ayşe Yıldız", 28, Gender.FEMALE,
            reason_for_visit="Annual checkup"
        ),
        EmergencyPatient(
            "P-20003", "Can Arslan", 35, Gender.MALE,
            emergency_case=EmergencyCase(
                "EM-002", datetime.now(), 3,
                "Broken leg from accident", True
            )
        )
    ]
    
    for patient in patients:
        success = repo.save(patient)
        print(f"  {'✓' if success else '✗'} {patient.name} kaydedildi")
    
    # Listeleme
    print("\n3. Tüm Hastalar Listeleniyor...")
    all_patients = repo.list_all()
    print(f"  Toplam hasta sayısı: {len(all_patients)}")
    for p in all_patients:
        print(f"  - {p.id}: {p.name} ({p.__class__.__name__})")
    
    # ID ile arama
    print("\n4. ID ile Hasta Arama...")
    found = repo.find_by_id("P-20001")
    if found:
        print(f"  ✓ Bulundu: {found.name} - {found.status.value}")
    
    # Filtreleme
    print("\n5. Duruma Göre Filtreleme...")
    active_patients = repo.filter_by_status(PatientStatus.IN_TREATMENT)
    print(f"  Tedavide olan hasta sayısı: {len(active_patients)}")
    
    # Tipe göre filtreleme
    print("\n6. Tipe Göre Filtreleme...")
    inpatients = repo.filter_by_type(Inpatient)
    print(f"  Yatan hasta sayısı: {len(inpatients)}")
    
    # İstatistikler
    print("\n7. Repository İstatistikleri...")
    stats = repo.get_statistics()
    print(f"  Toplam hasta: {stats['total_patients']}")
    print(f"  Yatan hasta: {stats['inpatients']}")
    print(f"  Ayakta tedavi: {stats['outpatients']}")
    print(f"  Acil hasta: {stats['emergency_patients']}")
    print(f"  Ortalama yaş: {stats['average_age']}")
    
    return repo


def demo_service_layer(repo):
    """Servis katmanı işlemlerini gösterir"""
    print_section("DEMO 3: Servis Katmanı İşlemleri")
    
    # Servis oluşturma
    print("\n1. Servisler Oluşturuluyor...")
    registration_service = PatientRegistrationService(repo)
    management_service = PatientManagementService(repo)
    print("  ✓ PatientRegistrationService")
    print("  ✓ PatientManagementService")
    
    # Yeni hasta kaydı
    print("\n2. Yeni Hasta Kaydediliyor...")
    new_patient = Outpatient(
        "P-30001",
        "Zeynep Şahin",
        22,
        Gender.FEMALE,
        reason_for_visit="Flu symptoms"
    )
    
    success = registration_service.register_patient(new_patient)
    print(f"  {'✓' if success else '✗'} Hasta kaydı: {new_patient.name}")
    
    # Hasta durumu güncelleme
    print("\n3. Hasta Durumu Güncelleniyor...")
    success = management_service.update_patient_status(
        "P-20001",
        PatientStatus.RECOVERED,
        "Post-surgery recovery complete"
    )
    print(f"  {'✓' if success else '✗'} Durum güncellendi")
    
    # İsme göre arama
    print("\n4. İsme Göre Hasta Arama...")
    results = management_service.search_patients_by_name("Ayşe")
    print(f"  Bulunan hasta sayısı: {len(results)}")
    for p in results:
        print(f"  - {p.name}")
    
    # Kritik hasta listesi
    print("\n5. Kritik Hastalar...")
    critical = management_service.get_critical_patients()
    print(f"  Kritik hasta sayısı: {len(critical)}")
    
    # Hasta taburcu etme
    print("\n6. Hasta Taburcu Ediliyor...")
    success = management_service.discharge_patient(
        "P-20002",
        "Healthy, no follow-up required"
    )
    print(f"  {'✓' if success else '✗'} Taburcu işlemi tamamlandı")
    
    # Kayıt istatistikleri
    print("\n7. Kayıt İstatistikleri...")
    reg_stats = registration_service.get_registration_statistics()
    print(f"  Toplam kayıt: {reg_stats['total_registrations']}")
    print("  Tipe göre dağılım:", reg_stats['by_type'])
    
    return registration_service, management_service


def demo_advanced_features():
    """Gelişmiş özellikleri gösterir"""
    print_section("DEMO 4: Gelişmiş Özellikler")
    
    # CLASS METHOD kullanımı
    print("\n1. CLASS METHOD Örneği: ICU Hastası Oluşturma...")
    icu_patient = Inpatient.create_icu_patient(
        "P-40001",
        "Hasan Çelik",
        72,
        Gender.MALE,
        diagnosis="Severe Pneumonia"
    )
    print(f"  ✓ ICU hastası oluşturuldu: {icu_patient.name}")
    print(f"  - Yatak: {icu_patient.bed_assignment.get_location()}")
    print(f"  - Maliyet: {icu_patient.calculate_treatment_cost():.2f} TL")
    
    # STATIC METHOD kullanımı
    print("\n2. STATIC METHOD Örneği: ID Validasyonu...")
    test_ids = ["P-12345", "INVALID", "P-ABC123", "123"]
    for test_id in test_ids:
        is_valid = Inpatient.validate_patient_id(test_id)
        print(f"  {test_id}: {'✓ Geçerli' if is_valid else '✗ Geçersiz'}")
    
    # Vital signs ekleme
    print("\n3. Hayati Bulgular Kaydediliyor...")
    vitals = VitalSigns(
        timestamp=datetime.now(),
        temperature=38.5,
        blood_pressure_systolic=140,
        blood_pressure_diastolic=90,
        heart_rate=95,
        respiratory_rate=20,
        oxygen_saturation=96.0
    )
    icu_patient.add_vital_signs(vitals)
    print(f"  ✓ {vitals}")
    print(f"  - Kritik: {'Evet' if vitals.is_critical() else 'Hayır'}")
    
    # Sigorta hesaplaması
    print("\n4. Sigorta Kapsamı Hesaplama...")
    insurance = Insurance(
        provider="Acme Health Insurance",
        policy_number="INS-2024-5678",
        coverage_percentage=80.0,
        expiry_date=datetime.now() + timedelta(days=365)
    )
    
    total_cost = icu_patient.calculate_treatment_cost()
    coverage = insurance.calculate_coverage(total_cost)
    patient_pays = total_cost - coverage
    
    print(f"  Toplam Maliyet: {total_cost:.2f} TL")
    print(f"  Sigorta Karşılama: {coverage:.2f} TL (%{insurance.coverage_percentage})")
    print(f"  Hasta Ödemesi: {patient_pays:.2f} TL")
    
    # Hasta raporu
    print("\n5. Detaylı Hasta Raporu Oluşturuluyor...")
    report = PatientManagementService.generate_patient_report(icu_patient)
    print(report)
    
    return icu_patient


def demo_emergency_scenarios():
    """Acil durum senaryolarını gösterir"""
    print_section("DEMO 5: Acil Durum Senaryoları")
    
    # Travma hastası
    print("\n1. Travma Hastası (CLASS METHOD)...")
    trauma = EmergencyPatient.create_trauma_patient(
        "P-50001",
        "Emre Aydın",
        25,
        Gender.MALE,
        "Multiple injuries from car accident"
    )
    print(f"  ✓ Travma hastası oluşturuldu: {trauma.name}")
    print(f"  - Triyaj: {trauma.emergency_case.triage_level}")
    print(f"  - Öncelik: {trauma.get_priority_level()}/10")
    
    # Müdahaleler
    print("\n2. Acil Müdahaleler Kaydediliyor...")
    interventions = [
        "X-ray performed - multiple fractures detected",
        "IV fluids administered",
        "Pain management initiated",
        "Surgery consultation requested"
    ]
    
    for intervention in interventions:
        trauma.add_critical_intervention(intervention)
        print(f"  ✓ {intervention}")
    
    # Stabilizasyon
    print("\n3. Hasta Stabilize Ediliyor...")
    trauma.stabilize_patient()
    print(f"  ✓ Hasta stabilize edildi")
    print(f"  - Yeni öncelik: {trauma.get_priority_level()}/10")
    
    # Servise transfer
    print("\n4. Hastane Servise Transfer...")
    trauma.transfer_to_ward("Orthopedics")
    print(f"  ✓ Transfer tamamlandı")
    print(f"  - Durum: {trauma.status.value}")
    
    # Triyaj seviyesi belirleme (STATIC METHOD)
    print("\n5. STATIC METHOD: Triyaj Seviyesi Belirleme...")
    test_symptoms = [
        ["chest pain", "difficulty breathing"],
        ["fever", "cough"],
        ["minor cut", "headache"]
    ]
    
    for symptoms in test_symptoms:
        level = EmergencyPatient.determine_triage_level(symptoms)
        print(f"  Semptomlar: {', '.join(symptoms)}")
        print(f"  → Triyaj Seviyesi: {level}")
    
    return trauma


def run_complete_demo():
    """Tüm demo senaryolarını çalıştırır"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "HASTA YÖNETİM SİSTEMİ DEMO" + " "*27 + "║")
    print("║" + " "*20 + "Modül 1: Patient Management" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    # Demo 1: Hasta Oluşturma
    patients = demo_patient_creation()
    
    # Demo 2: Repository
    repo = demo_repository_operations()
    
    # Demo 3: Servis Katmanı
    reg_service, mgmt_service = demo_service_layer(repo)
    
    # Demo 4: Gelişmiş Özellikler
    icu_patient = demo_advanced_features()
    
    # Demo 5: Acil Durumlar
    trauma_patient = demo_emergency_scenarios()
    
    # Final özet
    print_section("DEMO TAMAMLANDI - ÖZET")
    print(f"""
    ✓ {len(patients)} farklı hasta tipi oluşturuldu
    ✓ Repository işlemleri başarıyla gerçekleştirildi
    ✓ Servis katmanı fonksiyonları test edildi
    ✓ Polimorfizm örnekleri gösterildi
    ✓ Class method, static method ve nesne metodları kullanıldı
    ✓ Soyut sınıf ve kalıtım yapısı çalıştırıldı
    
    Toplam Hasta Sayısı: {repo.count()}
    Repository İstatistikleri:
    {repo.get_statistics()}
    """)
    
    print("\n" + "="*70)
    print("  DEMO BAŞARIYLA TAMAMLANDI!")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_complete_demo()
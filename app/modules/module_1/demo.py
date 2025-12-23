"""
Hasta Yönetim Modülü - Demo ve Senaryo Gösterimi
"""
from datetime import datetime, timedelta
from app.modules.module_1.implementations import (
    Inpatient, 
    Outpatient, 
    EmergencyPatient,
    PatientService,
    MedicalRecord,
    VitalSigns,
    Medication
)
from app.modules.module_1.repository import PatientRepository, FileBasedPatientRepository, CachedPatientRepository
from app.modules.module_1.base import Patient


def print_separator(title: str = "") -> None:
    """
    Görsel ayırıcı yazdırır
    """
    print("\n" + "=" * 80)
    if title:
        print(f" {title} ".center(80, "="))
        print("=" * 80)


def demonstrate_polymorphism() -> None:
    """
    Polimorfizm örneğini gösterir
    """
    print_separator("POLİMORFİZM GÖSTERİMİ")
    
    patients: list[Patient] = [
        Inpatient("Ahmet Yılmaz", 55, "male", "201", "Cardiology", "Myocardial infarction"),
        Outpatient("Ayşe Demir", 34, "female", "Annual checkup"),
        EmergencyPatient("Mehmet Kaya", 28, "male", "Traffic accident", 2),
        Inpatient("Fatma Şahin", 68, "female", "305", "Neurology", "Stroke"),
        EmergencyPatient("Ali Çelik", 42, "male", "Severe chest pain", 1)
    ]
    
    print("\nTüm hastaların tedavi öncelikleri:")
    for patient in patients:
        priority = patient.calculate_treatment_priority()
        admission_type = patient.get_admission_type()
        daily_cost = patient.calculate_daily_cost()
        
        print(f"\n{admission_type} - {patient.name}")
        print(f"  Yaş: {patient.age}, Cinsiyet: {patient.gender}")
        print(f"  Tedavi Önceliği: {priority}/10")
        print(f"  Günlük Maliyet: ${daily_cost:.2f}")
        print(f"  Durum: {patient.status}")
    
    print("\n\nÖnceliğe göre sıralı liste:")
    sorted_patients = sorted(patients, key=lambda p: p.calculate_treatment_priority(), reverse=True)
    for idx, patient in enumerate(sorted_patients, 1):
        print(f"{idx}. {patient.name} ({patient.get_admission_type()}) - Öncelik: {patient.calculate_treatment_priority()}")


def demonstrate_inpatient_operations() -> None:
    """
    Yatan hasta işlemlerini gösterir
    """
    print_separator("YATAN HASTA İŞLEMLERİ")
    
    inpatient = Inpatient(
        name="Hasan Öztürk",
        age=62,
        gender="male",
        room_number="404",
        ward="Intensive Care Unit",
        admission_reason="Post-operative monitoring"
    )
    
    print(f"\nYeni yatan hasta kaydedildi: {inpatient.name}")
    print(f"Hasta ID: {Patient.format_patient_id(inpatient.id)}")
    print(f"Oda: {inpatient.room_number}, Servis: {inpatient.ward}")
    
    inpatient.set_blood_type("A+")
    inpatient.add_allergy("Penicillin")
    inpatient.add_allergy("Latex")
    inpatient.set_emergency_contact("Zeynep Öztürk", "+90 555 123 4567", "Spouse")
    
    print("\nKişisel bilgiler güncellendi:")
    print(f"  Kan Grubu: {inpatient.blood_type}")
    print(f"  Alerjiler: {', '.join(inpatient.allergies)}")
    
    inpatient.set_bed_type("private")
    inpatient.set_estimated_stay(7)
    
    print(f"\nYatak tipi: {inpatient.bed_type}")
    print(f"Tahmini kalış süresi: {inpatient.estimated_stay_days} gün")
    
    inpatient.add_medication("Aspirin", "100mg", "Once daily", 5.50)
    inpatient.add_medication("Metoprolol", "50mg", "Twice daily", 12.30)
    inpatient.add_medication("Atorvastatin", "20mg", "Once daily at bedtime", 18.75)
    
    print("\nEklenen ilaçlar:")
    for med in inpatient.medications:
        print(f"  - {med['name']} {med['dosage']} ({med['frequency']}) - ${med['daily_cost']}")
    
    inpatient.record_vital_signs(37.2, "120/80", 72, 98)
    inpatient.record_vital_signs(37.5, "125/82", 76, 97)
    inpatient.record_vital_signs(38.1, "130/85", 82, 96)
    
    print(f"\nVital signs kayıt sayısı: {len(inpatient.vital_signs_history)}")
    print("Son vital signs:")
    last_vitals = inpatient.vital_signs_history[-1]
    print(f"  Sıcaklık: {last_vitals['temperature']}°C")
    print(f"  Tansiyon: {last_vitals['blood_pressure']}")
    print(f"  Nabız: {last_vitals['heart_rate']} bpm")
    print(f"  Oksijen: %{last_vitals['oxygen_saturation']}")
    
    inpatient.add_daily_note("Patient responded well to treatment", "Dr. Smith")
    inpatient.add_daily_note("Vital signs stable, continue monitoring", "Nurse Johnson")
    
    print(f"\nGünlük not sayısı: {len(inpatient.daily_notes)}")
    
    daily_cost = inpatient.calculate_daily_cost()
    total_stay_cost = daily_cost * inpatient.get_length_of_stay()
    
    print(f"\nMaliyet Analizi:")
    print(f"  Günlük maliyet: ${daily_cost:.2f}")
    print(f"  Kalış süresi: {inpatient.get_length_of_stay()} gün")
    print(f"  Toplam maliyet: ${total_stay_cost:.2f}")
    
    summary = inpatient.get_inpatient_summary()
    print(f"\nHasta Özeti:")
    print(f"  Tedavi Önceliği: {summary['treatment_priority']}/10")
    print(f"  Yaş Kategorisi: {summary['age_category']}")
    print(f"  İlaç Sayısı: {summary['medications_count']}")

sample_repo : CachedPatientRepository = CachedPatientRepository(
        cache_size=100
    )
def demonstrate_outpatient_operations() -> None:
    """
    Ayaktan hasta işlemlerini gösterir
    """
    
    print_separator("AYAKTAN HASTA İŞLEMLERİ")
    
    repository: PatientRepository = FileBasedPatientRepository("patients.json")
    
    outpatient = Outpatient(
        name="Elif Yıldız",
        age=29,
        gender="female",
        visit_reason="Persistent headache and dizziness"
    )
    
    print(f"\nYeni ayaktan hasta: {outpatient.name}")
    print(f"Ziyaret nedeni: {outpatient.visit_reason}")
    
    outpatient.department = "Neurology"
    outpatient.assigned_doctor = "Dr. Ayşe Kara"
    
    print(f"Bölüm: {outpatient.department}")
    print(f"Doktor: {outpatient.assigned_doctor}")
    
    outpatient.add_visit_record(
        diagnosis="Tension headache",
        treatment="Pain medication and stress management",
        doctor="Dr. Ayşe Kara"
    )
    
    print("\nTanı ve tedavi kaydedildi")
    
    outpatient.add_prescription("Ibuprofen", "400mg", 10, 25.00)
    outpatient.add_prescription("Paracetamol", "500mg", 10, 15.00)
    
    print("\nReçeteler:")
    for presc in outpatient.prescriptions:
        status = "Karşılandı" if presc['filled'] else "Beklemede"
        print(f"  - {presc['medication']} {presc['dosage']} ({presc['duration_days']} gün) - ${presc['cost']} [{status}]")
    
    outpatient.mark_prescription_filled(0)
    print("\nİlk reçete karşılandı olarak işaretlendi")
    
    unfilled = outpatient.get_unfilled_prescriptions()
    print(f"Karşılanmamış reçete sayısı: {len(unfilled)}")
    
    outpatient.schedule_follow_up(14, "Check if headaches persist")
    print(f"\nTakip randevusu planlandı")
    print(f"Randevu tarihi: {outpatient.next_appointment_date.strftime('%Y-%m-%d')}")
    
    referral_id = outpatient.create_referral("MRI Imaging", "Detailed brain scan required")
    print(f"\nSevk oluşturuldu")
    print(f"Sevk No: {referral_id}")
    print(f"Sevk edilen bölüm: {outpatient.referral_department}")
    
    outpatient.update_payment_status("paid")
    print(f"\nÖdeme durumu: {outpatient.payment_status}")
    
    total_cost = outpatient.calculate_daily_cost()
    print(f"Toplam maliyet: ${total_cost:.2f}")
    
    summary = outpatient.get_outpatient_summary()
    print(f"\nHasta Özeti:")
    print(f"  Ziyaret sayısı: {summary['visit_count']}")
    print(f"  Takip gerekli: {'Evet' if summary['follow_up_required'] else 'Hayır'}")
    print(f"  Sevk gerekli: {'Evet' if summary['referral_needed'] else 'Hayır'}")


def demonstrate_emergency_operations() -> None:
    """
    Acil hasta işlemlerini gösterir
    """
    print_separator("ACİL HASTA İŞLEMLERİ")
    
    emergency_patient = EmergencyPatient(
        name="Can Aydın",
        age=35,
        gender="male",
        emergency_type="Severe chest pain",
        severity_level=1
    )
    
    print(f"\nACİL DURUM: {emergency_patient.name}")
    print(f"Acil tipi: {emergency_patient.emergency_type}")
    print(f"Şiddet seviyesi: {emergency_patient.severity_level}/5")
    print(f"Varış zamanı: {emergency_patient.arrival_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    emergency_patient.arrival_mode = "ambulance"
    print(f"Geliş şekli: {emergency_patient.arrival_mode}")
    
    emergency_patient.record_arrival_vitals(
        blood_pressure="180/110",
        heart_rate=125,
        respiratory_rate=24,
        glasgow_coma_scale=14
    )
    
    print("\nVarış vital signs:")
    vitals = emergency_patient.vital_signs_on_arrival
    print(f"  Tansiyon: {vitals['blood_pressure']}")
    print(f"  Nabız: {vitals['heart_rate']} bpm")
    print(f"  Solunum: {vitals['respiratory_rate']}/dk")
    print(f"  Glasgow Koma Skalası: {vitals['glasgow_coma_scale']}/15")
    
    if emergency_patient.trauma_team_activated:
        print("\n⚠️  TRAVMA EKİBİ AKTİVE EDİLDİ!")
    
    emergency_patient.perform_triage(1, "Critical - Suspected myocardial infarction")
    print("\nTriyaj tamamlandı")
    
    emergency_patient.add_injury("Chest discomfort", "Chest")
    emergency_patient.add_injury("Shortness of breath", "Respiratory")
    
    print(f"\nKayıtlı yaralanma/şikayet sayısı: {len(emergency_patient.injuries)}")
    
    emergency_patient.activate_trauma_team("Suspected cardiac emergency")
    
    emergency_patient.add_emergency_procedure(
        procedure_name="ECG",
        performed_by="Dr. Emergency Team",
        cost=150.00,
        success=True
    )
    
    emergency_patient.add_emergency_procedure(
        procedure_name="Cardiac enzyme test",
        performed_by="Lab Tech",
        cost=200.00,
        success=True
    )
    
    emergency_patient.add_emergency_procedure(
        procedure_name="IV Nitroglycerin",
        performed_by="Emergency Nurse",
        cost=75.00,
        success=True
    )
    
    print("\nUygulanan acil prosedürler:")
    for proc in emergency_patient.emergency_procedures:
        status = "✓" if proc['success'] else "✗"
        print(f"  {status} {proc['name']} - ${proc['cost']:.2f}")
    
    emergency_patient.treatment_start_time = datetime.now()
    time_to_treatment = emergency_patient.get_time_to_treatment()
    print(f"\nTedaviye kadar geçen süre: {time_to_treatment} dakika")
    
    emergency_patient.request_blood_transfusion(2, "O+")
    print("\nKan transfüzyonu talep edildi")
    
    emergency_patient.schedule_emergency_surgery("Cardiac catheterization", "Immediate")
    print("Acil ameliyat planlandı")
    
    emergency_patient.notify_emergency_contacts()
    print("Acil kontaklar bilgilendirildi")
    
    emergency_patient.stabilize_patient()
    print(f"\nHasta stabilize edildi - Yeni durum: {emergency_patient.status}")
    
    total_cost = emergency_patient.calculate_daily_cost()
    print(f"\nToplam acil maliyet: ${total_cost:.2f}")
    
    priority = emergency_patient.calculate_treatment_priority()
    print(f"Tedavi önceliği: {priority}/10")
    
    summary = emergency_patient.get_emergency_summary()
    print(f"\nAcil Hasta Özeti:")
    print(f"  Şiddet: {summary['severity_level']}/5")
    print(f"  Stabilize: {'Evet' if summary['stabilized'] else 'Hayır'}")
    print(f"  Travma ekibi: {'Aktif' if summary['trauma_team_activated'] else 'Pasif'}")
    print(f"  Prosedür sayısı: {summary['procedures_performed']}")


def demonstrate_repository_operations() -> None:
    """
    Repository işlemlerini gösterir
    """
    print_separator("REPOSITORY İŞLEMLERİ")
    
    repository = PatientRepository()
    
    print("\nYeni hastalar ekleniyor...")
    
    patient1 = Inpatient("Ahmet Yılmaz", 55, "male", "101", "Cardiology", "Heart disease")
    patient2 = Outpatient("Ayşe Demir", 34, "female", "Regular checkup")
    patient3 = EmergencyPatient("Mehmet Kaya", 28, "male", "Car accident", 2)
    patient4 = Inpatient("Fatma Şahin", 68, "female", "202", "Neurology", "Stroke")
    patient5 = Outpatient("Ali Çelik", 42, "male", "Diabetes consultation")
    
    repository.save(patient1)
    repository.save(patient2)
    repository.save(patient3)
    repository.save(patient4)
    repository.save(patient5)
    
    print(f"Toplam hasta sayısı: {repository.count()}")
    
    print("\nTipe göre hasta sayıları:")
    inpatients = repository.find_by_type("inpatient")
    outpatients = repository.find_by_type("outpatient")
    emergencies = repository.find_by_type("emergency")
    
    print(f"  Yatan hastalar: {len(inpatients)}")
    print(f"  Ayaktan hastalar: {len(outpatients)}")
    print(f"  Acil hastalar: {len(emergencies)}")
    
    print("\nID ile hasta bulma:")
    found_patient = repository.find_by_id(patient1.id)
    if found_patient:
        print(f"  Bulundu: {found_patient.name} ({found_patient.get_admission_type()})")
    
    print("\nİsme göre arama:")
    results = repository.find_by_name("Ayşe Demir")
    for patient in results:
        print(f"  {patient.name} - {patient.age} yaş - {patient.gender}")
    
    print("\nYaş aralığına göre filtreleme (30-60):")
    age_filtered = repository.find_by_age_range(30, 60)
    for patient in age_filtered:
        print(f"  {patient.name} - {patient.age} yaş")
    
    print("\nCinsiyete göre dağılım:")
    male_patients = repository.find_by_gender("male")
    female_patients = repository.find_by_gender("female")
    print(f"  Erkek: {len(male_patients)}")
    print(f"  Kadın: {len(female_patients)}")
    
    patient3.update_status("critical")
    repository.update(patient3)
    print("\nBir hastanın durumu 'critical' olarak güncellendi")
    
    critical_patients = repository.find_critical_patients()
    print(f"Kritik hasta sayısı: {len(critical_patients)}")
    for patient in critical_patients:
        print(f"  {patient.name} - {patient.get_admission_type()}")
    
    print("\nİstatistikler:")
    stats = sample_repo.get_statistics()
    print(f"Yatan hasta: {stats['by_type']['inpatient']}")
    print(f"Ayaktan hasta: {stats['by_type']['outpatient']}")
    print(f"Acil hasta: {stats['by_type']['emergency']}")


def demonstrate_advanced_features() -> None:
    """
    Gelişmiş özellikleri gösterir
    """
    print_separator("GELİŞMİŞ ÖZELLİKLER")
    
    print("\nCached Repository kullanımı:")
    cached_repo = CachedPatientRepository(cache_size=50)
    
    patient1 = Outpatient("Test Patient 1", 30, "male", "Checkup")
    patient2 = Outpatient("Test Patient 2", 40, "female", "Consultation")
    
    cached_repo.save(patient1)
    cached_repo.save(patient2)
    
    print("İlk erişim (cache miss):")
    result1 = cached_repo.find_by_id(patient1.id)
    print(f"  Bulunan: {result1.name}")
    
    print("İkinci erişim (cache hit):")
    result2 = cached_repo.find_by_id(patient1.id)
    print(f"  Bulunan: {result2.name}")
    
    cache_stats = cached_repo.get_cache_stats()
    print(f"\nCache İstatistikleri:")
    print(f"  Cache boyutu: {cache_stats['cache_size']}/{cache_stats['max_cache_size']}")
    print(f"  Hit sayısı: {cache_stats['hits']}")
    print(f"  Miss sayısı: {cache_stats['misses']}")
    print(f"  Hit oranı: %{cache_stats['hit_rate']}")
    
    print("\n\nToplu işlemler:")
    bulk_repo = PatientRepository()
    
    bulk_patients = [
        Outpatient(f"Patient {i}", 20 + i, "male" if i % 2 == 0 else "female", "Checkup")
        for i in range(10)
    ]
    
    result = bulk_repo.bulk_save(bulk_patients)
    print(f"Toplu kayıt sonucu:")
    print(f"  Başarılı: {result['success']}")
    print(f"  Başarısız: {result['failed']}")
    print(f"  Toplam: {result['total']}")
    
    for patient in bulk_patients[:3]:
        patient.update_status("discharged")
    
    update_result = bulk_repo.bulk_update(bulk_patients[:3])
    print(f"\nToplu güncelleme sonucu:")
    print(f"  Güncellenen: {update_result['success']}")
    
    print("\n\nData export/import:")
    export_data = bulk_repo.export_to_dict()
    print(f"Export edilen hasta sayısı: {len(export_data)}")
    print(f"İlk hastanın export verisi:")
    print(f"  İsim: {export_data[0]['name']}")
    print(f"  Tip: {export_data[0].get('type', 'N/A')}")
    
    print("\n\nÖzel filtreleme örnekleri:")
    
    elderly_female = bulk_repo.filter_by_criteria(
        lambda p: p.age > 25 and p.gender == "female"
    )
    print(f"25 yaş üstü kadın hasta sayısı: {len(elderly_female)}")
    
    discharged_patients = bulk_repo.filter_by_criteria(
        lambda p: p.status == "discharged"
    )
    print(f"Taburcu edilmiş hasta sayısı: {len(discharged_patients)}")


def main():
    """
    Ana demo fonksiyonu
    """
    print_separator("HASTA YÖNETİM MODÜLÜ DEMO")
    print("\nBu demo, hasta yönetim modülünün tüm özelliklerini gösterir.")
    print("Polimorfizm, soyut sınıflar, kalıtım ve servis katmanı kullanımı dahil.")
    
    try:
        demonstrate_polymorphism()
        demonstrate_inpatient_operations()
        demonstrate_outpatient_operations()
        demonstrate_emergency_operations()
        demonstrate_repository_operations()
        demonstrate_service_layer()
        demonstrate_data_classes()
        demonstrate_static_and_class_methods()
        demonstrate_advanced_features()
        
        print_separator("DEMO TAMAMLANDI")
        print("\nTüm özellikler başarıyla gösterildi!")
        print("Modül kullanıma hazır.")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()

repository: PatientRepository = FileBasedPatientRepository("patients.json")
sample_repo: CachedPatientRepository = CachedPatientRepository(
        repository=repository,
        cache_size=100
    )
if __name__ == "__main__":
    stats = repository.get_statistics()
    print(f"  Toplam hasta: {stats['total_patients']}")
    print(f"  Ortalama yaş: {stats['average_age']:.1f}")
    print(f"  Durum dağılımı: {stats['by_status']}")
    
    print("\nGenel arama ('Mehmet'):")
    search_results = repository.search("Mehmet")
    for patient in search_results:
        print(f"  {patient.name} - ID: {Patient.format_patient_id(patient.id)}")
    
    print("\nÖzel filtreleme (60 yaş üstü):")
    elderly = repository.filter_by_criteria(lambda p: p.age > 60)
    for patient in elderly:
        print(f"  {patient.name} - {patient.age} yaş")
    
    print("\nTransaction log (son 5):")
    logs = repository.get_transaction_log(5)
    for log in logs:
        print(f"  [{log['timestamp']}] {log['operation']}: {log['message']}")


def demonstrate_service_layer() -> None:
    """
    Servis katmanı işlemlerini gösterir
    """
    print_separator("SERVİS KATMANI İŞLEMLERİ")
    
    repository = PatientRepository()
    service = PatientService(repository)
    
    print("\nYeni hasta kaydı oluşturuluyor...")
    
    new_patient = Inpatient(
        name="Zeynep Arslan",
        age=45,
        gender="female",
        room_number="303",
        ward="Oncology",
        admission_reason="Cancer treatment"
    )
    
    patient_id = service.register_new_patient(new_patient)
    print(f"Hasta başarıyla kaydedildi")
    print(f"Hasta ID: {Patient.format_patient_id(patient_id)}")
    
    print("\nBildirim servisi mesajları:")
    notifications = service.notification_service.get_recent_notifications(1)
    for notif in notifications:
        print(f"  [{notif['type']}] {notif['message']}")
    
    summary = service.get_patient_summary(patient_id)
    print(f"\nHasta özeti alındı:")
    print(f"  İsim: {summary['name']}")
    print(f"  Yaş: {summary['age']}")
    print(f"  Kabul tipi: {summary['admission_type']}")
    print(f"  Tedavi önceliği: {summary['treatment_priority']}/10")
    
    print("\nDaha fazla hasta ekleniyor...")
    
    patients_data = [
        {"type": "inpatient", "name": "Hasan Öztürk", "age": 62, "gender": "male", 
         "room_number": "404", "ward": "ICU", "admission_reason": "Post-surgery"},
        {"type": "outpatient", "name": "Elif Yıldız", "age": 29, "gender": "female", 
         "visit_reason": "Headache"},
        {"type": "emergency", "name": "Can Aydın", "age": 35, "gender": "male", 
         "emergency_type": "Chest pain", "severity_level": 1}
    ]
    
    bulk_patients = PatientService.create_bulk_patients(patients_data)
    for patient in bulk_patients:
        service.register_new_patient(patient)
    
    print(f"Toplu kayıt tamamlandı: {len(bulk_patients)} hasta")
    
    print("\nHasta arama (isim: 'Elif'):")
    search_results = service.search_patients_by_name("Elif")
    for patient in search_results:
        print(f"  {patient.name} - {patient.get_admission_type()}")
    
    print("\nKritik hastaları getir:")
    service.update_patient_status(bulk_patients[-1].id, "critical")
    critical = service.get_critical_patients()
    print(f"Kritik hasta sayısı: {len(critical)}")
    
    print("\nTipe göre hasta sayıları:")
    inpatient_count = len(service.get_patients_by_type("inpatient"))
    outpatient_count = len(service.get_patients_by_type("outpatient"))
    emergency_count = len(service.get_patients_by_type("emergency"))
    
    print(f"  Yatan: {inpatient_count}")
    print(f"  Ayaktan: {outpatient_count}")
    print(f"  Acil: {emergency_count}")
    
    bed_occupancy = service.calculate_total_bed_occupancy()
    print(f"\nYatak doluluk oranı: {bed_occupancy} yatak")
    
    all_patients = repository.get_all()
    avg_age = PatientService.calculate_average_age(all_patients)
    gender_dist = PatientService.get_gender_distribution(all_patients)
    
    print(f"\nGenel istatistikler:")
    print(f"  Ortalama yaş: {avg_age:.1f}")
    print(f"  Cinsiyet dağılımı: {gender_dist}")
    
    if inpatient_count > 0:
        print("\nYatan hasta taburcu ediliyor...")
        inpatients = service.get_patients_by_type("inpatient")
        if inpatients:
            discharge_success = service.discharge_patient(
                inpatients[0].id,
                "Patient recovered fully, follow-up in 2 weeks"
            )
            if discharge_success:
                print("Taburcu işlemi başarılı")
                
                recent_notifs = service.notification_service.get_recent_notifications(1)
                if recent_notifs:
                    print(f"Bildirim: {recent_notifs[0]['message']}")


def demonstrate_data_classes() -> None:
    """
    Data class kullanımını gösterir
    """
    print_separator("DATA CLASS KULLANIMI")
    
    print("\nMedical Record oluşturma:")
    record = MedicalRecord(
        record_id="REC001",
        patient_id="PAT123",
        record_type="Diagnosis",
        description="Patient diagnosed with hypertension",
        recorded_by="Dr. Smith"
    )
    
    print(f"Kayıt ID: {record.record_id}")
    print(f"Tip: {record.record_type}")
    print(f"Açıklama: {record.description}")
    print(f"Kaydeden: {record.recorded_by}")
    
    record.add_attachment("/path/to/xray.jpg")
    record.add_attachment("/path/to/lab_results.pdf")
    print(f"Ek dosya sayısı: {len(record.attachments)}")
    
    print(f"\nKaydın yaşı: {record.get_record_age_days()} gün")
    
    print("\nVital Signs oluşturma:")
    vitals = VitalSigns(
        patient_id="PAT123",
        temperature=37.2,
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        heart_rate=72,
        respiratory_rate=16,
        oxygen_saturation=98
    )
    
    print(f"Sıcaklık: {vitals.temperature}°C")
    print(f"Tansiyon: {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}")
    print(f"Nabız: {vitals.heart_rate} bpm")
    print(f"Solunum: {vitals.respiratory_rate}/dk")
    print(f"Oksijen: %{vitals.oxygen_saturation}")
    
    print(f"\nNormal mi? {'Evet' if vitals.is_normal() else 'Hayır'}")
    print(f"Uyarı seviyesi: {vitals.get_alert_level()}")
    
    print("\nAnormal vital signs:")
    abnormal_vitals = VitalSigns(
        patient_id="PAT124",
        temperature=39.5,
        blood_pressure_systolic=160,
        blood_pressure_diastolic=100,
        heart_rate=110,
        respiratory_rate=22,
        oxygen_saturation=92
    )
    
    print(f"Normal mi? {'Evet' if abnormal_vitals.is_normal() else 'Hayır'}")
    print(f"Uyarı seviyesi: {abnormal_vitals.get_alert_level()}")
    
    print("\nMedication oluşturma:")
    medication = Medication(
        medication_id="MED001",
        name="Lisinopril",
        dosage="10mg",
        frequency="Once daily",
        route="Oral",
        prescribed_by="Dr. Johnson"
    )
    
    print(f"İlaç: {medication.name}")
    print(f"Doz: {medication.dosage}")
    print(f"Sıklık: {medication.frequency}")
    print(f"Yol: {medication.route}")
    print(f"Aktif mi? {'Evet' if medication.is_active() else 'Hayır'}")
    
    medication.add_side_effect("Dizziness")
    medication.add_side_effect("Dry cough")
    print(f"Yan etkiler: {', '.join(medication.side_effects)}")


def demonstrate_static_and_class_methods() -> None:
    """
    Static ve class method kullanımını gösterir
    """
    print_separator("STATİK VE CLASS METHOD KULLANIMI")
    
    print("\nBMI Hesaplama (Static Method):")
    weight = 75  # kg
    height = 175  # cm
    bmi = Patient.calculate_bmi(weight, height)
    print(f"Kilo: {weight}kg, Boy: {height}cm")
    print(f"BMI: {bmi}")
    
    if bmi < 18.5:
        category = "Düşük kilolu"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Fazla kilolu"
    else:
        category = "Obez"
    print(f"Kategori: {category}")
    
    print("\nKan Grubu Uyumluluğu (Static Method):")
    blood_type = "AB+"
    compatible = Patient.get_blood_type_compatibility(blood_type)
    print(f"{blood_type} kan grubu şu gruplardan kan alabilir:")
    print(f"  {', '.join(compatible)}")
    
    print("\nHasta ID Formatlama (Static Method):")
    raw_id = "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    formatted = Patient.format_patient_id(raw_id)
    print(f"Ham ID: {raw_id}")
    print(f"Formatlanmış: {formatted}")
    
    print("\nHasta Veri Validasyonu (Class Method):")
    valid_data = Patient.validate_patient_data("John Doe", 45, "male")
    invalid_data = Patient.validate_patient_data("", -5, "unknown")
    
    print(f"Geçerli veri: {'Evet' if valid_data else 'Hayır'}")
    print(f"Geçersiz veri: {'Evet' if invalid_data else 'Hayır'}")
    
    print("\nÖrnek Verilerle Repository Oluşturma (Class Method):")
    sample_repo = PatientRepository.create_repository_with_sample_data()
    print(f"Oluşturulan hasta sayısı: {sample_repo.count()}")
    
    stats
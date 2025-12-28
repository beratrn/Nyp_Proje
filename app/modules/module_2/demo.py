import sys
import os

# Mevcut dosyanın bulunduğu dizini path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from datetime import datetime, timedelta
from base import AppointmentBase
from implementations import (
    RoutineAppointment,
    EmergencyAppointment,
    OnlineAppointment,
    AppointmentService,
    Doctor
)
from repository import InMemoryAppointmentRepository, FileBasedAppointmentRepository


# Polimorfizm örneği 1: Farklı randevu tiplerini tek listede işleme
def polymorphism_example_1():
    print("\n" + "="*70)
    print("POLİMORFİZM ÖRNEĞİ 1: Farklı Randevu Tipleri - Tek Liste")
    print("="*70)
    
    now = datetime.now()
    
    randevular: list[AppointmentBase] = [
        RoutineAppointment(
            "APT001",
            "P001",
            "Dr. Mehmet Yılmaz",
            now + timedelta(days=1, hours=10),
            department="Kardiyoloji"
        ),
        EmergencyAppointment(
            "APT002",
            "P002",
            "Dr. Ayşe Demir",
            now + timedelta(hours=2),
            urgency_level="critical",
            symptoms=["Göğüs ağrısı", "Nefes darlığı"]
        ),
        OnlineAppointment(
            "APT003",
            "P003",
            "Dr. Ali Kaya",
            now + timedelta(days=2, hours=14),
            platform="Zoom",
            requires_prescription=True
        ),
        RoutineAppointment(
            "APT004",
            "P004",
            "Dr. Zeynep Şahin",
            now + timedelta(days=3, hours=11),
            department="Nöroloji",
            is_followup=True
        ),
        EmergencyAppointment(
            "APT005",
            "P005",
            "Dr. Can Öztürk",
            now + timedelta(hours=1),
            urgency_level="high",
            symptoms=["Kırık şüphesi"]
        )
    ]
    
    print(f"\nToplam {len(randevular)} randevu oluşturuldu.\n")
    
    print("Her randevu tipinin detaylarını polymorphism ile gösteriyoruz:\n")
    for i, randevu in enumerate(randevular, 1):
        print(f"\n--- Randevu {i} ---")
        print(f"Tip: {type(randevu).__name__}")
        print(randevu.get_appointment_details())
        print(f"Maliyet: {randevu.calculate_cost():.2f} TL")
        print("-" * 50)
    
    print("\n\nTüm randevuların toplam maliyeti:")
    toplam_maliyet = sum(randevu.calculate_cost() for randevu in randevular)
    print(f"Toplam: {toplam_maliyet:.2f} TL")


# Polimorfizm örneği 2: Repository'de farklı tipleri saklama ve çağırma
def polymorphism_example_2():
    print("\n" + "="*70)
    print("POLİMORFİZM ÖRNEĞİ 2: Repository ile Tip Bağımsız İşlemler")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    now = datetime.now()
    
    randevular: list[AppointmentBase] = [
        RoutineAppointment("R001", "P100", "Dr. Fatma Arslan", now + timedelta(days=5), department="Ortopedi"),
        EmergencyAppointment("E001", "P101", "Dr. Hakan Çelik", now + timedelta(hours=3), urgency_level="medium"),
        OnlineAppointment("O001", "P102", "Dr. Selin Aydın", now + timedelta(days=7), platform="Teams"),
        RoutineAppointment("R002", "P103", "Dr. Burak Yıldız", now + timedelta(days=4), department="Genel"),
        EmergencyAppointment("E002", "P104", "Dr. Elif Koç", now + timedelta(hours=4), urgency_level="low")
    ]
    
    print("\nRandevuları repository'ye kaydediyoruz...")
    for randevu in randevular:
        repository.save(randevu)
        print(f"✓ {randevu.appointment_id} kaydedildi ({type(randevu).__name__})")
    
    print(f"\n\nRepository'den tüm randevuları çekiyoruz (Polymorphism):")
    tum_randevular = repository.list_all()
    
    print(f"Toplam {len(tum_randevular)} randevu bulundu.\n")
    
    for randevu in tum_randevular:
        print(f"{randevu.appointment_id}: {type(randevu).__name__} - {randevu.doctor_name}")
        print(f"  → Durum: {randevu.status}, Maliyet: {randevu.calculate_cost():.2f} TL")
    
    print("\n\nİstatistikler:")
    stats = repository.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


# Temel randevu oluşturma senaryosu
def basic_appointment_scenario():
    print("\n" + "="*70)
    print("SENARYO 1: Temel Randevu Oluşturma ve Yönetim")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    
    now = datetime.now()
    
    print("\n1. Rutin Randevu Oluşturma:")
    routine = RoutineAppointment(
        "APT100",
        "P200",
        "Dr. Emre Yılmaz",
        now + timedelta(days=10, hours=9),
        department="Kardiyoloji",
        examination_type="EKG"
    )
    success, message = service.create_appointment(routine)
    print(f"   {message}")
    print(f"   Maliyet: {routine.calculate_cost():.2f} TL")
    
    print("\n2. Acil Randevu Oluşturma:")
    emergency = EmergencyAppointment(
        "APT101",
        "P201",
        "Dr. Aylin Demir",
        now + timedelta(hours=2),
        urgency_level="critical",
        symptoms=["Yüksek ateş", "Baş ağrısı", "Kusma"],
        requires_ambulance=True
    )
    success, message = service.create_appointment(emergency)
    print(f"   {message}")
    print(f"   Triyaj: {emergency.triage_code}")
    print(f"   Ambulans: {'Gerekli' if emergency.requires_ambulance else 'Gerekli değil'}")
    print(f"   Maliyet: {emergency.calculate_cost():.2f} TL")
    
    print("\n3. Online Randevu Oluşturma:")
    online = OnlineAppointment(
        "APT102",
        "P202",
        "Dr. Cem Öztürk",
        now + timedelta(days=3, hours=15),
        platform="Zoom",
        requires_prescription=True
    )
    success, message = service.create_appointment(online)
    print(f"   {message}")
    print(f"   Platform: {online.platform}")
    print(f"   Link: {online.meeting_link}")
    print(f"   Maliyet: {online.calculate_cost():.2f} TL")
    
    print("\n4. Repository Durumu:")
    stats = repository.get_statistics()
    print(f"   Toplam Randevu: {stats['total_appointments']}")
    print(f"   Toplam Hasta: {stats['unique_patients']}")
    print(f"   Toplam Doktor: {stats['unique_doctors']}")


# Randevu iptal ve erteleme senaryosu
def appointment_cancellation_scenario():
    print("\n" + "="*70)
    print("SENARYO 2: Randevu İptal ve Erteleme İşlemleri")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    
    now = datetime.now()
    
    appointment = RoutineAppointment(
        "APT200",
        "P300",
        "Dr. Deniz Akar",
        now + timedelta(days=5, hours=10),
        department="Nöroloji"
    )
    
    print("\n1. Randevu Oluşturma:")
    service.create_appointment(appointment)
    print(f"   {appointment.appointment_id} oluşturuldu")
    print(f"   Tarih: {appointment.date_time.strftime('%d.%m.%Y %H:%M')}")
    
    print("\n2. Randevu Erteleme:")
    new_date = now + timedelta(days=8, hours=14)
    success, message = service.postpone_appointment("APT200", new_date)
    print(f"   {message}")
    updated = repository.find_by_id("APT200")
    if updated:
      print(f" Yeni Tarih: {updated.date_time.strftime('%d.%m.%Y %H:%M')}")
      print(f"   Durum: {updated.status}")
    else:
      print("İşlem başarısız: Güncellenecek randevu bulunamadı.")
      return 
    
    can_cancel = updated.can_be_cancelled()
    
    print("\n3. Randevu İptal Kontrolü:")
    can_cancel = updated.can_be_cancelled()
    print(f"   İptal edilebilir mi? {'Evet' if can_cancel else 'Hayır'}")
    print(f"   Randevuya kalan süre: {updated.get_time_until_appointment():.1f} saat")
    
    print("\n4. Randevu İptali:")
    success, message = service.cancel_appointment("APT200")
    print(f"   {message}")
    cancelled = repository.find_by_id("APT200")
    print(f"   Son Durum: {cancelled.status}")


# Acil durum senaryosu
def emergency_scenario():
    print("\n" + "="*70)
    print("SENARYO 3: Acil Durum Randevu Yönetimi")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    
    now = datetime.now()
    
    print("\n1. Düşük Öncelikli Acil Randevu:")
    emergency_low = EmergencyAppointment(
        "EMR001",
        "P400",
        "Dr. Gizem Yıldırım",
        now + timedelta(hours=6),
        urgency_level="low",
        symptoms=["Hafif baş ağrısı"]
    )
    service.create_appointment(emergency_low)
    print(f"   Triyaj Kodu: {emergency_low.triage_code}")
    print(f"   Max Bekleme: {emergency_low.get_max_waiting_time()} dakika")
    print(f"   Kritik mi? {'Evet' if emergency_low.is_critical() else 'Hayır'}")
    
    print("\n2. Aciliyeti Yükseltme:")
    before = emergency_low.urgency_level
    emergency_low.escalate_urgency()
    print(f"   Önceki Seviye: {before}")
    print(f"   Yeni Seviye: {emergency_low.urgency_level}")
    print(f"   Yeni Triyaj: {emergency_low.triage_code}")
    
    print("\n3. Kritik Acil Durum:")
    emergency_critical = EmergencyAppointment(
        "EMR002",
        "P401",
        "Dr. Kaan Özcan",
        now + timedelta(minutes=30),
        urgency_level="critical",
        symptoms=["Göğüs ağrısı", "Nefes darlığı", "Terleme"],
        requires_ambulance=True
    )
    service.create_appointment(emergency_critical)
    print(f"   Triyaj Kodu: {emergency_critical.triage_code}")
    print(f"   Max Bekleme: {emergency_critical.get_max_waiting_time()} dakika")
    print(f"   Kritik mi? {'Evet' if emergency_critical.is_critical() else 'Hayır'}")
    
    print("\n4. Ambulans Talebi:")
    ambulance_info = emergency_critical.request_ambulance()
    for key, value in ambulance_info.items():
        print(f"   {key}: {value}")


# Online randevu senaryosu
def online_appointment_scenario():
    print("\n" + "="*70)
    print("SENARYO 4: Online Randevu İşlemleri")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    
    now = datetime.now()
    
    print("\n1. Online Randevu Oluşturma:")
    online = OnlineAppointment(
        "ONL001",
        "P500",
        "Dr. Lale Şen",
        now + timedelta(days=2, hours=16),
        platform="Teams",
        requires_prescription=False
    )
    service.create_appointment(online)
    print(f"   Platform: {online.platform}")
    print(f"   Session ID: {online.session_id}")
    print(f"   Link: {online.meeting_link}")
    
    print("\n2. Bağlantı Testi:")
    quality = online.test_connection()
    print(f"   Bağlantı Kalitesi: {quality}")
    
    print("\n3. Toplantıyı Başlatma:")
    meeting_info = online.start_meeting()
    for key, value in meeting_info.items():
        print(f"   {key}: {value}")
    
    print("\n4. Teknik Destek Bilgileri:")
    support = online.get_technical_support()
    print(f"   Platform: {support['platform']}")
    print(f"   Destek Linki: {support['support_link']}")
    print("   Sorun Giderme Adımları:")
    for i, step in enumerate(support['troubleshooting_steps'], 1):
        print(f"     {i}. {step}")
    
    print("\n5. Toplantıyı Sonlandırma:")
    online.end_meeting(45)
    print(f"   Toplantı Süresi: {online.meeting_duration_minutes} dakika")
    print(f"   Son Durum: {online.status}")


# İstatistik ve analiz senaryosu
def statistics_scenario():
    print("\n" + "="*70)
    print("SENARYO 5: İstatistik ve Analiz")
    print("="*70)
    
    repository = InMemoryAppointmentRepository()
    service = AppointmentService(repository)
    
    now = datetime.now()
    
    randevular = [
        RoutineAppointment("S001", "P601", "Dr. Mert Aydın", now + timedelta(days=1), department="Kardiyoloji"),
        RoutineAppointment("S002", "P602", "Dr. Mert Aydın", now + timedelta(days=1, hours=1), department="Kardiyoloji"),
        EmergencyAppointment("S003", "P603", "Dr. Naz Kara", now + timedelta(hours=2), urgency_level="high"),
        OnlineAppointment("S004", "P604", "Dr. Onur Bal", now + timedelta(days=2), platform="Zoom"),
        RoutineAppointment("S005", "P605", "Dr. Mert Aydın", now + timedelta(days=1, hours=2), department="Kardiyoloji"),
        EmergencyAppointment("S006", "P606", "Dr. Pelin Taş", now + timedelta(hours=3), urgency_level="critical"),
        OnlineAppointment("S007", "P607", "Dr. Onur Bal", now + timedelta(days=2, hours=1), platform="Teams"),
        RoutineAppointment("S008", "P608", "Dr. Mert Aydın", now + timedelta(days=3), department="Nöroloji")
    ]
    
    for randevu in randevular:
        service.create_appointment(randevu)
    
    print(f"\n1. Toplam {len(randevular)} randevu oluşturuldu")
    
    print("\n2. Doktora Göre Randevular:")
    doctor_appointments = service.list_appointments_by_doctor("Dr. Mert Aydın")
    print(f"   Dr. Mert Aydın: {len(doctor_appointments)} randevu")
    
    print("\n3. Randevu Tipi Dağılımı:")
    distribution = AppointmentService.calculate_appointment_type_distribution(randevular)
    print("   Sayılar:")
    for tip, count in distribution['counts'].items():
        print(f"     {tip}: {count}")
    print("   Yüzdeler:")
    for tip, percent in distribution['percentages'].items():
        print(f"     {tip}: {percent:.1f}%")
    
    print("\n4. Günlük İstatistikler:")
    target_date = now + timedelta(days=1)
    daily_stats = service.get_daily_statistics(target_date)
    for key, value in daily_stats.items():
        print(f"   {key}: {value}")
    
    print("\n5. Doktor İş Yükü Analizi:")
    workload = service.analyze_doctor_workload("Dr. Mert Aydın", now + timedelta(days=1))
    for key, value in workload.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n6. En Yoğun Saatler:")
    peak_hours = AppointmentService.find_peak_appointment_hours(randevular)
    print(f"   Yoğun Saatler: {', '.join(map(str, peak_hours))}")


# Dosya tabanlı repository senaryosu
def file_repository_scenario():
    print("\n" + "="*70)
    print("SENARYO 6: Dosya Tabanlı Veri Saklama")
    print("="*70)
    
    file_repo = FileBasedAppointmentRepository("test_appointments.json")
    
    now = datetime.now()
    
    print("\n1. Randevuları JSON dosyasına kaydetme:")
    appointments = [
        RoutineAppointment("F001", "P700", "Dr. Rana Öz", now + timedelta(days=4), department="Ortopedi"),
        EmergencyAppointment("F002", "P701", "Dr. Sinan Er", now + timedelta(hours=5), urgency_level="medium"),
        OnlineAppointment("F003", "P702", "Dr. Tuba Ak", now + timedelta(days=6), platform="Google Meet")
    ]
    
    for apt in appointments:
        file_repo.save(apt)
        print(f"   ✓ {apt.appointment_id} dosyaya kaydedildi")
    
    print("\n2. Dosyadan Okuma:")
    all_from_file = file_repo.list_all()
    print(f"   Dosyadan {len(all_from_file)} randevu okundu")
    
    print("\n3. Dosya İstatistikleri:")
    stats = file_repo.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n4. Yedekleme:")
    backup_success = file_repo.backup("backup_appointments.json")
    print(f"   Yedekleme: {'Başarılı' if backup_success else 'Başarısız'}")
    
    print("\n5. Temizlik:")
    file_repo.clear_all()
    print("   Dosya temizlendi")


# Ana demo fonksiyonu
def run_all_demos():
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + " " * 15 + "RANDEVU YÖNETİM SİSTEMİ DEMO" + " " * 25 + "*")
    print("*" + " " * 15 + "Doktor & Randevu Modülü" + " " * 30 + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    polymorphism_example_1()
    polymorphism_example_2()
    basic_appointment_scenario()
    appointment_cancellation_scenario()
    emergency_scenario()
    online_appointment_scenario()
    statistics_scenario()
    file_repository_scenario()
    
    print("\n" + "="*70)
    print("TÜM DEMOLAR TAMAMLANDI!")
    print("="*70 + "\n")


# Programı çalıştır
if __name__ == "__main__":
    run_all_demos()
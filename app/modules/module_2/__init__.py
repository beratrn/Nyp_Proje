# Randevu modülünün ana paket tanımlama dosyası
"""
Doktor & Randevu Modülü (Appointment Module)

Bu modül hastane otomasyon sisteminde doktor randevularının yönetimini sağlar.
Farklı randevu tiplerini (rutin, acil, online) destekler ve randevu işlemlerini
(oluşturma, iptal, erteleme) yönetir.

Modül Yapısı:
    - base.py: Soyut temel sınıf (AppointmentBase)
    - implementations.py: Somut randevu tipleri ve servis sınıfları
    - repository.py: Veri yönetim katmanı
    - demo.py: Örnek kullanım senaryoları

Ana Sınıflar:
    - AppointmentBase: Tüm randevu tiplerinin soyut base class'ı
    - RoutineAppointment: Rutin kontrol randevuları
    - EmergencyAppointment: Acil durum randevuları
    - OnlineAppointment: Online görüşme randevuları
    - AppointmentService: Randevu işlemlerini yöneten servis katmanı
    - AppointmentRepository: Randevu verilerini saklayan repository katmanı

Yazar: [Öğrenci İsmi]
Tarih: Aralık 2025
Ders: Nesne Yönelimli Programlama
"""

# Base sınıfı import et
from base import AppointmentBase

# Implementation sınıfları import et
from implementations import (
    RoutineAppointment,
    EmergencyAppointment,
    OnlineAppointment,
    Doctor,
    AppointmentService
)

# Repository sınıfları import et
from repository import (
    InMemoryAppointmentRepository,
    FileBasedAppointmentRepository
)

# Modül versiyonu
__version__ = "1.0.0"

# Modül yazarı
__author__ = "Öğrenci İsmi"

# Modülün kısa açıklaması
__doc__ = "Doktor ve Randevu Yönetim Modülü"

# Public API - dışarıya açılan sınıflar
__all__ = [
    "AppointmentBase",
    "RoutineAppointment",
    "EmergencyAppointment",
    "OnlineAppointment",
    "Doctor",
    "AppointmentService",
    "InMemoryAppointmentRepository",
    "FileBasedAppointmentRepository"
]

# Modül başlatma mesajı (geliştirme aşamasında kullanışlı)
def _initialize_module():
    """Modül başlatma fonksiyonu, gerekli kontrolleri yapar"""
    pass

# Modül yüklendiğinde çalışacak kod
_initialize_module()

# Modül hakkında bilgi döndüren yardımcı fonksiyon
def get_module_info():
    """Modül hakkında bilgi döndürür"""
    return {
        "name": "Appointment Module",
        "version": __version__,
        "author": __author__,
        "description": "Doktor ve randevu yönetim sistemi"
    }

# Modülde kullanılabilir randevu durumları
APPOINTMENT_STATUSES = [
    "scheduled",
    "in_progress", 
    "completed",
    "cancelled",
    "postponed"
]

# Randevu tipleri
APPOINTMENT_TYPES = [
    "routine",
    "emergency",
    "online"
]

# Varsayılan çalışma saatleri
DEFAULT_WORKING_HOURS = {
    "start": 9,
    "end": 17,
    "slot_duration": 30  # dakika
}

# Randevu iptal kuralları
CANCELLATION_RULES = {
    "min_hours_before": 2,  # Randevudan en az 2 saat önce iptal edilebilir
    "max_cancellations_per_month": 3  # Ayda maksimum 3 iptal
}
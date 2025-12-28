from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from base import AppointmentBase
import random
import string


# Rutin kontrol randevuları için sınıf, düzenli hasta takibi için kullanılır
class RoutineAppointment(AppointmentBase):
    
    # Rutin randevu nesnesi oluşturur ve ek özellikler ekler
    def __init__(
        self,
        appointment_id: str,
        patient_id: str,
        doctor_name: str,
        date_time: datetime,
        status: str = "scheduled",
        department: str = "Genel",
        is_followup: bool = False,
        previous_appointment_id: Optional[str] = None,
        examination_type = "Genel Muayene"
    ):
        super().__init__(appointment_id, patient_id, doctor_name, date_time, status)
        self.__department = department
        self.__is_followup = is_followup
        self.__previous_appointment_id = previous_appointment_id
        self.__examination_type = examination_type 
        self.__estimated_duration = 30
    
    # Departman bilgisini döndürür
    @property
    def department(self) -> str:
        return self.__department
    
    # Departman bilgisini ayarlar
    @department.setter
    def department(self, value: str) -> None:
        self.__department = value
    
    # Takip randevusu olup olmadığını döndürür
    @property
    def is_followup(self) -> bool:
        return self.__is_followup
    
    # Takip randevusu özelliğini ayarlar
    @is_followup.setter
    def is_followup(self, value: bool) -> None:
        self.__is_followup = value
    
    # Önceki randevu ID'sini döndürür
    @property
    def previous_appointment_id(self) -> Optional[str]:
        return self.__previous_appointment_id
    
    # Önceki randevu ID'sini ayarlar
    @previous_appointment_id.setter
    def previous_appointment_id(self, value: Optional[str]) -> None:
        self.__previous_appointment_id = value
    
    # Muayene tipini döndürür
    @property
    def examination_type(self) -> str:
        return self.__examination_type
    
    # Muayene tipini ayarlar
    @examination_type.setter
    def examination_type(self, value: str) -> None:
        self.__examination_type = value
    
    # Tahmini süreyi döndürür
    @property
    def estimated_duration(self) -> int:
        return self.__estimated_duration
    
    # Tahmini süreyi ayarlar
    @estimated_duration.setter
    def estimated_duration(self, value: int) -> None:
        if value < 15 or value > 120:
            raise ValueError("Süre 15-120 dakika arasında olmalıdır")
        self.__estimated_duration = value
    
    # Randevunun detaylı açıklamasını döndürür
    def get_appointment_details(self) -> str:
        followup_text = "Takip Randevusu" if self.__is_followup else "İlk Randevu"
        details = f"Rutin Randevu - {followup_text}\n"
        details += f"Departman: {self.__department}\n"
        details += f"Muayene Tipi: {self.__examination_type}\n"
        details += f"Tahmini Süre: {self.__estimated_duration} dakika\n"
        details += f"Doktor: {self.doctor_name}\n"
        details += f"Tarih: {self.date_time.strftime('%d.%m.%Y %H:%M')}\n"
        details += f"Durum: {self.status}"
        if self.__previous_appointment_id:
            details += f"\nÖnceki Randevu: {self.__previous_appointment_id}"
        return details
    
    # Randevu maliyetini hesaplar, takip randevularında indirim uygulanır
    def calculate_cost(self) -> float:
        base_cost = 200.0
        if self.__is_followup:
            base_cost *= 0.8
        if self.__estimated_duration > 45:
            base_cost += 50.0
        department_multipliers = {
            "Kardiyoloji": 1.5,
            "Nöroloji": 1.4,
            "Ortopedi": 1.3,
            "Genel": 1.0
        }
        multiplier = department_multipliers.get(self.__department, 1.0)
        return base_cost * multiplier
    
    # Sonraki kontrol randevusunu otomatik önerir
    def suggest_next_appointment(self, weeks_later: int = 4) -> datetime:
        next_date = self.date_time + timedelta(weeks=weeks_later)
        while next_date.weekday() > 4:
            next_date += timedelta(days=1)
        return next_date
    
    # Randevuyu takip randevusu olarak işaretler
    def mark_as_followup(self, previous_id: str) -> None:
        self.__is_followup = True
        self.__previous_appointment_id = previous_id
    
    # Departman değiştirme işlemi yapar
    def change_department(self, new_department: str) -> bool:
        if self.status != "scheduled":
            return False
        self.__department = new_department
        return True
    
    # Randevunun öncelik seviyesini hesaplar
    def get_priority_level(self) -> str:
        if self.__is_followup:
            return "Orta"
        hours_until = self.get_time_until_appointment()
        if hours_until < 24:
            return "Yüksek"
        return "Düşük"


# Acil durum randevuları için sınıf, ivedi müdahale gerektiren durumlar için
class EmergencyAppointment(AppointmentBase):
    
    # Acil randevu nesnesi oluşturur ve aciliyet özellikleri ekler
    def __init__(
        self,
        appointment_id: str,
        patient_id: str,
        doctor_name: str,
        date_time: datetime,
        status: str = "scheduled",
        urgency_level: str = "high",
        symptoms: List[str] = None,
        requires_ambulance: bool = False
    ):
        super().__init__(appointment_id, patient_id, doctor_name, date_time, status)
        self.__urgency_level = urgency_level
        self.__symptoms = symptoms if symptoms else []
        self.__requires_ambulance = requires_ambulance
        self.__triage_code = self._assign_triage_code()
        self.__arrival_time = None
        self.__response_time_minutes = 0
    
    # Aciliyet seviyesini döndürür
    @property
    def urgency_level(self) -> str:
        return self.__urgency_level
    
    # Aciliyet seviyesini ayarlar
    @urgency_level.setter
    def urgency_level(self, value: str) -> None:
        valid_levels = ["critical", "high", "medium", "low"]
        if value not in valid_levels:
            raise ValueError(f"Geçersiz aciliyet seviyesi: {value}")
        self.__urgency_level = value
        self.__triage_code = self._assign_triage_code()
    
    # Semptom listesini döndürür
    @property
    def symptoms(self) -> List[str]:
        return self.__symptoms.copy()
    
    # Ambulans gereksinimi bilgisini döndürür
    @property
    def requires_ambulance(self) -> bool:
        return self.__requires_ambulance
    
    # Ambulans gereksinimi bilgisini ayarlar
    @requires_ambulance.setter
    def requires_ambulance(self, value: bool) -> None:
        self.__requires_ambulance = value
    
    # Triyaj kodunu döndürür
    @property
    def triage_code(self) -> str:
        return self.__triage_code
    
    # Varış zamanını döndürür
    @property
    def arrival_time(self) -> Optional[datetime]:
        return self.__arrival_time
    
    # Varış zamanını ayarlar
    @arrival_time.setter
    def arrival_time(self, value: datetime) -> None:
        self.__arrival_time = value
        if value:
            self.__response_time_minutes = (value - self.date_time).total_seconds() / 60
    
    # Müdahale süresini döndürür
    @property
    def response_time_minutes(self) -> float:
        return self.__response_time_minutes
    
    # Aciliyet seviyesine göre triyaj kodu atar
    def _assign_triage_code(self) -> str:
        triage_map = {
            "critical": "RED",
            "high": "ORANGE",
            "medium": "YELLOW",
            "low": "GREEN"
        }
        return triage_map.get(self.__urgency_level, "GREEN")
    
    # Randevunun detaylı açıklamasını döndürür
    def get_appointment_details(self) -> str:
        details = f"ACİL RANDEVU - Triyaj: {self.__triage_code}\n"
        details += f"Aciliyet: {self.__urgency_level.upper()}\n"
        details += f"Doktor: {self.doctor_name}\n"
        details += f"Tarih: {self.date_time.strftime('%d.%m.%Y %H:%M')}\n"
        if self.__symptoms:
            details += f"Semptomlar: {', '.join(self.__symptoms)}\n"
        details += f"Ambulans Gerekli: {'Evet' if self.__requires_ambulance else 'Hayır'}\n"
        if self.__arrival_time:
            details += f"Varış Zamanı: {self.__arrival_time.strftime('%H:%M')}\n"
            details += f"Müdahale Süresi: {self.__response_time_minutes:.1f} dakika\n"
        details += f"Durum: {self.status}"
        return details
    
    # Acil randevu maliyetini hesaplar, aciliyet seviyesine göre fiyatlandırma yapar
    def calculate_cost(self) -> float:
        base_cost = 500.0
        urgency_multipliers = {
            "critical": 3.0,
            "high": 2.0,
            "medium": 1.5,
            "low": 1.2
        }
        multiplier = urgency_multipliers.get(self.__urgency_level, 1.5)
        total_cost = base_cost * multiplier
        if self.__requires_ambulance:
            total_cost += 300.0
        if len(self.__symptoms) > 3:
            total_cost += 100.0
        return total_cost
    
    # Semptom listesine yeni semptom ekler
    def add_symptom(self, symptom: str) -> None:
        if symptom and symptom not in self.__symptoms:
            self.__symptoms.append(symptom)
    
    # Semptom listesinden semptom kaldırır
    def remove_symptom(self, symptom: str) -> bool:
        if symptom in self.__symptoms:
            self.__symptoms.remove(symptom)
            return True
        return False
    
    # Aciliyet seviyesini yükseltir
    def escalate_urgency(self) -> bool:
        escalation_map = {
            "low": "medium",
            "medium": "high",
            "high": "critical"
        }
        if self.__urgency_level in escalation_map:
            self.__urgency_level = escalation_map[self.__urgency_level]
            self.__triage_code = self._assign_triage_code()
            return True
        return False
    
    # Maksimum bekleme süresini dakika cinsinden döndürür
    def get_max_waiting_time(self) -> int:
        waiting_times = {
            "critical": 0,
            "high": 10,
            "medium": 30,
            "low": 60
        }
        return waiting_times.get(self.__urgency_level, 60)
    
    # Randevunun kritik olup olmadığını kontrol eder
    def is_critical(self) -> bool:
        return self.__urgency_level == "critical" or self.__triage_code == "RED"
    
    # Ambulans çağrısı başlatır
    def request_ambulance(self) -> Dict:
        self.__requires_ambulance = True
        return {
            "status": "requested",
            "priority": self.__urgency_level,
            "triage": self.__triage_code,
            "estimated_arrival": (datetime.now() + timedelta(minutes=15)).strftime("%H:%M")
        }


# Online görüşme randevuları için sınıf, uzaktan konsültasyon sağlar
class OnlineAppointment(AppointmentBase):
    
    # Online randevu nesnesi oluşturur ve dijital özellikler ekler
    def __init__(
        self,
        appointment_id: str,
        patient_id: str,
        doctor_name: str,
        date_time: datetime,
        status: str = "scheduled",
        platform: str = "Zoom",
        meeting_link: Optional[str] = None,
        requires_prescription: bool = False
    ):
        super().__init__(appointment_id, patient_id, doctor_name, date_time, status)
        self.__platform = platform
        self.__meeting_link = meeting_link if meeting_link else self._generate_meeting_link()
        self.__requires_prescription = requires_prescription
        self.__connection_quality = "unknown"
        self.__meeting_duration_minutes = 0
        self.__recording_enabled = False
        self.__session_id = self._generate_session_id()
    
    # Platform bilgisini döndürür
    @property
    def platform(self) -> str:
        return self.__platform
    
    # Platform bilgisini ayarlar
    @platform.setter
    def platform(self, value: str) -> None:
        valid_platforms = ["Zoom", "Teams", "Google Meet", "Skype"]
        if value not in valid_platforms:
            raise ValueError(f"Geçersiz platform: {value}")
        self.__platform = value
    
    # Toplantı linkini döndürür
    @property
    def meeting_link(self) -> str:
        return self.__meeting_link
    
    # Reçete gereksinimi bilgisini döndürür
    @property
    def requires_prescription(self) -> bool:
        return self.__requires_prescription
    
    # Reçete gereksinimi bilgisini ayarlar
    @requires_prescription.setter
    def requires_prescription(self, value: bool) -> None:
        self.__requires_prescription = value
    
    # Bağlantı kalitesi bilgisini döndürür
    @property
    def connection_quality(self) -> str:
        return self.__connection_quality
    
    # Bağlantı kalitesi bilgisini ayarlar
    @connection_quality.setter
    def connection_quality(self, value: str) -> None:
        valid_qualities = ["excellent", "good", "fair", "poor", "unknown"]
        if value not in valid_qualities:
            raise ValueError(f"Geçersiz bağlantı kalitesi: {value}")
        self.__connection_quality = value
    
    # Toplantı süresini döndürür
    @property
    def meeting_duration_minutes(self) -> int:
        return self.__meeting_duration_minutes
    
    # Kayıt durumunu döndürür
    @property
    def recording_enabled(self) -> bool:
        return self.__recording_enabled
    
    # Kayıt durumunu ayarlar
    @recording_enabled.setter
    def recording_enabled(self, value: bool) -> None:
        self.__recording_enabled = value
    
    # Oturum ID'sini döndürür
    @property
    def session_id(self) -> str:
        return self.__session_id
    
    # Rastgele toplantı linki oluşturur
    def _generate_meeting_link(self) -> str:
        random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return f"https://{self.__platform.lower()}.com/j/{random_code}"
    
    # Rastgele oturum ID'si oluşturur
    def _generate_session_id(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # Randevunun detaylı açıklamasını döndürür
    def get_appointment_details(self) -> str:
        details = f"ONLİNE RANDEVU\n"
        details += f"Platform: {self.__platform}\n"
        details += f"Toplantı Linki: {self.__meeting_link}\n"
        details += f"Oturum ID: {self.__session_id}\n"
        details += f"Doktor: {self.doctor_name}\n"
        details += f"Tarih: {self.date_time.strftime('%d.%m.%Y %H:%M')}\n"
        details += f"Reçete Gerekli: {'Evet' if self.__requires_prescription else 'Hayır'}\n"
        if self.__meeting_duration_minutes > 0:
            details += f"Toplantı Süresi: {self.__meeting_duration_minutes} dakika\n"
        if self.__connection_quality != "unknown":
            details += f"Bağlantı Kalitesi: {self.__connection_quality}\n"
        details += f"Kayıt: {'Açık' if self.__recording_enabled else 'Kapalı'}\n"
        details += f"Durum: {self.status}"
        return details
    
    # Online randevu maliyetini hesaplar, indirimli fiyatlandırma uygulanır
    def calculate_cost(self) -> float:
        base_cost = 150.0
        if self.__requires_prescription:
            base_cost += 30.0
        if self.__recording_enabled:
            base_cost += 20.0
        return base_cost
    
    # Toplantı linkini yeniler
    def regenerate_meeting_link(self) -> str:
        self.__meeting_link = self._generate_meeting_link()
        return self.__meeting_link
    
    # Toplantıyı başlatır ve bilgileri döndürür
    def start_meeting(self) -> Dict:
        if self.status != "scheduled":
            return {"error": "Randevu başlatılamaz"}
        self.status = "in_progress"
        return {
            "status": "started",
            "link": self.__meeting_link,
            "session_id": self.__session_id,
            "platform": self.__platform,
            "instructions": f"{self.__platform} uygulamasını açın ve linke tıklayın"
        }
    
    # Toplantıyı sonlandırır ve süreyi kaydeder
    def end_meeting(self, duration_minutes: int) -> bool:
        if self.status != "in_progress":
            return False
        self.__meeting_duration_minutes = duration_minutes
        self.status = "completed"
        return True
    
    # Bağlantı testi yapar ve kaliteyi belirler
    def test_connection(self) -> str:
        quality_options = ["excellent", "good", "fair", "poor"]
        self.__connection_quality = random.choice(quality_options)
        return self.__connection_quality
    
    # Teknik destek bilgileri sağlar
    def get_technical_support(self) -> Dict:
        return {
            "platform": self.__platform,
            "support_link": f"https://{self.__platform.lower()}.com/support",
            "troubleshooting_steps": [
                "İnternet bağlantınızı kontrol edin",
                "Tarayıcınızı güncelleyin",
                "Kamera ve mikrofon izinlerini verin",
                f"{self.__platform} uygulamasını yeniden başlatın"
            ],
            "contact": "teknik.destek@hastane.com"
        }
    
    # Randevunun uygun teknolojik gereksinimleri sağlayıp sağlamadığını kontrol eder
    def check_technical_requirements(self) -> Dict:
        return {
            "internet_speed_required": "5 Mbps minimum",
            "browser_support": ["Chrome", "Firefox", "Safari", "Edge"],
            "camera_required": True,
            "microphone_required": True,
            "speakers_required": True,
            "platform": self.__platform,
            "mobile_support": True
        }


# Doktor varlık sınıfı, doktor bilgilerini tutar
class Doctor:
    
    # Doktor nesnesi oluşturur
    def __init__(
        self,
        doctor_id: str,
        name: str,
        specialization: str,
        phone: str,
        email: str
    ):
        self.__doctor_id = doctor_id
        self.__name = name
        self.__specialization = specialization
        self.__phone = phone
        self.__email = email
        self.__available_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.__max_daily_appointments = 16
        self.__rating = 0.0
        self.__total_patients = 0
    
    # Doktor ID'sini döndürür
    @property
    def doctor_id(self) -> str:
        return self.__doctor_id
    
    # Doktor adını döndürür
    @property
    def name(self) -> str:
        return self.__name
    
    # Uzmanlık alanını döndürür
    @property
    def specialization(self) -> str:
        return self.__specialization
    
    # Telefon numarasını döndürür
    @property
    def phone(self) -> str:
        return self.__phone
    
    # Email adresini döndürür
    @property
    def email(self) -> str:
        return self.__email
    
    # Müsait günleri döndürür
    @property
    def available_days(self) -> List[str]:
        return self.__available_days.copy()
    
    # Günlük maksimum randevu sayısını döndürür
    @property
    def max_daily_appointments(self) -> int:
        return self.__max_daily_appointments
    
    # Doktor puanını döndürür
    @property
    def rating(self) -> float:
        return self.__rating
    
    # Toplam hasta sayısını döndürür
    @property
    def total_patients(self) -> int:
        return self.__total_patients
    
    # Doktor bilgilerini string olarak döndürür
    def __str__(self) -> str:
        return f"Dr. {self.__name} - {self.__specialization}"
    
    # Doktorun belirli bir günde müsait olup olmadığını kontrol eder
    def is_available_on_day(self, day: str) -> bool:
        return day in self.__available_days
    
    # Doktora puan ekler ve ortalama puanı günceller
    def add_rating(self, rating: float) -> None:
        if 0 <= rating <= 5:
            total_rating = self.__rating * self.__total_patients
            self.__total_patients += 1
            self.__rating = (total_rating + rating) / self.__total_patients


# Randevu yönetim servisi, iş mantığını ve işlemleri yönetir
class AppointmentService:
    
    # Servis nesnesini başlatır ve repository referansını alır
    def __init__(self, repository=None):
        self.__repository = repository
        self.__notification_log = []
        self.__cancellation_count = {}
        self.__appointment_history = []
    
    # Repository referansını döndürür
    @property
    def repository(self):
        return self.__repository
    
    # Repository referansını ayarlar
    @repository.setter
    def repository(self, value) -> None:
        self.__repository = value
    
    # Bildirim logunu döndürür
    @property
    def notification_log(self) -> List[str]:
        return self.__notification_log.copy()
    
    # Yeni bir randevu oluşturur ve repository'ye kaydeder
    def create_appointment(self, appointment: AppointmentBase) -> Tuple[bool, str]:
        if not appointment.is_valid():
            return False, "Geçersiz randevu bilgileri"
        if not self.__check_time_availability(appointment):
            return False, "Seçilen zaman uygun değil"
        if self.__repository:
            success = self.__repository.save(appointment)
            if success:
                self.__appointment_history.append({
                    "action": "created",
                    "appointment_id": appointment.appointment_id,
                    "timestamp": datetime.now()
                })
                self.__send_notification(
                    appointment.patient_id,
                    f"Randevunuz oluşturuldu: {appointment.date_time.strftime('%d.%m.%Y %H:%M')}"
                )
                return True, "Randevu başarıyla oluşturuldu"
        return False, "Randevu kaydedilemedi"
    
    # Randevuyu iptal eder ve bildirim gönderir
    def cancel_appointment(self, appointment_id: str) -> Tuple[bool, str]:
        if not self.__repository:
            return False, "Repository bulunamadı"
        appointment = self.__repository.find_by_id(appointment_id)
        if not appointment:
            return False, "Randevu bulunamadı"
        if not appointment.can_be_cancelled():
            return False, "Randevu iptal edilemez"
        patient_id = appointment.patient_id
        if patient_id not in self.__cancellation_count:
            self.__cancellation_count[patient_id] = 0
        self.__cancellation_count[patient_id] += 1
        if appointment.cancel_appointment():
            self.__repository.update(appointment)
            self.__appointment_history.append({
                "action": "cancelled",
                "appointment_id": appointment_id,
                "timestamp": datetime.now()
            })
            self.__send_notification(
                patient_id,
                f"Randevunuz iptal edildi: {appointment_id}"
            )
            return True, "Randevu iptal edildi"
        return False, "İptal işlemi başarısız"
    
    # Randevuyu yeni bir tarihe erteler
    def postpone_appointment(
        self,
        appointment_id: str,
        new_date_time: datetime
    ) -> Tuple[bool, str]:
        if not self.__repository:
            return False, "Repository bulunamadı"
        appointment = self.__repository.find_by_id(appointment_id)
        if not appointment:
            return False, "Randevu bulunamadı"
        if appointment.postpone_appointment(new_date_time):
            self.__repository.update(appointment)
            self.__appointment_history.append({
                "action": "postponed",
                "appointment_id": appointment_id,
                "new_date": new_date_time,
                "timestamp": datetime.now()
            })
            self.__send_notification(
                appointment.patient_id,
                f"Randevunuz ertelendi. Yeni tarih: {new_date_time.strftime('%d.%m.%Y %H:%M')}"
            )
            return True, "Randevu ertelendi"
        return False, "Erteleme işlemi başarısız"
    
    # Randevuyu tamamlanmış olarak işaretler
    def complete_appointment(self, appointment_id: str) -> Tuple[bool, str]:
        if not self.__repository:
            return False, "Repository bulunamadı"
        appointment = self.__repository.find_by_id(appointment_id)
        if not appointment:
            return False, "Randevu bulunamadı"
        if appointment.complete_appointment():
            self.__repository.update(appointment)
            self.__appointment_history.append({
                "action": "completed",
                "appointment_id": appointment_id,
                "timestamp": datetime.now()
            })
            self.__send_notification(
                appointment.patient_id,
                f"Randevunuz tamamlandı: {appointment_id}"
            )
            return True, "Randevu tamamlandı"
        return False, "Tamamlama işlemi başarısız"
    
    # Belirli bir doktora ait randevuları listeler
    def list_appointments_by_doctor(self, doctor_name: str) -> List[AppointmentBase]:
        if not self.__repository:
            return []
        all_appointments = self.__repository.list_all()
        return [apt for apt in all_appointments if apt.doctor_name == doctor_name]
    
    # Belirli bir hastaya ait randevuları listeler
    def list_appointments_by_patient(self, patient_id: str) -> List[AppointmentBase]:
        if not self.__repository:
            return []
        all_appointments = self.__repository.list_all()
        return [apt for apt in all_appointments if apt.patient_id == patient_id]
    
    # Belirli bir tarih aralığındaki randevuları listeler
    def list_appointments_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[AppointmentBase]:
        if not self.__repository:
            return []
        all_appointments = self.__repository.list_all()
        return [
            apt for apt in all_appointments
            if start_date <= apt.date_time <= end_date
        ]
    
    # Belirli bir durumdaki randevuları listeler
    def list_appointments_by_status(self, status: str) -> List[AppointmentBase]:
        if not self.__repository:
            return []
        all_appointments = self.__repository.list_all()
        return [apt for apt in all_appointments if apt.status == status]
    
    # Hastaya bildirim gönderir ve loga kaydeder
    def __send_notification(self, patient_id: str, message: str) -> None:
        notification = {
            "patient_id": patient_id,
            "message": message,
            "timestamp": datetime.now(),
            "type": "sms"
        }
        self.__notification_log.append(notification)
    
    # Zaman uygunluğunu kontrol eder
    def __check_time_availability(self, appointment: AppointmentBase) -> bool:
        if not AppointmentBase.is_valid_appointment_slot(appointment.date_time):
            return False
        if not self.__repository:
            return True
        existing = self.list_appointments_by_date_range(
            appointment.date_time - timedelta(minutes=30),
            appointment.date_time + timedelta(minutes=30)
        )
        for existing_apt in existing:
            if existing_apt.doctor_name == appointment.doctor_name:
                return False
        return True
    
    # Günlük randevu istatistiklerini hesaplar
    def get_daily_statistics(self, date: datetime) -> Dict:
        start_of_day = date.replace(hour=0, minute=0, second=0)
        end_of_day = date.replace(hour=23, minute=59, second=59)
        daily_appointments = self.list_appointments_by_date_range(start_of_day, end_of_day)
        total = len(daily_appointments)
        completed = len([apt for apt in daily_appointments if apt.status == "completed"])
        cancelled = len([apt for apt in daily_appointments if apt.status == "cancelled"])
        scheduled = len([apt for apt in daily_appointments if apt.status == "scheduled"])
        return {
            "date": date.strftime("%d.%m.%Y"),
            "total": total,
            "completed": completed,
            "cancelled": cancelled,
            "scheduled": scheduled,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    # Doktor iş yükü analizini yapar
    def analyze_doctor_workload(self, doctor_name: str, date: datetime) -> Dict:
        start_of_day = date.replace(hour=0, minute=0, second=0)
        end_of_day = date.replace(hour=23, minute=59, second=59)
        appointments = self.list_appointments_by_date_range(start_of_day, end_of_day)
        doctor_appointments = [apt for apt in appointments if apt.doctor_name == doctor_name]
        total_duration = sum(
            getattr(apt, 'estimated_duration', 30) 
            for apt in doctor_appointments
        )
        return {
            "doctor": doctor_name,
            "date": date.strftime("%d.%m.%Y"),
            "total_appointments": len(doctor_appointments),
            "total_duration_minutes": total_duration,
            "average_duration": total_duration / len(doctor_appointments) if doctor_appointments else 0,
            "workload_percentage": (total_duration / 480 * 100)
        }
    
    # Belirli bir hastanın iptal geçmişini döndürür
    def get_cancellation_history(self, patient_id: str) -> int:
        return self.__cancellation_count.get(patient_id, 0)
    
    # Randevu geçmişini döndürür
    def get_appointment_history(self) -> List[Dict]:
        return self.__appointment_history.copy()
    
    # Yaklaşan randevular için hatırlatma gönderir
    def send_reminders_for_upcoming_appointments(self, hours_before: int = 24) -> int:
        if not self.__repository:
            return 0
        now = datetime.now()
        reminder_time = now + timedelta(hours=hours_before)
        appointments = self.list_appointments_by_status("scheduled")
        reminder_count = 0
        for apt in appointments:
            time_until = (apt.date_time - now).total_seconds() / 3600
            if 0 < time_until <= hours_before:
                self.__send_notification(
                    apt.patient_id,
                    f"Hatırlatma: {apt.date_time.strftime('%d.%m.%Y %H:%M')} randevunuz var"
                )
                reminder_count += 1
        return reminder_count
    
    # Randevu tipine göre istatistik üretir
    @staticmethod
    def calculate_appointment_type_distribution(appointments: List[AppointmentBase]) -> Dict:
        distribution = {
            "RoutineAppointment": 0,
            "EmergencyAppointment": 0,
            "OnlineAppointment": 0
        }
        for apt in appointments:
            apt_type = type(apt).__name__
            if apt_type in distribution:
                distribution[apt_type] += 1
        total = len(appointments)
        percentages = {
            k: (v / total * 100) if total > 0 else 0
            for k, v in distribution.items()
        }
        return {
            "counts": distribution,
            "percentages": percentages,
            "total": total
        }
    
    # Randevu başarı oranını hesaplar
    @staticmethod
    def calculate_success_rate(appointments: List[AppointmentBase]) -> float:
        if not appointments:
            return 0.0
        completed = len([apt for apt in appointments if apt.status == "completed"])
        return (completed / len(appointments)) * 100
    
    # En yoğun randevu saatlerini analiz eder
    @classmethod
    def find_peak_appointment_hours(cls, appointments: List[AppointmentBase]) -> List[int]:
        hour_counts = {}
        for apt in appointments:
            hour = apt.date_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        if not hour_counts:
            return []
        max_count = max(hour_counts.values())
        peak_hours = [hour for hour, count in hour_counts.items() if count == max_count]
        return sorted(peak_hours)
    
    # Ortalama randevu süresini hesaplar
    @classmethod
    def calculate_average_appointment_duration(cls, appointments: List[AppointmentBase]) -> float:
        total_duration = 0
        count = 0
        for apt in appointments:
            if hasattr(apt, 'estimated_duration'):
                total_duration += apt.estimated_duration
                count += 1
            elif hasattr(apt, 'meeting_duration_minutes'):
                total_duration += apt.meeting_duration_minutes
                count += 1
            else:
                total_duration += 30
                count += 1
        return total_duration / count if count > 0 else 0
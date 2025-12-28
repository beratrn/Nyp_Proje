from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict


# Randevu sisteminin temel soyut sınıfı, tüm randevu tiplerinin ortak yapısını tanımlar
class AppointmentBase(ABC):
    
    # Randevu nesnesi oluşturur ve temel özellikleri başlatır
    def __init__(
        self,
        appointment_id: str,
        patient_id: str,
        doctor_name: str,
        date_time: datetime,
        status: str = "scheduled"
    ):
        self.__appointment_id = appointment_id
        self.__patient_id = patient_id
        self.__doctor_name = doctor_name
        self.__date_time = date_time
        self.__status = status
        self.__notes = ""
        self.__created_at = datetime.now()
    
    # Randevu ID'sini döndürür
    @property
    def appointment_id(self) -> str:
        return self.__appointment_id
    
    # Randevu ID'sini ayarlar
    @appointment_id.setter
    def appointment_id(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Geçersiz randevu ID")
        self.__appointment_id = value
    
    # Hasta ID'sini döndürür
    @property
    def patient_id(self) -> str:
        return self.__patient_id
    
    # Hasta ID'sini ayarlar
    @patient_id.setter
    def patient_id(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Geçersiz hasta ID")
        self.__patient_id = value
    
    # Doktor adını döndürür
    @property
    def doctor_name(self) -> str:
        return self.__doctor_name
    
    # Doktor adını ayarlar
    @doctor_name.setter
    def doctor_name(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Geçersiz doktor adı")
        self.__doctor_name = value
    
    # Randevu tarih ve saatini döndürür
    @property
    def date_time(self) -> datetime:
        return self.__date_time
    
    # Randevu tarih ve saatini ayarlar
    @date_time.setter
    def date_time(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Geçersiz tarih formatı")
        if value < datetime.now():
            raise ValueError("Randevu tarihi geçmiş olamaz")
        self.__date_time = value
    
    # Randevu durumunu döndürür
    @property
    def status(self) -> str:
        return self.__status
    
    # Randevu durumunu ayarlar
    @status.setter
    def status(self, value: str) -> None:
        valid_statuses = ["scheduled", "completed", "cancelled", "postponed", "in_progress"]
        if value not in valid_statuses:
            raise ValueError(f"Geçersiz durum: {value}")
        self.__status = value
    
    # Randevu notlarını döndürür
    @property
    def notes(self) -> str:
        return self.__notes
    
    # Randevu notlarını ayarlar
    @notes.setter
    def notes(self, value: str) -> None:
        self.__notes = value if value else ""
    
    # Randevu oluşturulma zamanını döndürür
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    # Randevunun detaylı açıklamasını döndürür, alt sınıflar tarafından override edilmelidir
    @abstractmethod
    def get_appointment_details(self) -> str:
        pass
    
    # Randevu maliyetini hesaplar, alt sınıflar kendi fiyatlandırma mantığını uygular
    @abstractmethod
    def calculate_cost(self) -> float:
        pass
    
    # Randevuyu iptal eder ve durumu günceller
    def cancel_appointment(self) -> bool:
        if self.__status in ["completed", "cancelled"]:
            return False
        self.__status = "cancelled"
        return True
    
    # Randevuyu başka bir tarihe erteler
    def postpone_appointment(self, new_date_time: datetime) -> bool:
        if self.__status in ["completed", "cancelled"]:
            return False
        if new_date_time < datetime.now():
            return False
        self.__date_time = new_date_time
        self.__status = "postponed"
        return True
    
    # Randevuyu tamamlanmış olarak işaretler
    def complete_appointment(self) -> bool:
        if self.__status != "scheduled" and self.__status != "in_progress":
            return False
        self.__status = "completed"
        return True
    
    # Randevuya not ekler veya mevcut notu günceller
    def add_notes(self, note: str) -> None:
        if self.__notes:
            self.__notes += f"\n{note}"
        else:
            self.__notes = note
    
    # Randevunun geçerli olup olmadığını kontrol eder
    def is_valid(self) -> bool:
        if not self.__appointment_id or not self.__patient_id or not self.__doctor_name:
            return False
        if self.__date_time < datetime.now() and self.__status == "scheduled":
            return False
        return True
    
    # Randevunun iptal edilebilir olup olmadığını kontrol eder
    def can_be_cancelled(self) -> bool:
        if self.__status in ["completed", "cancelled"]:
            return False
        time_until_appointment = (self.__date_time - datetime.now()).total_seconds() / 3600
        if time_until_appointment < 2:
            return False
        return True
    
    # Randevunun başlamasına kalan süreyi saat cinsinden döndürür
    def get_time_until_appointment(self) -> float:
        delta = self.__date_time - datetime.now()
        return delta.total_seconds() / 3600
    
    # Randevu nesnesinin string temsilini döndürür
    def __str__(self) -> str:
        return f"Randevu ID: {self.__appointment_id}, Hasta: {self.__patient_id}, Doktor: {self.__doctor_name}, Tarih: {self.__date_time.strftime('%Y-%m-%d %H:%M')}, Durum: {self.__status}"
    
    # Randevu nesnesinin detaylı temsilini döndürür
    def __repr__(self) -> str:
        return f"AppointmentBase(id={self.__appointment_id}, patient={self.__patient_id}, doctor={self.__doctor_name}, date={self.__date_time}, status={self.__status})"
    
    # İki randevu nesnesinin eşitliğini kontrol eder
    def __eq__(self, other) -> bool:
        if not isinstance(other, AppointmentBase):
            return False
        return self.__appointment_id == other.__appointment_id
    
    # Randevu nesnesinin hash değerini döndürür
    def __hash__(self) -> int:
        return hash(self.__appointment_id)
    
    # Verilen durum için geçerli durum geçişlerini döndürür
    @staticmethod
    def get_valid_status_transitions(current_status: str) -> List[str]:
        transitions = {
            "scheduled": ["in_progress", "cancelled", "postponed"],
            "in_progress": ["completed", "cancelled"],
            "completed": [],
            "cancelled": [],
            "postponed": ["scheduled", "cancelled"]
        }
        return transitions.get(current_status, [])
    
    # Randevu önceliğini durum ve tarihe göre hesaplar
    @staticmethod
    def calculate_priority(status: str, date_time: datetime) -> int:
        priority_map = {
            "scheduled": 1,
            "in_progress": 0,
            "postponed": 2,
            "cancelled": 5,
            "completed": 5
        }
        base_priority = priority_map.get(status, 3)
        hours_until = (date_time - datetime.now()).total_seconds() / 3600
        if hours_until < 24:
            base_priority -= 1
        if hours_until < 2:
            base_priority -= 2
        return max(0, base_priority)
    
    # İki tarih arasında çakışma olup olmadığını kontrol eder
    @staticmethod
    def check_time_conflict(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        return not (end1 <= start2 or end2 <= start1)
    
    # Verilen tarih için randevu slot'u uygun mu kontrol eder
    @staticmethod
    def is_valid_appointment_slot(appointment_date: datetime) -> bool:
        if appointment_date.weekday() > 4:
            return False
        if appointment_date.hour < 8 or appointment_date.hour >= 18:
            return False
        return True
    
    # Belirtilen doktor ve tarih için çalışma saati içinde mi kontrol eder
    @classmethod
    def validate_doctor_schedule(cls, doctor_name: str, date_time: datetime) -> bool:
        if date_time.hour < 9 or date_time.hour > 17:
            return False
        if date_time.minute not in [0, 30]:
            return False
        return True
    
    # Belirli bir zaman aralığında kaç randevu olabileceğini hesaplar
    @classmethod
    def calculate_max_appointments_in_period(
        cls,
        start_date: datetime,
        end_date: datetime,
        slot_duration_minutes: int = 30
    ) -> int:
        total_hours = (end_date - start_date).total_seconds() / 3600
        working_days = 0
        current = start_date
        while current < end_date:
            if current.weekday() < 5:
                working_days += 1
            current = current.replace(day=current.day + 1)
        working_hours_per_day = 9
        total_working_hours = working_days * working_hours_per_day
        slots_per_hour = 60 / slot_duration_minutes
        return int(total_working_hours * slots_per_hour)
    
    # Randevu bilgilerini sözlük formatında döndürür
    @classmethod
    def create_appointment_dict(
        cls,
        appointment_id: str,
        patient_id: str,
        doctor_name: str,
        date_time: datetime,
        status: str
    ) -> Dict:
        return {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "doctor_name": doctor_name,
            "date_time": date_time.isoformat(),
            "status": status,
            "created_at": datetime.now().isoformat()
        }
    
    # Sözlük formatındaki randevu verisini doğrular
    @classmethod
    def validate_appointment_data(cls, data: Dict) -> bool:
        required_fields = ["appointment_id", "patient_id", "doctor_name", "date_time", "status"]
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        return True
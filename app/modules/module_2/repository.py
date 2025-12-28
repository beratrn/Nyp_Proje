from datetime import datetime
from typing import List, Optional, Dict
from base import AppointmentBase
import json
import os


# Bellek tabanlı randevu repository sınıfı, verileri RAM'de tutar
class InMemoryAppointmentRepository:
    
    # Repository nesnesini başlatır ve boş veri yapıları oluşturur
    def __init__(self):
        self.__appointments = {}
        self.__index_by_patient = {}
        self.__index_by_doctor = {}
        self.__index_by_status = {}
        self.__total_records = 0
    
    # Toplam kayıt sayısını döndürür
    @property
    def total_records(self) -> int:
        return self.__total_records
    
    # Tüm randevuları döndürür
    def get_all_appointments(self) -> Dict:
        return self.__appointments.copy()
    
    # Randevuyu kaydeder ve indeksleri günceller
    def save(self, appointment: AppointmentBase) -> bool:
        if not appointment or not appointment.appointment_id:
            return False
        self.__appointments[appointment.appointment_id] = appointment
        self.__update_indexes(appointment)
        self.__total_records = len(self.__appointments)
        return True
    
    # ID'ye göre randevu arar ve döndürür
    def find_by_id(self, appointment_id: str) -> Optional[AppointmentBase]:
        return self.__appointments.get(appointment_id)
    
    # Hasta ID'sine göre randevuları listeler
    def find_by_patient(self, patient_id: str) -> List[AppointmentBase]:
        appointment_ids = self.__index_by_patient.get(patient_id, [])
        return [self.__appointments[aid] for aid in appointment_ids if aid in self.__appointments]
    
    # Doktor adına göre randevuları listeler
    def find_by_doctor(self, doctor_name: str) -> List[AppointmentBase]:
        appointment_ids = self.__index_by_doctor.get(doctor_name, [])
        return [self.__appointments[aid] for aid in appointment_ids if aid in self.__appointments]
    
    # Duruma göre randevuları listeler
    def find_by_status(self, status: str) -> List[AppointmentBase]:
        appointment_ids = self.__index_by_status.get(status, [])
        return [self.__appointments[aid] for aid in appointment_ids if aid in self.__appointments]
    
    # Tarih aralığına göre randevuları filtreler
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AppointmentBase]:
        result = []
        for appointment in self.__appointments.values():
            if start_date <= appointment.date_time <= end_date:
                result.append(appointment)
        return result
    
    # Randevuyu günceller ve indeksleri yeniden oluşturur
    def update(self, appointment: AppointmentBase) -> bool:
        if appointment.appointment_id not in self.__appointments:
            return False
        old_appointment = self.__appointments[appointment.appointment_id]
        self.__remove_from_indexes(old_appointment)
        self.__appointments[appointment.appointment_id] = appointment
        self.__update_indexes(appointment)
        return True
    
    # Randevuyu siler ve indekslerden kaldırır
    def delete(self, appointment_id: str) -> bool:
        if appointment_id not in self.__appointments:
            return False
        appointment = self.__appointments[appointment_id]
        self.__remove_from_indexes(appointment)
        del self.__appointments[appointment_id]
        self.__total_records = len(self.__appointments)
        return True
    
    # Tüm randevuları listeler
    def list_all(self) -> List[AppointmentBase]:
        return list(self.__appointments.values())
    
    # Belirli bir sayıda randevu döndürür
    def list_with_limit(self, limit: int) -> List[AppointmentBase]:
        return list(self.__appointments.values())[:limit]
    
    # Tüm verileri temizler
    def clear_all(self) -> None:
        self.__appointments.clear()
        self.__index_by_patient.clear()
        self.__index_by_doctor.clear()
        self.__index_by_status.clear()
        self.__total_records = 0
    
    # Randevu indekslerini günceller
    def __update_indexes(self, appointment: AppointmentBase) -> None:
        apt_id = appointment.appointment_id
        if appointment.patient_id not in self.__index_by_patient:
            self.__index_by_patient[appointment.patient_id] = []
        if apt_id not in self.__index_by_patient[appointment.patient_id]:
            self.__index_by_patient[appointment.patient_id].append(apt_id)
        if appointment.doctor_name not in self.__index_by_doctor:
            self.__index_by_doctor[appointment.doctor_name] = []
        if apt_id not in self.__index_by_doctor[appointment.doctor_name]:
            self.__index_by_doctor[appointment.doctor_name].append(apt_id)
        if appointment.status not in self.__index_by_status:
            self.__index_by_status[appointment.status] = []
        if apt_id not in self.__index_by_status[appointment.status]:
            self.__index_by_status[appointment.status].append(apt_id)
    
    # Randevuyu indekslerden kaldırır
    def __remove_from_indexes(self, appointment: AppointmentBase) -> None:
        apt_id = appointment.appointment_id
        if appointment.patient_id in self.__index_by_patient:
            if apt_id in self.__index_by_patient[appointment.patient_id]:
                self.__index_by_patient[appointment.patient_id].remove(apt_id)
        if appointment.doctor_name in self.__index_by_doctor:
            if apt_id in self.__index_by_doctor[appointment.doctor_name]:
                self.__index_by_doctor[appointment.doctor_name].remove(apt_id)
        if appointment.status in self.__index_by_status:
            if apt_id in self.__index_by_status[appointment.status]:
                self.__index_by_status[appointment.status].remove(apt_id)
    
    # Repository istatistiklerini döndürür
    def get_statistics(self) -> Dict:
        return {
            "total_appointments": self.__total_records,
            "unique_patients": len(self.__index_by_patient),
            "unique_doctors": len(self.__index_by_doctor),
            "status_breakdown": {
                status: len(ids) for status, ids in self.__index_by_status.items()
            }
        }
    
    # Randevu var mı kontrol eder
    def exists(self, appointment_id: str) -> bool:
        return appointment_id in self.__appointments
    
    # Toplu kayıt yapar
    def save_batch(self, appointments: List[AppointmentBase]) -> int:
        success_count = 0
        for appointment in appointments:
            if self.save(appointment):
                success_count += 1
        return success_count
    
    # Repository'nin boş olup olmadığını kontrol eder
    @staticmethod
    def is_empty_repository(repo) -> bool:
        return repo.total_records == 0
    
    # Verilen listedeki randevuları tarih sırasına göre sıralar
    @staticmethod
    def sort_by_date(appointments: List[AppointmentBase], ascending: bool = True) -> List[AppointmentBase]:
        return sorted(appointments, key=lambda x: x.date_time, reverse=not ascending)
    
    # Belirli bir tarihteki randevuları sayar
    @classmethod
    def count_appointments_on_date(cls, appointments: List[AppointmentBase], target_date: datetime) -> int:
        count = 0
        for apt in appointments:
            if apt.date_time.date() == target_date.date():
                count += 1
        return count
    
    # Randevuları duruma göre gruplar
    @classmethod
    def group_by_status(cls, appointments: List[AppointmentBase]) -> Dict[str, List[AppointmentBase]]:
        grouped = {}
        for apt in appointments:
            if apt.status not in grouped:
                grouped[apt.status] = []
            grouped[apt.status].append(apt)
        return grouped


# JSON dosya tabanlı randevu repository sınıfı, verileri dosyada saklar
class FileBasedAppointmentRepository:
    
    # Repository nesnesini başlatır ve dosya yolunu ayarlar
    def __init__(self, file_path: str = "appointments.json"):
        self.__file_path = file_path
        self.__appointments = {}
        self.__load_from_file()
    
    # Dosya yolunu döndürür
    @property
    def file_path(self) -> str:
        return self.__file_path
    
    # Toplam kayıt sayısını döndürür
    @property
    def total_records(self) -> int:
        return len(self.__appointments)
    
    # Dosyadan verileri yükler
    def __load_from_file(self) -> None:
        if os.path.exists(self.__file_path):
            try:
                with open(self.__file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.__appointments = data
            except Exception as e:
                self.__appointments = {}
    
    # Verileri dosyaya kaydeder
    def __save_to_file(self) -> bool:
        try:
            with open(self.__file_path, 'w', encoding='utf-8') as f:
                json.dump(self.__appointments, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            return False
    
    # Randevuyu sözlük formatına dönüştürür
    def __appointment_to_dict(self, appointment: AppointmentBase) -> Dict:
        return {
            "appointment_id": appointment.appointment_id,
            "patient_id": appointment.patient_id,
            "doctor_name": appointment.doctor_name,
            "date_time": appointment.date_time.isoformat(),
            "status": appointment.status,
            "notes": appointment.notes,
            "type": type(appointment).__name__
        }
    
    # Randevuyu kaydeder ve dosyaya yazar
    def save(self, appointment: AppointmentBase) -> bool:
        if not appointment or not appointment.appointment_id:
            return False
        self.__appointments[appointment.appointment_id] = self.__appointment_to_dict(appointment)
        return self.__save_to_file()
    
    # ID'ye göre randevu arar
    def find_by_id(self, appointment_id: str) -> Optional[Dict]:
        return self.__appointments.get(appointment_id)
    
    # Hasta ID'sine göre randevuları listeler
    def find_by_patient(self, patient_id: str) -> List[Dict]:
        result = []
        for apt in self.__appointments.values():
            if apt.get("patient_id") == patient_id:
                result.append(apt)
        return result
    
    # Doktor adına göre randevuları listeler
    def find_by_doctor(self, doctor_name: str) -> List[Dict]:
        result = []
        for apt in self.__appointments.values():
            if apt.get("doctor_name") == doctor_name:
                result.append(apt)
        return result
    
    # Duruma göre randevuları listeler
    def find_by_status(self, status: str) -> List[Dict]:
        result = []
        for apt in self.__appointments.values():
            if apt.get("status") == status:
                result.append(apt)
        return result
    
    # Randevuyu günceller
    def update(self, appointment: AppointmentBase) -> bool:
        if appointment.appointment_id not in self.__appointments:
            return False
        self.__appointments[appointment.appointment_id] = self.__appointment_to_dict(appointment)
        return self.__save_to_file()
    
    # Randevuyu siler
    def delete(self, appointment_id: str) -> bool:
        if appointment_id not in self.__appointments:
            return False
        del self.__appointments[appointment_id]
        return self.__save_to_file()
    
    # Tüm randevuları listeler
    def list_all(self) -> List[Dict]:
        return list(self.__appointments.values())
    
    # Tüm verileri temizler
    def clear_all(self) -> None:
        self.__appointments.clear()
        self.__save_to_file()
    
    # Repository istatistiklerini döndürür
    def get_statistics(self) -> Dict:
        patients = set()
        doctors = set()
        status_count = {}
        for apt in self.__appointments.values():
            patients.add(apt.get("patient_id"))
            doctors.add(apt.get("doctor_name"))
            status = apt.get("status", "unknown")
            status_count[status] = status_count.get(status, 0) + 1
        return {
            "total_appointments": len(self.__appointments),
            "unique_patients": len(patients),
            "unique_doctors": len(doctors),
            "status_breakdown": status_count,
            "file_path": self.__file_path
        }
    
    # Dosyayı yedekler
    def backup(self, backup_path: str) -> bool:
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.__appointments, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    # Yedekten geri yükler
    def restore(self, backup_path: str) -> bool:
        if not os.path.exists(backup_path):
            return False
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                self.__appointments = json.load(f)
            return self.__save_to_file()
        except Exception:
            return False
    
    # Dosya boyutunu byte cinsinden döndürür
    @staticmethod
    def get_file_size(file_path: str) -> int:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    # Belirtilen yolda dosya var mı kontrol eder
    @staticmethod
    def file_exists(file_path: str) -> bool:
        return os.path.exists(file_path)
    
    # JSON dosyasını doğrular
    @classmethod
    def validate_json_file(cls, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except Exception:
            return False
    
    # İki repository'yi birleştirir
    @classmethod
    def merge_repositories(cls, repo1, repo2) -> Dict:
        merged = {}
        merged.update(repo1.get_all_appointments() if hasattr(repo1, 'get_all_appointments') else repo1._FileBasedAppointmentRepository__appointments)
        merged.update(repo2.get_all_appointments() if hasattr(repo2, 'get_all_appointments') else repo2._FileBasedAppointmentRepository__appointments)
        return merged
"""
Hasta Yönetim Modülü - Repository Katmanı
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import json
from base import Patient
from implementations import Inpatient, Outpatient, EmergencyPatient


class PatientRepository:
    """
    Hasta verilerini yöneten repository sınıfı (In-Memory)
    """
    
    def __init__(self):
        self._patients: Dict[str, Patient] = {}
        self._index_by_name: Dict[str, List[str]] = {}
        self._index_by_status: Dict[str, List[str]] = {}
        self._index_by_type: Dict[str, List[str]] = {}
        self._transaction_log: List[Dict] = []
    
    def save(self, patient: Patient) -> bool:
        """
        Hasta kaydeder
        """
        try:
            self._patients[patient.id] = patient
            self._update_indexes(patient)
            self._log_transaction("save", patient.id, "Patient saved successfully")
            return True
        except Exception as e:
            self._log_transaction("save", patient.id, f"Failed to save patient: {str(e)}")
            return False
    
    def update(self, patient: Patient) -> bool:
        """
        Hasta bilgilerini günceller
        """
        if patient.id not in self._patients:
            return False
        
        try:
            self._remove_from_indexes(patient.id)
            self._patients[patient.id] = patient
            self._update_indexes(patient)
            self._log_transaction("update", patient.id, "Patient updated successfully")
            return True
        except Exception as e:
            self._log_transaction("update", patient.id, f"Failed to update patient: {str(e)}")
            return False
    
    def delete(self, patient_id: str) -> bool:
        """
        Hasta siler
        """
        if patient_id not in self._patients:
            return False
        
        try:
            self._remove_from_indexes(patient_id)
            del self._patients[patient_id]
            self._log_transaction("delete", patient_id, "Patient deleted successfully")
            return True
        except Exception as e:
            self._log_transaction("delete", patient_id, f"Failed to delete patient: {str(e)}")
            return False
    
    def find_by_id(self, patient_id: str) -> Optional[Patient]:
        """
        ID ile hasta bulur
        """
        return self._patients.get(patient_id)
    
    def find_by_name(self, name: str) -> List[Patient]:
        """
        İsme göre hasta bulur
        """
        patient_ids = self._index_by_name.get(name.lower(), [])
        return [self._patients[pid] for pid in patient_ids if pid in self._patients]
    
    def find_by_status(self, status: str) -> List[Patient]:
        """
        Duruma göre hasta bulur
        """
        patient_ids = self._index_by_status.get(status, [])
        return [self._patients[pid] for pid in patient_ids if pid in self._patients]
    
    def find_by_type(self, patient_type: str) -> List[Patient]:
        """
        Tipe göre hasta bulur
        """
        patient_ids = self._index_by_type.get(patient_type, [])
        return [self._patients[pid] for pid in patient_ids if pid in self._patients]
    
    def get_all(self) -> List[Patient]:
        """
        Tüm hastaları döndürür
        """
        return list(self._patients.values())
    
    def count(self) -> int:
        """
        Toplam hasta sayısını döndürür
        """
        return len(self._patients)
    
    def exists(self, patient_id: str) -> bool:
        """
        Hastanın var olup olmadığını kontrol eder
        """
        return patient_id in self._patients
    
    def find_by_age_range(self, min_age: int, max_age: int) -> List[Patient]:
        """
        Yaş aralığına göre hasta bulur
        """
        return [p for p in self._patients.values() if min_age <= p.age <= max_age]
    
    def find_by_gender(self, gender: str) -> List[Patient]:
        """
        Cinsiyete göre hasta bulur
        """
        return [p for p in self._patients.values() if p.gender == gender]
    
    def find_critical_patients(self) -> List[Patient]:
        """
        Kritik durumdaki hastaları bulur
        """
        return self.find_by_status("critical")
    
    def find_active_patients(self) -> List[Patient]:
        """
        Aktif hastaları bulur
        """
        return self.find_by_status("active")
    
    def find_discharged_patients(self) -> List[Patient]:
        """
        Taburcu edilmiş hastaları bulur
        """
        return self.find_by_status("discharged")
    
    def search(self, query: str) -> List[Patient]:
        """
        Genel arama yapar
        """
        query_lower = query.lower()
        results = []
        
        for patient in self._patients.values():
            if (query_lower in patient.name.lower() or
                query_lower in patient.id.lower() or
                query_lower in patient.status.lower()):
                results.append(patient)
        
        return results
    
    def filter_by_criteria(self, filter_func: Callable[[Patient], bool]) -> List[Patient]:
        """
        Özel kriterlere göre filtreler
        """
        return [p for p in self._patients.values() if filter_func(p)]
    
    def get_statistics(self) -> Dict:
        """
        İstatistikleri döndürür
        """
        all_patients = self.get_all()
        
        if not all_patients:
            return {
                "total_patients": 0,
                "by_type": {},
                "by_status": {},
                "by_gender": {},
                "average_age": 0.0
            }
        
        stats = {
            "total_patients": len(all_patients),
            "by_type": {
                "inpatient": len([p for p in all_patients if isinstance(p, Inpatient)]),
                "outpatient": len([p for p in all_patients if isinstance(p, Outpatient)]),
                "emergency": len([p for p in all_patients if isinstance(p, EmergencyPatient)])
            },
            "by_status": {},
            "by_gender": {},
            "average_age": sum(p.age for p in all_patients) / len(all_patients)
        }
        
        for patient in all_patients:
            stats["by_status"][patient.status] = stats["by_status"].get(patient.status, 0) + 1
            stats["by_gender"][patient.gender] = stats["by_gender"].get(patient.gender, 0) + 1
        
        return stats
    
    def bulk_save(self, patients: List[Patient]) -> Dict[str, int]:
        """
        Toplu kayıt yapar
        """
        success_count = 0
        failed_count = 0
        
        for patient in patients:
            if self.save(patient):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(patients)
        }
    
    def bulk_update(self, patients: List[Patient]) -> Dict[str, int]:
        """
        Toplu güncelleme yapar
        """
        success_count = 0
        failed_count = 0
        
        for patient in patients:
            if self.update(patient):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(patients)
        }
    
    def bulk_delete(self, patient_ids: List[str]) -> Dict[str, int]:
        """
        Toplu silme yapar
        """
        success_count = 0
        failed_count = 0
        
        for patient_id in patient_ids:
            if self.delete(patient_id):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(patient_ids)
        }
    
    def clear_all(self) -> None:
        """
        Tüm hastaları temizler
        """
        self._patients.clear()
        self._index_by_name.clear()
        self._index_by_status.clear()
        self._index_by_type.clear()
        self._log_transaction("clear", "all", "All patients cleared")
    
    def export_to_dict(self) -> List[Dict]:
        """
        Tüm hastaları dictionary listesi olarak export eder
        """
        exported_data = []
        
        for patient in self._patients.values():
            patient_dict = patient.get_patient_info()
            
            if isinstance(patient, Inpatient):
                patient_dict.update({
                    "type": "inpatient",
                    "room_number": patient.room_number,
                    "ward": patient.ward,
                    "admission_reason": patient.admission_reason
                })
            elif isinstance(patient, Outpatient):
                patient_dict.update({
                    "type": "outpatient",
                    "visit_reason": patient.visit_reason,
                    "department": patient.department
                })
            elif isinstance(patient, EmergencyPatient):
                patient_dict.update({
                    "type": "emergency",
                    "emergency_type": patient.emergency_type,
                    "severity_level": patient.severity_level
                })
            
            exported_data.append(patient_dict)
        
        return exported_data
    
    def get_transaction_log(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Transaction logunu döndürür
        """
        if limit:
            return self._transaction_log[-limit:]
        return self._transaction_log
    
    def clear_transaction_log(self) -> None:
        """
        Transaction logunu temizler
        """
        self._transaction_log.clear()
    
    def _update_indexes(self, patient: Patient) -> None:
        """
        İndeksleri günceller
        """
        name_key = patient.name.lower()
        if name_key not in self._index_by_name:
            self._index_by_name[name_key] = []
        if patient.id not in self._index_by_name[name_key]:
            self._index_by_name[name_key].append(patient.id)
        
        if patient.status not in self._index_by_status:
            self._index_by_status[patient.status] = []
        if patient.id not in self._index_by_status[patient.status]:
            self._index_by_status[patient.status].append(patient.id)
        
        patient_type = patient.get_admission_type().lower()
        if patient_type not in self._index_by_type:
            self._index_by_type[patient_type] = []
        if patient.id not in self._index_by_type[patient_type]:
            self._index_by_type[patient_type].append(patient.id)
    
    def _remove_from_indexes(self, patient_id: str) -> None:
        """
        İndekslerden kaldırır
        """
        patient = self._patients.get(patient_id)
        if not patient:
            return
        
        name_key = patient.name.lower()
        if name_key in self._index_by_name and patient_id in self._index_by_name[name_key]:
            self._index_by_name[name_key].remove(patient_id)
            if not self._index_by_name[name_key]:
                del self._index_by_name[name_key]
        
        if patient.status in self._index_by_status and patient_id in self._index_by_status[patient.status]:
            self._index_by_status[patient.status].remove(patient_id)
            if not self._index_by_status[patient.status]:
                del self._index_by_status[patient.status]
        
        patient_type = patient.get_admission_type().lower()
        if patient_type in self._index_by_type and patient_id in self._index_by_type[patient_type]:
            self._index_by_type[patient_type].remove(patient_id)
            if not self._index_by_type[patient_type]:
                del self._index_by_type[patient_type]
    
    def _log_transaction(self, operation: str, patient_id: str, message: str) -> None:
        """
        Transaction loglar
        """
        log_entry = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "operation": operation,
            "patient_id": patient_id,
            "message": message
        }
        self._transaction_log.append(log_entry)
    
    @staticmethod
    def validate_patient_data(patient_dict: Dict) -> bool:
        """
        Hasta verisini validate eder
        """
        required_fields = ["name", "age", "gender"]
        
        for field in required_fields:
            if field not in patient_dict:
                return False
        
        if not isinstance(patient_dict["age"], int) or patient_dict["age"] < 0:
            return False
        
        if patient_dict["gender"] not in ["male", "female", "other"]:
            return False
        
        return True
    
    @classmethod
    def create_repository_with_sample_data(cls):
        """
        Örnek verilerle repository oluşturur
        """
        repository = cls()
        
        sample_inpatients = [
            Inpatient("Ahmet Yılmaz", 45, "male", "101", "Cardiology", "Heart attack"),
            Inpatient("Ayşe Demir", 62, "female", "205", "Neurology", "Stroke"),
            Inpatient("Mehmet Kaya", 38, "male", "310", "Orthopedics", "Fracture")
        ]
        
        sample_outpatients = [
            Outpatient("Fatma Şahin", 28, "female", "Regular checkup"),
            Outpatient("Ali Çelik", 55, "male", "Diabetes consultation"),
            Outpatient("Zeynep Arslan", 33, "female", "Pregnancy checkup")
        ]
        
        sample_emergency = [
            EmergencyPatient("Hasan Öztürk", 72, "male", "Cardiac arrest", 1),
            EmergencyPatient("Elif Yıldız", 19, "female", "Traffic accident", 2),
            EmergencyPatient("Can Aydın", 8, "male", "Severe allergic reaction", 3)
        ]
        
        for patient in sample_inpatients + sample_outpatients + sample_emergency:
            repository.save(patient)
        
        return repository
    
    def __len__(self) -> int:
        """
        Repository'deki hasta sayısını döndürür
        """
        return len(self._patients)
    
    def __contains__(self, patient_id: str) -> bool:
        """
        Hastanın repository'de olup olmadığını kontrol eder
        """
        return patient_id in self._patients
    
    def __iter__(self):
        """
        Iterator
        """
        return iter(self._patients.values())
    
    def __repr__(self) -> str:
        """
        Repr representation
        """
        return f"PatientRepository(patients={len(self._patients)})"


class FileBasedPatientRepository(PatientRepository):
    """
    Dosya tabanlı hasta repository sınıfı
    """
    
    def __init__(self, file_path: str = "patients_data.json"):
        super().__init__()
        self.file_path = file_path
        self._load_from_file()
    
    def save(self, patient: Patient) -> bool:
        """
        Hasta kaydeder ve dosyaya yazar
        """
        result = super().save(patient)
        if result:
            self._save_to_file()
        return result
    
    def update(self, patient: Patient) -> bool:
        """
        Hasta günceller ve dosyaya yazar
        """
        result = super().update(patient)
        if result:
            self._save_to_file()
        return result
    
    def delete(self, patient_id: str) -> bool:
        """
        Hasta siler ve dosyaya yazar
        """
        result = super().delete(patient_id)
        if result:
            self._save_to_file()
        return result
    
    def _save_to_file(self) -> None:
        """
        Verileri dosyaya kaydeder
        """
        try:
            data = self.export_to_dict()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    def _load_from_file(self) -> None:
        """
        Dosyadan verileri yükler
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for patient_dict in data:
                patient_type = patient_dict.get('type', 'outpatient')
                
                if patient_type == 'inpatient':
                    patient = Inpatient(
                        name=patient_dict['name'],
                        age=patient_dict['age'],
                        gender=patient_dict['gender'],
                        room_number=patient_dict.get('room_number', '000'),
                        ward=patient_dict.get('ward', 'General'),
                        admission_reason=patient_dict.get('admission_reason', 'Unknown'),
                        status=patient_dict.get('status', 'active')
                    )
                elif patient_type == 'emergency':
                    patient = EmergencyPatient(
                        name=patient_dict['name'],
                        age=patient_dict['age'],
                        gender=patient_dict['gender'],
                        emergency_type=patient_dict.get('emergency_type', 'Unknown'),
                        severity_level=patient_dict.get('severity_level', 5),
                        status=patient_dict.get('status', 'critical')
                    )
                else:
                    patient = Outpatient(
                        name=patient_dict['name'],
                        age=patient_dict['age'],
                        gender=patient_dict['gender'],
                        visit_reason=patient_dict.get('visit_reason', 'Checkup'),
                        status=patient_dict.get('status', 'active')
                    )
                
                patient.id = patient_dict['id']
                super().save(patient)
                
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading from file: {e}")


class CachedPatientRepository(PatientRepository):
    """
    Cache özellikli hasta repository sınıfı
    """
    
    def __init__(self, cache_size: int = 100):
        super().__init__()
        self.cache_size = cache_size
        self._cache: Dict[str, Patient] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def find_by_id(self, patient_id: str) -> Optional[Patient]:
        """
        ID ile hasta bulur (cache kullanarak)
        """
        if patient_id in self._cache:
            self._cache_hits += 1
            return self._cache[patient_id]
        
        self._cache_misses += 1
        patient = super().find_by_id(patient_id)
        
        if patient:
            self._add_to_cache(patient_id, patient)
        
        return patient
    
    def _add_to_cache(self, patient_id: str, patient: Patient) -> None:
        """
        Cache'e ekler
        """
        if len(self._cache) >= self.cache_size:
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        self._cache[patient_id] = patient
    
    def clear_cache(self) -> None:
        """
        Cache'i temizler
        """
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_cache_stats(self) -> Dict:
        """
        Cache istatistiklerini döndürür
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.cache_size,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": round(hit_rate, 2)
        }
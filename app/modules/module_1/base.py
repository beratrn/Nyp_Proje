"""
Hasta Yönetim Modülü - Base Sınıf Tanımlamaları
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class Patient(ABC):
    """
    Tüm hasta tiplerinin türeyeceği soyut base sınıf
    """
    
    def __init__(self, name: str, age: int, gender: str, status: str = "active"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.gender = gender
        self.status = status
        self.registration_date = datetime.now()
        self.medical_history: List[str] = []
        self.allergies: List[str] = []
        self.emergency_contact: Optional[Dict[str, str]] = None
        self.blood_type: Optional[str] = None
        self.insurance_number: Optional[str] = None
    
    @abstractmethod
    def calculate_treatment_priority(self) -> int:
        """
        Hastanın tedavi önceliğini hesaplar
        """
        pass
    
    @abstractmethod
    def get_admission_type(self) -> str:
        """
        Hastanın kabul tipini döndürür
        """
        pass
    
    @abstractmethod
    def calculate_daily_cost(self) -> float:
        """
        Günlük tedavi maliyetini hesaplar
        """
        pass
    
    def add_medical_history(self, record: str) -> None:
        """
        Tıbbi geçmişe kayıt ekler
        """
        self.medical_history.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {record}")
    
    def add_allergy(self, allergy: str) -> None:
        """
        Alerji bilgisi ekler
        """
        if allergy not in self.allergies:
            self.allergies.append(allergy)
    
    def set_blood_type(self, blood_type: str) -> None:
        """
        Kan grubu ayarlar
        """
        valid_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if blood_type in valid_types:
            self.blood_type = blood_type
        else:
            raise ValueError(f"Invalid blood type: {blood_type}")
    
    def set_emergency_contact(self, name: str, phone: str, relation: str) -> None:
        """
        Acil durum iletişim bilgisi ayarlar
        """
        self.emergency_contact = {
            "name": name,
            "phone": phone,
            "relation": relation
        }
    
    def update_status(self, new_status: str) -> None:
        """
        Hasta durumunu günceller
        """
        valid_statuses = ["active", "discharged", "transferred", "deceased", "critical"]
        if new_status in valid_statuses:
            old_status = self.status
            self.status = new_status
            self.add_medical_history(f"Status changed from {old_status} to {new_status}")
        else:
            raise ValueError(f"Invalid status: {new_status}")
    
    def get_age_category(self) -> str:
        """
        Yaş kategorisini döndürür
        """
        if self.age < 1:
            return "newborn"
        elif self.age < 12:
            return "child"
        elif self.age < 18:
            return "adolescent"
        elif self.age < 65:
            return "adult"
        else:
            return "elderly"
    
    def is_critical(self) -> bool:
        """
        Hastanın kritik durumda olup olmadığını kontrol eder
        """
        return self.status == "critical"
    
    def get_patient_info(self) -> Dict:
        """
        Hasta bilgilerini dictionary olarak döndürür
        """
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "status": self.status,
            "registration_date": self.registration_date.strftime('%Y-%m-%d %H:%M:%S'),
            "blood_type": self.blood_type,
            "allergies": self.allergies,
            "medical_history_count": len(self.medical_history),
            "admission_type": self.get_admission_type(),
            "treatment_priority": self.calculate_treatment_priority(),
            "age_category": self.get_age_category()
        }
    
    @classmethod
    def create_patient_from_dict(cls, data: Dict):
        """
        Dictionary'den hasta nesnesi oluşturur
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    @classmethod
    def validate_patient_data(cls, name: str, age: int, gender: str) -> bool:
        """
        Hasta verisini validate eder
        """
        if not name or not isinstance(name, str):
            return False
        if not isinstance(age, int) or age < 0 or age > 150:
            return False
        if gender not in ["male", "female", "other"]:
            return False
        return True
    
    @staticmethod
    def calculate_bmi(weight: float, height: float) -> float:
        """
        BMI (Vücut Kitle İndeksi) hesaplar
        """
        if height <= 0:
            raise ValueError("Height must be positive")
        return round(weight / ((height / 100) ** 2), 2)
    
    @staticmethod
    def format_patient_id(patient_id: str) -> str:
        """
        Hasta ID'sini formatlar
        """
        return f"PT-{patient_id[:8].upper()}"
    
    @staticmethod
    def get_blood_type_compatibility(blood_type: str) -> List[str]:
        """
        Kan grubu uyumluluğunu döndürür
        """
        compatibility_map = {
            "A+": ["A+", "A-", "O+", "O-"],
            "A-": ["A-", "O-"],
            "B+": ["B+", "B-", "O+", "O-"],
            "B-": ["B-", "O-"],
            "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            "AB-": ["A-", "B-", "AB-", "O-"],
            "O+": ["O+", "O-"],
            "O-": ["O-"]
        }
        return compatibility_map.get(blood_type, [])
    
    def __str__(self) -> str:
        """
        String representation
        """
        return f"{self.get_admission_type()}: {self.name} (ID: {self.format_patient_id(self.id)})"
    
    def __repr__(self) -> str:
        """
        Repr representation
        """
        return f"Patient(id={self.id}, name={self.name}, age={self.age}, status={self.status})"
    
    def __eq__(self, other) -> bool:
        """
        Eşitlik kontrolü
        """
        if not isinstance(other, Patient):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """
        Hash değeri
        """
        return hash(self.id)
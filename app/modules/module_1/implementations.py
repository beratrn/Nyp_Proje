"""
Hasta Yönetim Modülü - Implementation Sınıfları
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random
from app.modules.module_1.base import Patient


class Inpatient(Patient):
    """
    Yatan hasta sınıfı
    """
    
    def __init__(self, name: str, age: int, gender: str, room_number: str, 
                 ward: str, admission_reason: str, status: str = "active"):
        super().__init__(name, age, gender, status)
        self.room_number = room_number
        self.ward = ward
        self.admission_reason = admission_reason
        self.admission_date = datetime.now()
        self.discharge_date: Optional[datetime] = None
        self.attending_physician: Optional[str] = None
        self.nurse_assigned: Optional[str] = None
        self.bed_type: str = "standard"
        self.meal_preferences: List[str] = []
        self.visitor_restrictions: bool = False
        self.estimated_stay_days: int = 0
        self.daily_notes: List[str] = []
        self.medications: List[Dict] = []
        self.vital_signs_history: List[Dict] = []
    
    def calculate_treatment_priority(self) -> int:
        """
        Yatan hasta için tedavi önceliğini hesaplar
        """
        priority = 5
        
        if self.is_critical():
            priority = 10
        elif self.age > 70 or self.age < 5:
            priority = 8
        elif self.ward.lower() in ["icu", "intensive care"]:
            priority = 9
        elif len(self.allergies) > 3:
            priority = 7
        
        return priority
    
    def get_admission_type(self) -> str:
        """
        Kabul tipini döndürür
        """
        return "Inpatient"
    
    def calculate_daily_cost(self) -> float:
        """
        Günlük maliyeti hesaplar
        """
        base_cost = 500.0
        
        if self.bed_type == "private":
            base_cost += 200.0
        elif self.bed_type == "vip":
            base_cost += 500.0
        
        if self.ward.lower() in ["icu", "intensive care"]:
            base_cost += 1000.0
        
        medication_cost = sum(med.get('daily_cost', 0) for med in self.medications)
        
        return base_cost + medication_cost
    
    def assign_room(self, room_number: str, ward: str) -> None:
        """
        Oda ataması yapar
        """
        old_room = self.room_number
        self.room_number = room_number
        self.ward = ward
        self.add_medical_history(f"Room changed from {old_room} to {room_number} in {ward}")
    
    def set_bed_type(self, bed_type: str) -> None:
        """
        Yatak tipini ayarlar
        """
        valid_types = ["standard", "private", "vip"]
        if bed_type in valid_types:
            self.bed_type = bed_type
        else:
            raise ValueError(f"Invalid bed type: {bed_type}")
    
    def add_daily_note(self, note: str, author: str) -> None:
        """
        Günlük not ekler
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.daily_notes.append(f"[{timestamp}] {author}: {note}")
    
    def add_medication(self, medication_name: str, dosage: str, frequency: str, daily_cost: float) -> None:
        """
        İlaç ekler
        """
        medication = {
            "name": medication_name,
            "dosage": dosage,
            "frequency": frequency,
            "daily_cost": daily_cost,
            "start_date": datetime.now().strftime('%Y-%m-%d'),
            "active": True
        }
        self.medications.append(medication)
        self.add_medical_history(f"Medication added: {medication_name} - {dosage} - {frequency}")
    
    def record_vital_signs(self, temperature: float, blood_pressure: str, 
                          heart_rate: int, oxygen_saturation: int) -> None:
        """
        Vital signs kaydeder
        """
        vital_signs = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "temperature": temperature,
            "blood_pressure": blood_pressure,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen_saturation
        }
        self.vital_signs_history.append(vital_signs)
        
        if temperature > 38.5 or oxygen_saturation < 90:
            self.add_medical_history(f"Alert: Abnormal vital signs recorded")
    
    def set_estimated_stay(self, days: int) -> None:
        """
        Tahmini kalış süresini ayarlar
        """
        self.estimated_stay_days = days
        expected_discharge = self.admission_date + timedelta(days=days)
        self.add_medical_history(f"Estimated discharge date: {expected_discharge.strftime('%Y-%m-%d')}")
    
    def discharge_patient(self, discharge_summary: str) -> None:
        """
        Hastayı taburcu eder
        """
        self.discharge_date = datetime.now()
        self.update_status("discharged")
        self.add_medical_history(f"Patient discharged: {discharge_summary}")
    
    def get_length_of_stay(self) -> int:
        """
        Kalış süresini döndürür
        """
        if self.discharge_date:
            return (self.discharge_date - self.admission_date).days
        return (datetime.now() - self.admission_date).days
    
    def set_visitor_restrictions(self, restricted: bool, reason: str = "") -> None:
        """
        Ziyaretçi kısıtlaması ayarlar
        """
        self.visitor_restrictions = restricted
        if restricted:
            self.add_medical_history(f"Visitor restrictions applied: {reason}")
    
    @classmethod
    def create_patient_from_dict(cls, data: Dict):
        """
        Dictionary'den hasta oluşturur
        """
        return cls(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            room_number=data['room_number'],
            ward=data['ward'],
            admission_reason=data['admission_reason']
        )
    
    def get_inpatient_summary(self) -> Dict:
        """
        Yatan hasta özetini döndürür
        """
        return {
            **self.get_patient_info(),
            "room_number": self.room_number,
            "ward": self.ward,
            "admission_reason": self.admission_reason,
            "length_of_stay": self.get_length_of_stay(),
            "daily_cost": self.calculate_daily_cost(),
            "bed_type": self.bed_type,
            "medications_count": len(self.medications),
            "visitor_restrictions": self.visitor_restrictions
        }


class Outpatient(Patient):
    """
    Ayaktan hasta sınıfı
    """
    
    def __init__(self, name: str, age: int, gender: str, visit_reason: str,
                 status: str = "active"):
        super().__init__(name, age, gender, status)
        self.visit_reason = visit_reason
        self.visit_date = datetime.now()
        self.department: Optional[str] = None
        self.assigned_doctor: Optional[str] = None
        self.appointment_id: Optional[str] = None
        self.visit_history: List[Dict] = []
        self.prescriptions: List[Dict] = []
        self.follow_up_required: bool = False
        self.next_appointment_date: Optional[datetime] = None
        self.referral_needed: bool = False
        self.referral_department: Optional[str] = None
        self.payment_status: str = "pending"
        self.visit_count: int = 1
    
    def calculate_treatment_priority(self) -> int:
        """
        Ayaktan hasta için tedavi önceliğini hesaplar
        """
        priority = 3
        
        if self.is_critical():
            priority = 9
        elif "emergency" in self.visit_reason.lower():
            priority = 7
        elif self.age > 75 or self.age < 2:
            priority = 6
        elif self.follow_up_required:
            priority = 4
        
        return priority
    
    def get_admission_type(self) -> str:
        """
        Kabul tipini döndürür
        """
        return "Outpatient"
    
    def calculate_daily_cost(self) -> float:
        """
        Günlük maliyeti hesaplar
        """
        base_consultation_fee = 150.0
        
        if self.department in ["cardiology", "neurology", "oncology"]:
            base_consultation_fee += 100.0
        
        prescription_cost = sum(presc.get('cost', 0) for presc in self.prescriptions)
        
        return base_consultation_fee + prescription_cost
    
    def add_visit_record(self, diagnosis: str, treatment: str, doctor: str) -> None:
        """
        Ziyaret kaydı ekler
        """
        visit_record = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "diagnosis": diagnosis,
            "treatment": treatment,
            "doctor": doctor,
            "department": self.department
        }
        self.visit_history.append(visit_record)
        self.visit_count += 1
        self.add_medical_history(f"Outpatient visit: {diagnosis}")
    
    def add_prescription(self, medication_name: str, dosage: str, 
                        duration_days: int, cost: float) -> None:
        """
        Reçete ekler
        """
        prescription = {
            "medication": medication_name,
            "dosage": dosage,
            "duration_days": duration_days,
            "cost": cost,
            "issue_date": datetime.now().strftime('%Y-%m-%d'),
            "filled": False
        }
        self.prescriptions.append(prescription)
        self.add_medical_history(f"Prescription issued: {medication_name}")
    
    def schedule_follow_up(self, days_ahead: int, reason: str) -> None:
        """
        Takip randevusu planlar
        """
        self.follow_up_required = True
        self.next_appointment_date = datetime.now() + timedelta(days=days_ahead)
        self.add_medical_history(f"Follow-up scheduled for {self.next_appointment_date.strftime('%Y-%m-%d')}: {reason}")
    
    def create_referral(self, department: str, reason: str) -> str:
        """
        Sevk oluşturur
        """
        self.referral_needed = True
        self.referral_department = department
        referral_id = f"REF-{self.id[:8]}-{datetime.now().strftime('%Y%m%d')}"
        self.add_medical_history(f"Referred to {department}: {reason}")
        return referral_id
    
    def mark_prescription_filled(self, prescription_index: int) -> None:
        """
        Reçetenin karşılandığını işaretler
        """
        if 0 <= prescription_index < len(self.prescriptions):
            self.prescriptions[prescription_index]['filled'] = True
            self.prescriptions[prescription_index]['fill_date'] = datetime.now().strftime('%Y-%m-%d')
    
    def update_payment_status(self, status: str) -> None:
        """
        Ödeme durumunu günceller
        """
        valid_statuses = ["pending", "paid", "insurance_claimed", "partially_paid"]
        if status in valid_statuses:
            self.payment_status = status
            self.add_medical_history(f"Payment status: {status}")
    
    def get_unfilled_prescriptions(self) -> List[Dict]:
        """
        Karşılanmamış reçeteleri döndürür
        """
        return [p for p in self.prescriptions if not p['filled']]
    
    @classmethod
    def create_patient_from_dict(cls, data: Dict):
        """
        Dictionary'den hasta oluşturur
        """
        return cls(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            visit_reason=data['visit_reason']
        )
    
    def get_outpatient_summary(self) -> Dict:
        """
        Ayaktan hasta özetini döndürür
        """
        return {
            **self.get_patient_info(),
            "visit_reason": self.visit_reason,
            "department": self.department,
            "visit_count": self.visit_count,
            "follow_up_required": self.follow_up_required,
            "next_appointment": self.next_appointment_date.strftime('%Y-%m-%d') if self.next_appointment_date else None,
            "referral_needed": self.referral_needed,
            "payment_status": self.payment_status,
            "total_cost": self.calculate_daily_cost()
        }


class EmergencyPatient(Patient):
    """
    Acil hasta sınıfı
    """
    
    def __init__(self, name: str, age: int, gender: str, emergency_type: str,
                 severity_level: int, status: str = "critical"):
        super().__init__(name, age, gender, status)
        self.emergency_type = emergency_type
        self.severity_level = severity_level
        self.arrival_time = datetime.now()
        self.triage_time: Optional[datetime] = None
        self.treatment_start_time: Optional[datetime] = None
        self.arrival_mode: str = "ambulance"
        self.vital_signs_on_arrival: Dict = {}
        self.injuries: List[str] = []
        self.emergency_procedures: List[Dict] = []
        self.stabilized: bool = False
        self.trauma_team_activated: bool = False
        self.blood_transfusion_required: bool = False
        self.surgery_required: bool = False
        self.emergency_contacts_notified: bool = False
        self.police_report_filed: bool = False
    
    def calculate_treatment_priority(self) -> int:
        """
        Acil hasta için tedavi önceliğini hesaplar
        """
        base_priority = 10
        
        if self.severity_level == 1:
            base_priority = 10
        elif self.severity_level == 2:
            base_priority = 9
        elif self.severity_level == 3:
            base_priority = 7
        else:
            base_priority = 5
        
        if self.trauma_team_activated:
            base_priority = 10
        
        if not self.stabilized:
            base_priority = min(10, base_priority + 1)
        
        return base_priority
    
    def get_admission_type(self) -> str:
        """
        Kabul tipini döndürür
        """
        return "Emergency"
    
    def calculate_daily_cost(self) -> float:
        """
        Günlük maliyeti hesaplar
        """
        base_emergency_cost = 1500.0
        
        severity_multiplier = {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.5, 5: 1.0}
        base_emergency_cost *= severity_multiplier.get(self.severity_level, 1.0)
        
        if self.trauma_team_activated:
            base_emergency_cost += 2000.0
        
        if self.blood_transfusion_required:
            base_emergency_cost += 1000.0
        
        procedure_cost = sum(proc.get('cost', 0) for proc in self.emergency_procedures)
        
        return base_emergency_cost + procedure_cost
    
    def perform_triage(self, triage_level: int, initial_assessment: str) -> None:
        """
        Triyaj yapar
        """
        self.triage_time = datetime.now()
        self.severity_level = triage_level
        self.add_medical_history(f"Triage completed - Level {triage_level}: {initial_assessment}")
    
    def record_arrival_vitals(self, blood_pressure: str, heart_rate: int,
                             respiratory_rate: int, glasgow_coma_scale: int) -> None:
        """
        Varış vital signs kaydeder
        """
        self.vital_signs_on_arrival = {
            "blood_pressure": blood_pressure,
            "heart_rate": heart_rate,
            "respiratory_rate": respiratory_rate,
            "glasgow_coma_scale": glasgow_coma_scale,
            "recorded_at": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        if glasgow_coma_scale < 8 or heart_rate > 120 or heart_rate < 50:
            self.trauma_team_activated = True
            self.add_medical_history("Trauma team activated due to critical vital signs")
    
    def add_injury(self, injury_description: str, body_part: str) -> None:
        """
        Yaralanma ekler
        """
        injury = f"{body_part}: {injury_description}"
        self.injuries.append(injury)
        self.add_medical_history(f"Injury documented: {injury}")
    
    def add_emergency_procedure(self, procedure_name: str, performed_by: str, 
                               cost: float, success: bool) -> None:
        """
        Acil prosedür ekler
        """
        procedure = {
            "name": procedure_name,
            "performed_by": performed_by,
            "cost": cost,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "success": success
        }
        self.emergency_procedures.append(procedure)
        self.add_medical_history(f"Emergency procedure: {procedure_name} - {'Successful' if success else 'Failed'}")
    
    def stabilize_patient(self) -> None:
        """
        Hastayı stabilize eder
        """
        self.stabilized = True
        self.update_status("active")
        stabilization_time = datetime.now() - self.arrival_time
        self.add_medical_history(f"Patient stabilized after {stabilization_time.seconds // 60} minutes")
    
    def activate_trauma_team(self, reason: str) -> None:
        """
        Travma ekibini aktive eder
        """
        self.trauma_team_activated = True
        self.add_medical_history(f"Trauma team activated: {reason}")
    
    def request_blood_transfusion(self, units: int, blood_type: str) -> None:
        """
        Kan transfüzyonu talep eder
        """
        self.blood_transfusion_required = True
        self.add_medical_history(f"Blood transfusion requested: {units} units of {blood_type}")
    
    def schedule_emergency_surgery(self, surgery_type: str, urgency: str) -> None:
        """
        Acil ameliyat planlar
        """
        self.surgery_required = True
        self.add_medical_history(f"Emergency surgery scheduled: {surgery_type} - Urgency: {urgency}")
    
    def notify_emergency_contacts(self) -> None:
        """
        Acil kontakları bilgilendirir
        """
        self.emergency_contacts_notified = True
        self.add_medical_history("Emergency contacts notified")
    
    def get_time_to_treatment(self) -> Optional[int]:
        """
        Tedaviye kadar geçen süreyi döndürür (dakika)
        """
        if self.treatment_start_time:
            return (self.treatment_start_time - self.arrival_time).seconds // 60
        return None
    
    @classmethod
    def create_patient_from_dict(cls, data: Dict):
        """
        Dictionary'den hasta oluşturur
        """
        return cls(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            emergency_type=data['emergency_type'],
            severity_level=data['severity_level']
        )
    
    def get_emergency_summary(self) -> Dict:
        """
        Acil hasta özetini döndürür
        """
        return {
            **self.get_patient_info(),
            "emergency_type": self.emergency_type,
            "severity_level": self.severity_level,
            "stabilized": self.stabilized,
            "trauma_team_activated": self.trauma_team_activated,
            "injuries_count": len(self.injuries),
            "procedures_performed": len(self.emergency_procedures),
            "time_to_treatment": self.get_time_to_treatment(),
            "estimated_cost": self.calculate_daily_cost()
        }


@dataclass
class MedicalRecord:
    """
    Tıbbi kayıt veri sınıfı
    """
    record_id: str
    patient_id: str
    record_type: str
    description: str
    recorded_by: str
    timestamp: datetime = field(default_factory=datetime.now)
    attachments: List[str] = field(default_factory=list)
    
    def add_attachment(self, file_path: str) -> None:
        """
        Ek dosya ekler
        """
        self.attachments.append(file_path)
    
    def get_record_age_days(self) -> int:
        """
        Kaydın yaşını gün olarak döndürür
        """
        return (datetime.now() - self.timestamp).days


@dataclass
class VitalSigns:
    """
    Vital signs veri sınıfı
    """
    patient_id: str
    temperature: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    respiratory_rate: int
    oxygen_saturation: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_normal(self) -> bool:
        """
        Vital signs'ın normal olup olmadığını kontrol eder
        """
        if not (36.0 <= self.temperature <= 37.5):
            return False
        if not (90 <= self.blood_pressure_systolic <= 140):
            return False
        if not (60 <= self.blood_pressure_diastolic <= 90):
            return False
        if not (60 <= self.heart_rate <= 100):
            return False
        if not (12 <= self.respiratory_rate <= 20):
            return False
        if self.oxygen_saturation < 95:
            return False
        return True
    
    def get_alert_level(self) -> str:
        """
        Uyarı seviyesini döndürür
        """
        if self.is_normal():
            return "normal"
        
        if (self.temperature > 39.0 or self.temperature < 35.0 or
            self.blood_pressure_systolic > 180 or self.blood_pressure_systolic < 80 or
            self.heart_rate > 120 or self.heart_rate < 50 or
            self.oxygen_saturation < 90):
            return "critical"
        
        return "warning"


@dataclass
class Medication:
    """
    İlaç veri sınıfı
    """
    medication_id: str
    name: str
    dosage: str
    frequency: str
    route: str
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    prescribed_by: str = ""
    side_effects: List[str] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """
        İlacın aktif olup olmadığını kontrol eder
        """
        if self.end_date is None:
            return True
        return datetime.now() < self.end_date
    
    def add_side_effect(self, side_effect: str) -> None:
        """
        Yan etki ekler
        """
        if side_effect not in self.side_effects:
            self.side_effects.append(side_effect)


class PatientService:
    """
    Hasta yönetim servis katmanı
    """
    
    def __init__(self, repository):
        self.repository = repository
        self.notification_service = NotificationService()
    
    def register_new_patient(self, patient: Patient) -> str:
        """
        Yeni hasta kaydı oluşturur
        """
        if not Patient.validate_patient_data(patient.name, patient.age, patient.gender):
            raise ValueError("Invalid patient data")
        
        self.repository.save(patient)
        self.notification_service.send_registration_notification(patient)
        return patient.id
    
    def discharge_patient(self, patient_id: str, discharge_summary: str) -> bool:
        """
        Hastayı taburcu eder
        """
        patient = self.repository.find_by_id(patient_id)
        if patient is None:
            return False
        
        if isinstance(patient, Inpatient):
            patient.discharge_patient(discharge_summary)
            self.repository.update(patient)
            self.notification_service.send_discharge_notification(patient)
            return True
        
        return False
    
    def transfer_patient(self, patient_id: str, new_ward: str, new_room: str) -> bool:
        """
        Hastayı transfer eder
        """
        patient = self.repository.find_by_id(patient_id)
        if patient is None or not isinstance(patient, Inpatient):
            return False
        
        patient.assign_room(new_room, new_ward)
        self.repository.update(patient)
        self.notification_service.send_transfer_notification(patient, new_ward)
        return True
    
    def update_patient_status(self, patient_id: str, new_status: str) -> bool:
        """
        Hasta durumunu günceller
        """
        patient = self.repository.find_by_id(patient_id)
        if patient is None:
            return False
        
        patient.update_status(new_status)
        self.repository.update(patient)
        
        if new_status == "critical":
            self.notification_service.send_critical_alert(patient)
        
        return True
    
    def get_patient_summary(self, patient_id: str) -> Optional[Dict]:
        """
        Hasta özetini getirir
        """
        patient = self.repository.find_by_id(patient_id)
        if patient is None:
            return None
        
        if isinstance(patient, Inpatient):
            return patient.get_inpatient_summary()
        elif isinstance(patient, Outpatient):
            return patient.get_outpatient_summary()
        elif isinstance(patient, EmergencyPatient):
            return patient.get_emergency_summary()
        
        return patient.get_patient_info()
    
    def search_patients_by_name(self, name: str) -> List[Patient]:
        """
        İsme göre hasta arar
        """
        return self.repository.find_by_name(name)
    
    def get_critical_patients(self) -> List[Patient]:
        """
        Kritik hastaları getirir
        """
        return self.repository.find_by_status("critical")
    
    def get_patients_by_type(self, patient_type: str) -> List[Patient]:
        """
        Tipe göre hastaları getirir
        """
        all_patients = self.repository.get_all()
        
        if patient_type == "inpatient":
            return [p for p in all_patients if isinstance(p, Inpatient)]
        elif patient_type == "outpatient":
            return [p for p in all_patients if isinstance(p, Outpatient)]
        elif patient_type == "emergency":
            return [p for p in all_patients if isinstance(p, EmergencyPatient)]
        
        return []
    
    def calculate_total_bed_occupancy(self) -> int:
        """
        Toplam yatak doluluk oranını hesaplar
        """
        inpatients = self.get_patients_by_type("inpatient")
        active_inpatients = [p for p in inpatients if p.status == "active"]
        return len(active_inpatients)
    
    def get_patients_requiring_follow_up(self) -> List[Outpatient]:
        """
        Takip gerektiren hastaları getirir
        """
        outpatients = self.get_patients_by_type("outpatient")
        return [p for p in outpatients if isinstance(p, Outpatient) and p.follow_up_required]
    
    @staticmethod
    def calculate_average_age(patients: List[Patient]) -> float:
        """
        Ortalama yaşı hesaplar
        """
        if not patients:
            return 0.0
        return sum(p.age for p in patients) / len(patients)
    
    @staticmethod
    def get_gender_distribution(patients: List[Patient]) -> Dict[str, int]:
        """
        Cinsiyet dağılımını döndürür
        """
        distribution = {"male": 0, "female": 0, "other": 0}
        for patient in patients:
            distribution[patient.gender] = distribution.get(patient.gender, 0) + 1
        return distribution
    
    @classmethod
    def create_bulk_patients(cls, patient_data_list: List[Dict]) -> List[Patient]:
        """
        Toplu hasta oluşturur
        """
        patients = []
        for data in patient_data_list:
            patient_type = data.pop('type', 'outpatient')
            
            if patient_type == 'inpatient':
                patient = Inpatient.create_patient_from_dict(data)
            elif patient_type == 'emergency':
                patient = EmergencyPatient.create_patient_from_dict(data)
            else:
                patient = Outpatient.create_patient_from_dict(data)
            
            patients.append(patient)
        
        return patients


class NotificationService:
    """
    Bildirim servisi
    """
    
    def __init__(self):
        self.notifications: List[Dict] = []
    
    def send_registration_notification(self, patient: Patient) -> None:
        """
        Kayıt bildirimi gönderir
        """
        notification = {
            "type": "registration",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "message": f"New patient registered: {patient.name}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.notifications.append(notification)
    
    def send_discharge_notification(self, patient: Patient) -> None:
        """
        Taburcu bildirimi gönderir
        """
        notification = {
            "type": "discharge",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "message": f"Patient discharged: {patient.name}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.notifications.append(notification)
    
    def send_transfer_notification(self, patient: Patient, new_ward: str) -> None:
        """
        Transfer bildirimi gönderir
        """
        notification = {
            "type": "transfer",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "message": f"Patient transferred to {new_ward}: {patient.name}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.notifications.append(notification)
    
    def send_critical_alert(self, patient: Patient) -> None:
        """
        Kritik durum uyarısı gönderir
        """
        notification = {
            "type": "critical_alert",
            "patient_id": patient.id,
            "patient_name": patient.name,
            "message": f"CRITICAL: Patient status changed to critical: {patient.name}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "priority": "high"
        }
        self.notifications.append(notification)
    
    def get_recent_notifications(self, count: int = 10) -> List[Dict]:
        """
        Son bildirimleri getirir
        """
        return self.notifications[-count:]
    
    def clear_notifications(self) -> None:
        """
        Bildirimleri temizler
        """
        self.notifications.clear()
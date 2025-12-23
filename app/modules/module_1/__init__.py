"""
Hasta Yönetim Modülü - Patient Management Module
"""

from app.modules.module_1.base import Patient
from app.modules.module_1.implementations import (
    Inpatient,
    Outpatient,
    EmergencyPatient,
    MedicalRecord,
    VitalSigns,
    Medication,
    PatientService,
    NotificationService
)
from app.modules.module_1.repository import PatientRepository

__all__ = [
    'Patient',
    'Inpatient',
    'Outpatient',
    'EmergencyPatient',
    'MedicalRecord',
    'VitalSigns',
    'Medication',
    'PatientService',
    'NotificationService',
    'PatientRepository'
]

__version__ = '1.0.0'
__author__ = 'Hospital Management Team'
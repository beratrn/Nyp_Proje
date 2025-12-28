"""
Hasta Yönetim Modülü - Patient Management Module
"""

from base import Patient
from implementations import (
    Inpatient,
    Outpatient,
    EmergencyPatient,
    MedicalRecord,
    VitalSigns,
    Medication,
    PatientService,
    NotificationService
)
from repository import PatientRepository

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
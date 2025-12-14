# app/modules/laboratory/base.py
from abc import ABC, abstractmethod
from datetime import datetime
import uuid
from typing import Dict, Any, List

# --- Özel Hata Sınıfları ---
class LabHata(Exception):
    """Laboratuvar modülüne özgü hata durumu."""
    pass

class StatüHatası(LabHata):
    """Geçersiz statü girişi yapıldığında hata verir."""
    pass

class LabTest(ABC):
    """
    Laboratuvar Tetkikleri için Soyut Temel Sınıfı (Abstract Base Class).
    Tüm alt sınıfların (Kan, Görüntüleme, Biyopsi) ortak özelliklerini ve zorunlu kurallarını tanımlamak için.
    """
    
   
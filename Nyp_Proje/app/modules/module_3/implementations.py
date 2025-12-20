# app/modules/laboratory/implementations.py
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import random

# Base class'ı import ediyoruz
from .base import LabTest, LabHata, StatüHatası

# Veri Modelleri
class TestSonucu:
    """Test sonuçlarını detaylı şekilde tutan veri sınıfı."""
    
    def __init__(self, test_num, parametre_adi, deger, birim, referans_min, referans_max, kritik_esik=None):
        # Her bir veriyi manuel olarak nesneye atıyoruz
        self.test_num = test_num
        self.parametre_adi = parametre_adi
        self.deger = deger
        self.birim = birim
        self.referans_min = referans_min
        self.referans_max = referans_max
        self.kritik_esik = kritik_esik

    def normal_mi(self) -> bool:
        """Değerin normal aralıkta olup olmadığını kontrol eder."""
        return self.referans_min <= self.deger <= self.referans_max
    
    def kritik_mi(self) -> bool:
        """Değerin kritik eşiği aşıp aşmadığını kontrol eder."""
        if self.kritik_esik is None:
            return False
        return self.deger >= self.kritik_esik

class KritikUyari:
    """Kritik test sonuçları için uyarı bildirimi sınıfı."""
    
    def __init__(self, uyari_id, test_num, hasta_tc, uyari_mesaji, oncelik_seviyesi, olusturma_zamani=None, goruldu_mu=False):
        self.uyari_id = uyari_id
        self.test_num = test_num
        self.hasta_tc = hasta_tc
        self.uyari_mesaji = uyari_mesaji
        self.oncelik_seviyesi = oncelik_seviyesi
        # Eğer zaman verilmezse o anki zamanı ata
        self.olusturma_zamani = olusturma_zamani if olusturma_zamani else datetime.now()
        self.goruldu_mu = goruldu_mu
    
    def goruldu_isaretle(self):
        """Uyarıyı görüldü olarak işaretler."""
        self.goruldu_mu = True
        print(f"✓ Uyarı {self.uyari_id} görüldü olarak işaretlendi.")




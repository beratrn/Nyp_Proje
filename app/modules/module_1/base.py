# app/modules/module_1/base.py
import uuid
import json
import datetime
import inspect
from abc import ABC, abstractmethod
# ÖZEL HATA SINIFLARI (EXCEPTION HANDLING)
class TemelSistemHatasi(Exception):
    """Sistem genelindeki temel hata sınıfı."""
    def _init_(self, mesaj):
        self.mesaj = mesaj
        self.zaman = datetime.datetime.now()
        super()._init_(self.mesaj)

class VeriDogrulamaHatasi(TemelSistemHatasi):
    """Veri tipi veya formatı yanlış olduğunda fırlatılır."""
    pass

class KimlikHatasi(TemelSistemHatasi):
    """ID veya benzersizlik çakışmalarında fırlatılır."""
    pass
# YARDIMCI DOĞRULAMA SINIFI (VALIDATOR UTILITY)
class VeriDogrulayici:
    """Statik metodlarla veri bütünlüğünü kontrol eden yardımcı sınıf."""

    @staticmethod
    def metin_kontrol(deger, alan_adi, min_uzunluk=1):
        if not isinstance(deger, str):
            raise VeriDogrulamaHatasi(f"{alan_adi} alanı metin (string) formatında olmalıdır.")
        if len(deger.strip()) < min_uzunluk:
            raise VeriDogrulamaHatasi(f"{alan_adi} alanı en az {min_uzunluk} karakter olmalıdır.")
        return deger.strip()

    @staticmethod
    def tarih_kontrol(deger, alan_adi):
        if not isinstance(deger, datetime.datetime):
            raise VeriDogrulamaHatasi(f"{alan_adi} alanı datetime objesi olmalıdır.")
        return deger

    @staticmethod
    def tamsayi_kontrol(deger, alan_adi, pozitif_zorunlu=True):
        if not isinstance(deger, int):
            raise VeriDogrulamaHatasi(f"{alan_adi} alanı tam sayı (integer) olmalıdır.")
        if pozitif_zorunlu and deger < 0:
            raise VeriDogrulamaHatasi(f"{alan_adi} alanı negatif olamaz.")
        return deger

    @staticmethod
    def benzersiz_kimlik_olustur():
        return str(uuid.uuid4())

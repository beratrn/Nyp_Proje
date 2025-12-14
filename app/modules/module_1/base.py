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


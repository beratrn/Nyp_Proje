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
    #Sınıf Nitelikleri
    _Test_Statü : List[str] = ["Beklemede", "Devam Ediyor", "Tamamlandı", "Kritik", "İptal Edildi", "Hata"]
    
    @staticmethod
    def _tetkik_num() -> str:
        """
        Statik Metot : Tetkikler için benzersiz bir numara üretir.
        """
        return f"LAB-{uuid.uuid4()}"

    def __init__(self, Hasta_TC: str, test_tipi: str):
        """
        LabTest nesnesinin başlatıcısı (Constructor).
        
        """
        #Başlatma sırasında temel doğrulama 
        if not Hasta_TC or not isinstance(Hasta_TC, str) or len(Hasta_TC.strip()) == 0:
            raise ValueError("Hasta ID'si boş olamaz.")
        if not test_tipi or len(test_tipi.strip()) < 3:
            raise ValueError("Test türü belirtilmeli ve en az 3 karakter olmalıdır.")

        # Gizli Nitelikler (Kapsülleme) 
        self._test_num: str = self._tetkik_num()
        self._Hasta_TC: str = Hasta_TC
        self._test_tipi: str = test_tipi
        self._sonuc: str = "Sonuç Bekleniyor"
        self._statü: str = self._Test_Statü[0] # Başlangıç: Beklemede
        self._randevu_tarihi: datetime = datetime.now()
        self._lab_birimi: str = "Genel Laboratuvar" 
        self._Doktor_TC: str = "Atanmadı"

    # ABSTRACT METOTLAR
    
    @abstractmethod
    def kritik_seviye_kontrol(self) -> bool:
        """
        Abstract Metot 1: Tetkik sonucunun kritik bir eşiği aşıp aşmadığını kontrol etmek için
        Alt sınıflar bu mantığı kendi test türlerine göre uygularlar
        """
        pass

    @abstractmethod
    def maliyet_hesapla(self) -> float:
        """
        Zorunlu Abstract Metot 2: Tetkikin tahmini maliyetini hesaplar.
        Alt sınıflar, testin türüne göre maliyet hesaplama mantığını uygulamak zorundadır.
        """
        pass

    # KAPSÜLLEME (Getter/Setter)
    
    # test_numarası 
    @property
    def test_num(self) -> str:
        """Tetkik ID'sine erişim sağlar."""
        return self._test_num
    
    # statü (Getter)
    @property
    def statü(self) -> str:
        """Tetkik durumuna erişim sağlar."""
        return self._statü
    
    # statü (Setter) 
    @statü.setter
    def statü(self, yeni_statü: str):
        """
        Durumu güncellerken doğrulama yapar ve Statü Hataso fırlatır
        """
        try:
            if yeni_statü not in self._Test_Statü:
                raise StatüHatası(
                    f"Geçersiz durum '{yeni_statü}'. Kabul edilenler: {', '.join(self._Test_Statü)}"
                )
            self._status = yeni_statü
        except StatüHatası as e:
            print(f"[Durum Güncelleme Hatası] ID: {self._test_num} - Hata: {e}")
            raise 

    # Sonuç (Getter)
    @property
    def sonuc(self) -> str:
        """Test sonucuna erişim sağlar."""
        return self._result
        
    # Sonuc(Setter) - Detaylı Hata Kontrolü
    @sonuc.setter
    def sonuc(self, yeni_sonuc: str):
        """
        Test sonucunu ayarlar. Sonucun string ve yeterli uzunlukta olmasını kontrol eder.
        """
        try:
            if not isinstance(yeni_sonuc, str) or len(yeni_sonuc.strip()) < 5:
                raise ValueError("Sonuç bilgisi metin olmalı ve en az 5 karakter içermelidir.")
            self._result = yeni_sonuc
        except ValueError as e:
            print(f"[Sonuç Giriş Hatası] ID: {self._test_num} - Hata: {e}")
            raise    

     # teknisyen numarası (Getter)
    @property
    def teknisyen_num(self) -> str:
        """Sonucu giren teknisyenin ID'sine erişim sağlar."""
        return self._teknisyen_num
        
    # teknisyen numarası (Setter)
    @teknisyen_num.setter
    def teknisyen_num(self, yeni_num: str):
        """Teknisyen Numarasını ayarlar."""
        if len(yeni_num.strip()) < 4:
            raise ValueError("Teknisyen ID'si en az 4 karakter olmalıdır.")
        self._teknisyen_num = yeni_num

    #  Nesne Metotları
    
    def sonucu_gir(self, sonuc: str, teknisyen_num: str):
        """
        Tetkik sonucunu kaydeder ve kritik seviye kontrolünü çağırır.
        """
        try:
            self.sonuc = sonuc # Setter'lar ile doğrulama yapılır
            self.teknisyen_num = teknisyen_num
            self.statü = "Tamamlandı" 
            
            # Polimorfizm
            if self.kritik_seviye_kontrol():
                self.statü = "Kritik" 
                print(f"[KRİTİK BİLDİRİM] Test {self.test_num} durumu KRİTİK olarak işaretlendi.")
                
        except (ValueError, StatüHatası) as e:
            # Hata oluşursa durumu 'Hata' olarak günceller
            print(f"[Kritik İşlem Hatası] Test numarası {self._test_num}: İşlem Başarısız. ({e})")
            self.statü = "Hata"

    def get_ozet_bilgi(self) -> Dict[str, Any]:
        """Testin temel özetini sözlük olarak döner."""
        return {
            "test_num": self._test_num,
            "hasta_tc": self._Hasta_TC,
            "tip": self._test_tipi,
            "durum": self.statü,
            "istek_tarihi": self._randevu_tarihi.strftime("%Y-%m-%d %H:%M:%S"),
            "teknisyen": self._teknisyen_num,
            "lab_birimi": self._lab_birimi
        }
        
    def iptal_et(self, neden: str):
        """Test isteğini iptal eder."""
        if self.statü in ["Tamamlandı", "Kritik"]:
            raise LabHata("Tamamlanmış veya kritik bir test iptal edilemez.")
        self.statü = "İptal Edildi"
        print(f"Test {self.test_num} iptal edildi. Neden: {neden}")     

#DosyaSonuBase   
    
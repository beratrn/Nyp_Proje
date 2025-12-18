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
# TEMEL SOYUT SINIF (ABSTRACT BASE CLASS)
class TemelModel(ABC):
    """
    Tüm sistem nesnelerinin (Doktor, Hasta, Personel vb.) türetileceği 
    ana çekirdek sınıf.
    """

    def _init_(self, ad, soyad, aciklama=""):
        # Private (Gizli) Değişken Tanımları
        self._id = VeriDogrulayici.benzersiz_kimlik_olustur()
        self._olusturma_zamani = datetime.datetime.now()
        self._guncelleme_zamani = datetime.datetime.now()
        self._aktif_mi = True
        self._silindi_mi = False
        self._ad = ""
        self._soyad = ""
        self._aciklama = ""
        self._ozellikler = {}
        self._loglar = []

        # Setterlar üzerinden güvenli atama
        self.ad = ad
        self.soyad = soyad
        self.aciklama = aciklama
        
        # Başlangıç logu
        self.log_ekle("Nesne başlatıldı.")
      
    # PROPERTY YÖNETİMİ (GETTERS & SETTERS)

    @property
    def id(self):
        return self._id

    @property
    def olusturma_zamani(self):
        return self._olusturma_zamani

    @property
    def guncelleme_zamani(self):
        return self._guncelleme_zamani

    @property
    def ad(self):
        return self._ad

    @ad.setter
    def ad(self, yeni_ad):
        if self._salt_okunur_kontrol():
            return
        temiz_ad = VeriDogrulayici.metin_kontrol(yeni_ad, "Ad", 2)
        if self._ad != temiz_ad:
            eski_deger = self._ad
            self._ad = temiz_ad
            self._guncelleme_tetikle()
            if eski_deger:
                self.log_ekle(f"Ad değiştirildi: {eski_deger} -> {temiz_ad}")

    @property
    def soyad(self):
        return self._soyad

    @soyad.setter
    def soyad(self, yeni_soyad):
        if self._salt_okunur_kontrol():
            return
        temiz_soyad = VeriDogrulayici.metin_kontrol(yeni_soyad, "Soyad", 2)
        if self._soyad != temiz_soyad:
            self._soyad = temiz_soyad
            self._guncelleme_tetikle()

    @property
    def tam_ad(self):
        return f"{self._ad} {self._soyad}".strip()

    @property
    def aciklama(self):
        return self._aciklama

    @aciklama.setter
    def aciklama(self, yeni_aciklama):
        if yeni_aciklama is None:
            yeni_aciklama = ""
        self._aciklama = str(yeni_aciklama)
        self._guncelleme_tetikle()

    @property
    def aktif_mi(self):
        return self._aktif_mi

    @aktif_mi.setter
    def aktif_mi(self, durum):
        if not isinstance(durum, bool):
            raise VeriDogrulamaHatasi("Aktiflik durumu sadece True/False olabilir.")
        if self._aktif_mi != durum:
            self._aktif_mi = durum
            self._guncelleme_tetikle()
            durum_str = "Aktif" if durum else "Pasif"
            self.log_ekle(f"Durum değiştirildi: {durum_str}")

    @property
    def silindi_mi(self):
        return self._silindi_mi

    # SİSTEM METOTLARI

    def _guncelleme_tetikle(self):
        """Herhangi bir veri değiştiğinde zaman damgasını günceller."""
        self._guncelleme_zamani = datetime.datetime.now()

    def _salt_okunur_kontrol(self):
        """Nesne silinmişse değişikliğe izin verme."""
        if self._silindi_mi:
            raise 12345("Silinmiş bir nesne üzerinde değişiklik yapılamaz.")
        return False

    def sil(self):
        """Nesneyi güvenli şekilde silindi (soft delete) olarak işaretler."""
        if self._silindi_mi:
            raise 12345("Bu nesne zaten silinmiş.")
        self._silindi_mi = True
        self._aktif_mi = False
        self._guncelleme_tetikle()
        self.log_ekle("Nesne silindi (Soft Delete).")

    def geri_yukle(self):
        """Silinmiş nesneyi tekrar aktif hale getirir."""
        if not self._silindi_mi:
            raise 12345("Bu nesne silinmemiş, geri yüklenemez.")
        self._silindi_mi = False
        self._aktif_mi = True
        self._guncelleme_tetikle()
        self.log_ekle("Nesne geri yüklendi.")

    def ozellik_ekle(self, anahtar, deger):
        """Dinamik olarak yeni özellik eklemek için kullanılır."""
        if self._salt_okunur_kontrol():
            return
        anahtar = VeriDogrulayici.metin_kontrol(anahtar, "Özellik Anahtarı")
        self._ozellikler[anahtar] = deger
        self._guncelleme_tetikle()

    def ozellik_getir(self, anahtar):
        return self._ozellikler.get(anahtar, None)

    def ozellik_sil(self, anahtar):
        if anahtar in self._ozellikler:
            del self._ozellikler[anahtar]
            self._guncelleme_tetikle()

    # LOGLAMA VE İZLEME

    def log_ekle(self, mesaj):
        """Nesne üzerindeki değişiklikleri hafızada tutar."""
        zaman_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_kaydi = f"[{zaman_str}] {mesaj}"
        self._loglar.append(log_kaydi)

    def loglari_goster(self):
        return "\n".join(self._loglar)

    # SERİLEŞTİRME VE ÇIKTI METOTLARI

    def sozluge_cevir(self):
        """Nesneyi Python dictionary formatına çevirir."""
        return {
            "id": self._id,
            "ad": self._ad,
            "soyad": self._soyad,
            "tam_ad": self.tam_ad,
            "aciklama": self._aciklama,
            "olusturma_zamani": self._olusturma_zamani.isoformat(),
            "guncelleme_zamani": self._guncelleme_zamani.isoformat(),
            "aktif_mi": self._aktif_mi,
            "silindi_mi": self._silindi_mi,
            "ozellikler": self._ozellikler
        }

    def json_cikti_ver(self):
        """Nesneyi JSON formatında string olarak döndürür."""
        veri = self.sozluge_cevir()
        return json.dumps(veri, ensure_ascii=False, indent=4)

    @classmethod
    def sozlukten_olustur(cls, veri):
        """Dictionary verisinden nesne oluşturur (Factory Pattern)."""
        if not isinstance(veri, dict):
            raise VeriDogrulamaHatasi("Veri sözlük formatında olmalıdır.")
        
        ad = veri.get("ad", "")
        soyad = veri.get("soyad", "")
        aciklama = veri.get("aciklama", "")
        
        yeni_nesne = cls(ad, soyad, aciklama)
        
        # ID koruması
        if "id" in veri:
            yeni_nesne._id = veri["id"]
        
        return yeni_nesne

    # PYTHON SİHİRLİ METOTLARI (MAGIC METHODS)

    def _str_(self):
        durum = "Aktif" if self._aktif_mi else "Pasif"
        if self._silindi_mi:
            durum = "SİLİNDİ"
        return f"[{durum}] {self.tam_ad} (ID: {self._id})"

    def _repr_(self):
        sinif_adi = self._class.name_
        return f"<{sinif_adi} ID={self._id} Ad={self._ad}>"

    def _eq_(self, diger):
        """İki nesnenin eşit olup olmadığını ID üzerinden kontrol eder."""
        if not isinstance(diger, TemelModel):
            return False
        return self._id == diger.id

    def _ne_(self, diger):
        return not self._eq_(diger)
    
    def _hash_(self):
        """Nesnenin set içerisinde kullanılabilmesini sağlar."""
        return hash(self._id)

    @abstractmethod
    def detay_bilgi(self):
        """
        Türetilen sınıfların (Doktor, Randevu vb.) uygulaması gereken 
        zorunlu metot. Her sınıf kendi detayını döndürmelidir.
        """
        pass

# TEST VE ÇALIŞTIRMA BLOĞU

if __name__ == "_main_":
    # Bu blok sadece modül doğrudan çalıştırıldığında test amaçlı çalışır.
    try:
        print("--- Temel Model Test Başlatılıyor ---")
        
        # Test amaçlı geçici bir sınıf türetelim
        class TestKullanici(TemelModel):
            def detay_bilgi(self):
                return f"Kullanıcı: {self.tam_ad}"

        # 1. Nesne Oluşturma
        k1 = TestKullanici("Ahmet", "Yılmaz", "Sistem Admin")
        print(f"Oluşturuldu: {k1}")
        
        # 2. Güncelleme Testi
        k1.ad = "Mehmet"
        k1.aktif_mi = False
        print(f"Güncellendi: {k1}")
        
        # 3. Log Kontrolü
        print("\n--- İşlem Logları ---")
        print(k1.loglari_goster())
        
        # 4. JSON Çıktısı
        print("\n--- JSON Formatı ---")
        print(k1.json_cikti_ver())
        
        # 5. Hata Testi (Geçersiz Veri)
        print("\n--- Hata Testi ---")
        try:
            k1.ad = "A" # Çok kısa isim hatası vermeli
        except VeriDogrulamaHatasi as e:
            print(f"Beklenen Hata Yakalandı: {e}")

        # 6. Silme Testi
        k1.sil()
        print(f"\nSilme Sonrası Durum: {k1}")
        
        try:
            k1.soyad = "Demir" # Silinmiş nesne güncellenemez
        except 12345 as e:
            print(f"Koruma Hatası Yakalandı: {e}")

    except Exception as genel_hata:
        print(f"Beklenmeyen bir hata oluştu: {genel_hata}")
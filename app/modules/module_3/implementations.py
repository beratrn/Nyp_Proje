"""
Laboratuvar & Tetkik Modülü - Implementation Katmanı
Bu dosya entities, models ve service katmanlarını içericek.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import random

# Base sınıfımızdan import
from base import LabTest, LabHata, StatüHatası

# PART 1: SUBCLASS'LAR (Base Class'tan Türetilmiş)

class BloodTest(LabTest):
    """
    Kan Testi Alt Sınıfı - LabTest'ten türetilmiştir.
    Kan testlerine özgü özellikler ve davranışlar içerir.
    """
    
    # Sınıf Değişkeni
    KAN_TEST_TURLERI = ["Tam Kan", "Biyokimya", "Hormon", "Vitamin"]
    
    def __init__(self, Hasta_TC: str, test_tipi: str, numune_hacmi: float = 5.0):
        super().__init__(Hasta_TC, test_tipi)
        self._lab_birimi = "Kan Laboratuvarı"
        self._numune_hacmi = numune_hacmi
        self._deger_1: Optional[float] = None  # Genel değer 1
        self._deger_2: Optional[float] = None  # Genel değer 2
        self._deger_3: Optional[float] = None  # Genel değer 3
        
    def kritik_seviye_kontrol(self) -> bool:
        """Kan testi sonuçlarının kritik olup olmadığını kontrol eder."""
        kritik_durum = False
        
        if self._deger_1 is not None and (self._deger_1 < 8.0 or self._deger_1 > 20.0):
            kritik_durum = True
            print(f" KRİTİK: Değer 1 anormal! ({self._deger_1})")
        
        if self._deger_2 is not None and (self._deger_2 < 2000 or self._deger_2 > 20000):
            kritik_durum = True
            print(f" KRİTİK: Değer 2 anormal! ({self._deger_2})")
        
        if self._deger_3 is not None and (self._deger_3 < 50 or self._deger_3 > 300):
            kritik_durum = True
            print(f" KRİTİK: Değer 3 tehlikeli! ({self._deger_3})")
        
        return kritik_durum
    
    def maliyet_hesapla(self) -> float:
        """Kan testinin maliyetini hesaplar."""
        base_maliyet = 150.0
        
        ek_maliyet_map = {
            "Tam Kan": 50.0,
            "Biyokimya": 100.0,
            "Hormon": 200.0,
            "Vitamin": 150.0
        }
        
        ek_maliyet = ek_maliyet_map.get(self._test_tipi, 75.0)
        
        if self.statü == "Kritik":
            ek_maliyet *= 1.3
        
        return base_maliyet + ek_maliyet
    
    def degerler_gir(self, d1: float, d2: float, d3: float):
        """Nesne Metodu: Kan test değerlerini sisteme girer."""
        self._deger_1 = d1
        self._deger_2 = d2
        self._deger_3 = d3
        print(f"Değerler girildi: Test {self.test_num}")
    
    @classmethod
    def hizli_test_olustur(cls, Hasta_TC: str) -> 'BloodTest':
        """Sınıf Metodu: Hızlı test oluşturur."""
        test = cls(Hasta_TC, "Tam Kan", numune_hacmi=3.0)
        test._lab_birimi = "Acil Lab"
        print(f" Hızlı test oluşturuldu: {test.test_num}")
        return test
    
    @staticmethod
    def hacim_yeterli_mi(hacim: float, test_sayisi: int) -> bool:
        """Statik Metot: Hacim yeterliliği kontrolü."""
        return hacim >= (test_sayisi * 2.5)
    
    def rapor_olustur(self) -> str:
        """Nesne Metodu: Test raporu oluşturur."""
        return f"""
╔════════════════════════════════╗
║   KAN TESTİ RAPORU            ║
╠════════════════════════════════╣
║ Test No  : {self.test_num:<18}║
║ Hasta TC : {self._Hasta_TC:<18}║
║ Durum    : {self.statü:<18}║
║ Değer 1  : {self._deger_1 if self._deger_1 else 'Bekleniyor':<18}║
║ Değer 2  : {self._deger_2 if self._deger_2 else 'Bekleniyor':<18}║
║ Değer 3  : {self._deger_3 if self._deger_3 else 'Bekleniyor':<18}║
║ Maliyet  : {self.maliyet_hesapla():.2f} TL           ║
╚════════════════════════════════╝
"""


class ImagingTest(LabTest):
    """
    Görüntüleme Testi Alt Sınıfı - LabTest'ten türetilmiştir.
    Radyolojik görüntüleme testlerine özgü özellikler içerir.
    """
    
    GORUNTULUEME_YONTEMLERI = ["X-Ray", "MRI", "CT", "Ultrason"]
    
    def __init__(self, Hasta_TC: str, test_tipi: str, vucut_bolgesi: str):
        super().__init__(Hasta_TC, test_tipi)
        self._lab_birimi = "Radyoloji"
        self._vucut_bolgesi = vucut_bolgesi
        self._kontrast_kullanimi = False
        self._radyasyon_dozu: Optional[float] = None
        self._radyolog_yorumu: Optional[str] = None
        self._anomali_var = False
        
    def kritik_seviye_kontrol(self) -> bool:
        """Görüntülemede kritik bulgu kontrolü."""
        kritik_kelimeler = ["tümör", "kitle", "kırık", "kanama"]
        
        if self._radyolog_yorumu:
            yorum_kucuk = self._radyolog_yorumu.lower()
            for kelime in kritik_kelimeler:
                if kelime in yorum_kucuk:
                    self._anomali_var = True
                    print(f" KRİTİK BULGU: {kelime.upper()}!")
                    return True
        
        if self._radyasyon_dozu and self._radyasyon_dozu > 50.0:
            print(f"Yüksek radyasyon: {self._radyasyon_dozu} mSv")
            return True
        
        return False
    
    def maliyet_hesapla(self) -> float:
        """Görüntüleme maliyetini hesaplar."""
        maliyet_tablo = {
            "X-Ray": 200.0,
            "Ultrason": 300.0,
            "CT": 800.0,
            "MRI": 1500.0
        }
        
        base = maliyet_tablo.get(self._test_tipi, 500.0)
        
        if self._kontrast_kullanimi:
            base += 250.0
        
        if self._anomali_var:
            base += 200.0
        
        return base
    
    def yorum_ekle(self, yorum: str):
        """Nesne Metodu: Radyolog yorumu ekler."""
        if len(yorum.strip()) < 10:
            raise ValueError("Yorum en az 10 karakter olmalı.")
        self._radyolog_yorumu = yorum
        print(f" Yorum eklendi: {self.test_num}")
    
    @classmethod
    def acil_ct_olustur(cls, Hasta_TC: str, bolge: str) -> 'ImagingTest':
        """Sınıf Metodu: Acil CT taraması oluşturur."""
        test = cls(Hasta_TC, "CT", bolge)
        test._kontrast_kullanimi = True
        test._lab_birimi = "Acil Radyoloji"
        print(f" Acil CT oluşturuldu: {test.test_num}")
        return test
    
    @staticmethod
    def radyasyon_guvenli_mi(doz: float, yas: int) -> bool:
        """Statik Metot: Radyasyon güvenliği kontrolü."""
        limit = 10.0 if yas < 18 else (30.0 if yas > 65 else 50.0)
        return doz <= limit
    
    def detay_gir(self, radyasyon: float, kontrast: bool):
        """Nesne Metodu: Görüntüleme detaylarını kaydeder."""
        self._radyasyon_dozu = radyasyon
        self._kontrast_kullanimi = kontrast
        print(f" Detaylar kaydedildi: {self.test_num}")


class BiopsyTest(LabTest):
    """
    Biyopsi Testi Alt Sınıfı - LabTest'ten türetilmiştir.
    Doku örneklerinin incelenmesine özgü özellikler içerir.
    """
    
    BIYOPSI_TURLERI = ["İğne Biyopsi", "Açık Biyopsi", "Endoskopik"]
    
    def __init__(self, Hasta_TC: str, test_tipi: str, doku_tipi: str, organ: str):
        super().__init__(Hasta_TC, test_tipi)
        self._lab_birimi = "Patoloji Lab"
        self._doku_tipi = doku_tipi
        self._organ = organ
        self._sonuc_durumu: Optional[str] = None  # "Normal", "Anormal", "Şüpheli"
        self._derece: Optional[int] = None
        self._ek_test_gerekli = False
        
    def kritik_seviye_kontrol(self) -> bool:
        """Biyopsi sonucunun kritik olup olmadığını kontrol eder."""
        kritik = False
        
        if self._sonuc_durumu == "Anormal":
            kritik = True
            print(f" KRİTİK: Anormal hücre tespit!")
        
        elif self._sonuc_durumu == "Şüpheli":
            kritik = True
            print(f" ŞÜPHELİ: İleri tetkik gerekli!")
        
        if self._derece and self._derece >= 3:
            kritik = True
            print(f"Yüksek derece: {self._derece}")
        
        return kritik
    
    def maliyet_hesapla(self) -> float:
        """Biyopsi maliyetini hesaplar."""
        maliyet_tablo = {
            "İğne Biyopsi": 800.0,
            "Açık Biyopsi": 2000.0,
            "Endoskopik": 1500.0
        }
        
        base = maliyet_tablo.get(self._test_tipi, 1000.0)
        
        if self._ek_test_gerekli:
            base += 800.0
        
        if self._sonuc_durumu == "Anormal":
            base += 500.0
        
        return base
    
    def sonuc_gir(self, durum: str, derece: Optional[int] = None):
        """Nesne Metodu: Patoloji sonucunu girer."""
        gecerli = ["Normal", "Anormal", "Şüpheli"]
        
        if durum not in gecerli:
            raise ValueError(f"Geçersiz durum. Geçerli: {gecerli}")
        
        self._sonuc_durumu = durum
        
        if derece is not None:
            if not 1 <= derece <= 4:
                raise ValueError("Derece 1-4 arası olmalı.")
            self._derece = derece
        
        print(f"Sonuç girildi: {durum}")
    
    @classmethod
    def hizli_biyopsi_olustur(cls, Hasta_TC: str, organ: str) -> 'BiopsyTest':
        """Sınıf Metodu: Hızlı biyopsi oluşturur."""
        test = cls(Hasta_TC, "İğne Biyopsi", "Yumuşak Doku", organ)
        test._ek_test_gerekli = True
        print(f"🔬 Biyopsi oluşturuldu: {test.test_num}")
        return test
    
    @staticmethod
    def risk_skoru_hesapla(yas: int, aile_gecmisi: bool) -> int:
        """Statik Metot: Risk skoru hesaplar (0-100)."""
        skor = 0
        if yas > 60:
            skor += 30
        elif yas > 40:
            skor += 15
        if aile_gecmisi:
            skor += 25
        return min(skor, 100)
    
    def ek_test_kontrolu(self) -> Tuple[bool, List[str]]:
        """Nesne Metodu: Ek test gereksinimini kontrol eder."""
        testler = []
        
        if self._sonuc_durumu == "Anormal":
            testler.extend(["İleri Görüntüleme", "Onkoloji Konsültasyon"])
        
        if self._sonuc_durumu == "Şüpheli":
            testler.extend(["Tekrar Biyopsi", "İkinci Görüş"])
        
        return len(testler) > 0, testler

# PART 2

@dataclass
class LabNumune:
    """Laboratuvar numune modeli."""
    numune_id: str
    hasta_tc: str
    numune_tipi: str
    alinma_zamani: datetime
    saklama_sicakligi: float
    son_kullanim: datetime
    kontamine: bool = False
    
    def gecerli_mi(self) -> bool:
        """Numunenin geçerli olup olmadığını kontrol eder."""
        return (not self.kontamine and self.son_kullanim > datetime.now())
    
    def bilgi(self) -> Dict[str, Any]:
        """Numune bilgilerini döner."""
        return {
            "id": self.numune_id,
            "hasta": self.hasta_tc,
            "tip": self.numune_tipi,
            "gecerli": self.gecerli_mi()
        }

@dataclass
class LabCihaz:
    """Laboratuvar cihaz modeli."""
    cihaz_id: str
    cihaz_adi: str
    kalibrasyon_tarihi: datetime
    sonraki_bakim: datetime
    kullanilabilir: bool = True
    test_sayisi: int = 0
    
    def bakim_gerekli_mi(self) -> bool:
        """Bakım kontrolü."""
        return datetime.now() >= self.sonraki_bakim
    
    def test_yap(self) -> bool:
        """Test gerçekleştirir."""
        if not self.kullanilabilir or self.bakim_gerekli_mi():
            return False
        self.test_sayisi += 1
        return random.random() > 0.05  # %95 başarı


class OncelikSeviyesi(Enum):
    """Test öncelik seviyeleri."""
    DUSUK = 1
    NORMAL = 2
    YUKSEK = 3
    ACIL = 4


@dataclass
class TestIstegi:
    """Test istek modeli."""
    istek_id: str
    hasta_tc: str
    doktor_tc: str
    istenen_testler: List[str]
    oncelik: OncelikSeviyesi
    onaylandi: bool = False

# PART 3: SERVICE KATMANI

class TestYonetimServisi:
    """Test yönetim servisi."""
    
    def __init__(self):
        self._aktif_testler: List[LabTest] = []
        self._tamamlanan: List[LabTest] = []
        self._iptal_edilen: List[LabTest] = []
    
    def yeni_test_olustur(self, test_tipi: str, hasta_tc: str, **kwargs) -> Optional[LabTest]:
        """Nesne Metodu: Yeni test oluşturur."""
        try:
            if test_tipi == "Kan":
                test = BloodTest(hasta_tc, kwargs.get("alt_tip", "Tam Kan"),
                                kwargs.get("hacim", 5.0))
            elif test_tipi == "Görüntüleme":
                test = ImagingTest(hasta_tc, kwargs.get("alt_tip", "X-Ray"),
                                  kwargs.get("bolge", "Göğüs"))
            elif test_tipi == "Biyopsi":
                test = BiopsyTest(hasta_tc, kwargs.get("alt_tip", "İğne Biyopsi"),
                                 kwargs.get("doku", "Yumuşak Doku"),
                                 kwargs.get("organ", "Genel"))
            else:
                raise ValueError(f"Geçersiz test tipi: {test_tipi}")
            
            self._aktif_testler.append(test)
            print(f"Test oluşturuldu: {test.test_num}")
            return test
        except Exception as e:
            print(f"Hata: {e}")
            return None
    
    def test_tamamla(self, test_num: str) -> bool:
        """Test tamamlama işlemi."""
        for test in self._aktif_testler:
            if test.test_num == test_num:
                self._aktif_testler.remove(test)
                self._tamamlanan.append(test)
                print(f"Test tamamlandı: {test_num}")
                return True
        return False
    
    def kritik_testler(self) -> List[LabTest]:
        """Kritik testleri listeler."""
        return [t for t in self._aktif_testler if t.statü == "Kritik"]
    
    def hasta_testleri(self, hasta_tc: str) -> List[LabTest]:
        """Hastanın tüm testlerini getirir."""
        tum = self._aktif_testler + self._tamamlanan
        return [t for t in tum if t._Hasta_TC == hasta_tc]
    
    @classmethod
    def acil_paket_olustur(cls, hasta_tc: str) -> List[LabTest]:
        """Sınıf Metodu: Acil test paketi."""
        paket = [
            BloodTest.hizli_test_olustur(hasta_tc),
            ImagingTest(hasta_tc, "X-Ray", "Göğüs")
        ]
        print(f"Acil paket: {len(paket)} test")
        return paket
    
    def istatistik(self) -> Dict[str, int]:
        """Nesne Metodu: İstatistik raporu."""
        return {
            "aktif": len(self._aktif_testler),
            "tamamlanan": len(self._tamamlanan),
            "iptal": len(self._iptal_edilen),
            "kritik": len(self.kritik_testler())
        }


class KaliteKontrolServisi:
    """Kalite kontrol servisi."""
    
    def __init__(self):
        self._kontroller: List[Dict] = []
        self._basarisiz: List[str] = []
    
    def numune_kontrolu(self, numune: LabNumune) -> Tuple[bool, str]:
        """Nesne Metodu: Numune kalite kontrolü."""
        hatalar = []
        
        if numune.son_kullanim < datetime.now():
            hatalar.append("Süresi dolmuş")
        if numune.kontamine:
            hatalar.append("Kontamine")
        
        gecti = len(hatalar) == 0
        mesaj = "BAŞARILI" if gecti else ", ".join(hatalar)
        
        self._kontroller.append({
            "numune": numune.numune_id,
            "sonuc": gecti,
            "zaman": datetime.now()
        })
        
        if not gecti:
            self._basarisiz.append(numune.numune_id)
        
        return gecti, mesaj
    
    @staticmethod
    def cihaz_kalibrasyon_kontrolu(cihaz: LabCihaz) -> bool:
        """Statik Metot: Kalibrasyon kontrolü."""
        alti_ay_once = datetime.now() - timedelta(days=180)
        return cihaz.kalibrasyon_tarihi >= alti_ay_once
    
    def rapor(self) -> str:
        """Kalite raporu."""
        toplam = len(self._kontroller)
        basarisiz = len(self._basarisiz)
        basarili = toplam - basarisiz
        oran = (basarili / toplam * 100) if toplam > 0 else 0
        
        return f"""
╔═══════════════════════════╗
║  KALİTE KONTROL RAPORU   ║
╠═══════════════════════════╣
║ Toplam    : {toplam:<12} ║
║ Başarılı  : {basarili:<12} ║
║ Başarısız : {basarisiz:<12} ║
║ Oran      : %{oran:.1f}         ║
╚═══════════════════════════╝
"""


class RaporlamaServisi:
    """Raporlama servisi."""
    
    @staticmethod
    def gunluk_rapor(testler: List[LabTest]) -> str:
        """Statik Metot: Günlük rapor."""
        bugun = datetime.now().date()
        bugun_testleri = [t for t in testler if t._randevu_tarihi.date() == bugun]
        
        kan = sum(1 for t in bugun_testleri if isinstance(t, BloodTest))
        goruntu = sum(1 for t in bugun_testleri if isinstance(t, ImagingTest))
        biyopsi = sum(1 for t in bugun_testleri if isinstance(t, BiopsyTest))
        kritik = sum(1 for t in bugun_testleri if t.statü == "Kritik")
        
        return f"""
═══════════════════════════════════
      GÜNLÜK RAPOR
      {bugun.strftime('%d/%m/%Y')}
═══════════════════════════════════
Toplam Test    : {len(bugun_testleri)}
Kan Testleri   : {kan}
Görüntülemeler : {goruntu}
Biyopsiler     : {biyopsi}
Kritik Durumlar: {kritik}
═══════════════════════════════════
"""
    
    @classmethod
    def hasta_raporu(cls, hasta_tc: str, testler: List[LabTest]) -> str:
        """Sınıf Metodu: Hasta raporu."""
        hasta_testleri = [t for t in testler if t._Hasta_TC == hasta_tc]
        
        if not hasta_testleri:
            return f"Hasta {hasta_tc} için test yok."
        
        toplam_maliyet = sum(t.maliyet_hesapla() for t in hasta_testleri)
        kritik = sum(1 for t in hasta_testleri if t.statü == "Kritik")
        
        return f"""
╔══════════════════════════════╗
║    HASTA RAPORU             ║
╠══════════════════════════════╣
║ TC       : {hasta_tc:<16}║
║ Test     : {len(hasta_testleri):<16}║
║ Kritik   : {kritik:<16}║
║ Maliyet  : {toplam_maliyet:.2f} TL      ║
╚══════════════════════════════╝
"""

class BildirimServisi:
    """Bildirim servisi."""
    
    def __init__(self):
        self._bildirimler: List[Dict] = []
    
    def kritik_bildirim(self, test: LabTest, alici: str):
        """Nesne Metodu: Kritik bildirim gönderir."""
        bildirim = {
            "tip": "KRİTİK",
            "test": test.test_num,
            "alici": alici,
            "zaman": datetime.now()
        }
        self._bildirimler.append(bildirim)
        print(f"KRİTİK BİLDİRİM: {alici}")
    
    @classmethod
    def toplu_bildirim(cls, testler: List[LabTest]) -> List[Dict]:
        """Sınıf Metodu: Toplu bildirim."""
        return [{
            "test": t.test_num,
            "hasta": t._Hasta_TC,
            "zaman": datetime.now()
        } for t in testler]
    
    @staticmethod
    def oncelik_belirle(test: LabTest) -> str:
        """Statik Metot: Bildirim önceliği."""
        oncelik_map = {
            "Kritik": "ACIL",
            "Tamamlandı": "NORMAL",
            "Beklemede": "DÜŞÜK"
        }
        return oncelik_map.get(test.statü, "ORTA")

# PART 4: POLİMORFİZM
def toplu_test_analizi(testler: List[LabTest]) -> Dict[str, Any]:
    """
    Polimorfizm: Farklı test türlerini aynı şekilde işler.
    """
    print("\n" + "="*50)
    print("POLİMORFİK ANALİZ BAŞLIYOR...")
    print("="*50)
    
    toplam_maliyet = 0.0
    kritik_sayisi = 0
    
    for test in testler:
        # Her test kendi metodunu çalıştırır (polimorfizm)
        toplam_maliyet += test.maliyet_hesapla()
        if test.kritik_seviye_kontrol():
            kritik_sayisi += 1
        
        ozet = test.get_ozet_bilgi()
        print(f"  ✓ {ozet['test_num']} - {ozet['tip']}")
    
    sonuc = {
        "toplam_test": len(testler),
        "maliyet": toplam_maliyet,
        "kritik": kritik_sayisi,
        "ortalama": toplam_maliyet / len(testler) if testler else 0
    }
    
    print("="*50)
    print(f"{len(testler)} test analiz edildi")
    print(f" Toplam: {toplam_maliyet:.2f} TL")
    print(f" Kritik: {kritik_sayisi}")
    print("="*50 + "\n")
    
    return sonuc


def kritik_testleri_sirala(testler: List[LabTest]) -> List[LabTest]:
    """Testleri kritikliğe göre sıralar."""
    puanlar = {"Kritik": 5, "Devam Ediyor": 3, "Beklemede": 2}
    return sorted(testler, key=lambda t: puanlar.get(t.statü, 1), reverse=True)

# Dosya Sonu

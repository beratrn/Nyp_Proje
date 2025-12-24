"""
Laboratuvar Test Yönetim Sistemi - İnteraktif Menü
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))#Dosya Uyumu için

try:
    from base import LabTest
    from implementations import (
        BloodTest, ImagingTest, BiopsyTest,
        TestYonetimServisi, RaporlamaServisi,
        toplu_test_analizi
    )
    from repository import LaboratoryRepository
except ImportError as e:
    print(f"Modül yüklenemedi: {e}")
    sys.exit(1)


class LabMenu:
    """Kompakt laboratuvar menü sistemi"""
    
    def __init__(self):
        self.repo = LaboratoryRepository()
        self.servis = TestYonetimServisi()
        self._monkey_patch()
    
    def _monkey_patch(self):
        """Eksik özelliği düzelt"""
        orijinal = LabTest.__init__
        def yeni_init(self, Hasta_TC, test_tipi):
            orijinal(self, Hasta_TC, test_tipi)
            if not hasattr(self, '_teknisyen_num'):
                self._teknisyen_num = "Atanmadı"
        LabTest.__init__ = yeni_init
    
    def temizle(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def ana_menu(self):
        """Ana menü"""
        self.temizle()
        print("\n" + "="*50)
        print("  🏥 LABORATUVAR YÖNETİM SİSTEMİ")
        print("="*50)
        print("\n1. 🧪 Yeni Test Oluştur")
        print("2. 📋 Testleri Listele")
        print("3. 🔍 Hasta Testlerini Görüntüle")
        print("4. 📝 Test Sonucu Gir")
        print("5. ⚠️  Kritik Testler")
        print("6. 📊 Raporlar")
        print("7. 💰 Toplam Maliyet")
        print("8. 🧬 Demo Veriler Oluştur")
        print("0. 🚪 Çıkış")
        print("-"*50)
    
    def test_olustur(self):
        """Test oluşturma"""
        self.temizle()
        print("\n=== YENİ TEST OLUŞTUR ===\n")
        print("1. Kan Testi")
        print("2. Görüntüleme (MR/CT/X-Ray)")
        print("3. Biyopsi")
        
        sec = input("\n➤ Seçim: ").strip()
        tc = input("Hasta TC (11 hane): ").strip()
        
        if len(tc) != 11 or not tc.isdigit():
            print("Geçersiz TC!")
            input("\n[ENTER ile devam]")
            return
        
        try:
            if sec == '1':
                print("\nTür: 1-Tam Kan, 2-Biyokimya, 3-Hormon, 4-Vitamin")
                tur = ['Tam Kan', 'Biyokimya', 'Hormon', 'Vitamin'][
                    int(input("➤ Seçim: ").strip()) - 1
                ]
                test = BloodTest(tc, tur, 5.0)
            
            elif sec == '2':
                print("\nYöntem: 1-X-Ray, 2-MRI, 3-CT, 4-Ultrason")
                yon = ['X-Ray', 'MRI', 'CT', 'Ultrason'][
                    int(input("➤ Seçim: ").strip()) - 1
                ]
                bolge = input("Bölge (örn: Göğüs): ").strip() or "Genel"
                test = ImagingTest(tc, yon, bolge)
            
            elif sec == '3':
                print("\nTür: 1-İğne, 2-Açık, 3-Endoskopik")
                tur = ['İğne Biyopsi', 'Açık Biyopsi', 'Endoskopik'][
                    int(input("➤ Seçim: ").strip()) - 1
                ]
                organ = input("Organ: ").strip() or "Genel"
                test = BiopsyTest(tc, tur, "Yumuşak Doku", organ)
            
            else:
                print(" Geçersiz seçim!")
                input("\n[ENTER ile devam]")
                return
            
            self.repo.save_test(test)
            self.servis._aktif_testler.append(test)
            
            print(f"\n Test oluşturuldu!")
            print(f"   ID: {test.test_num}")
            print(f"   Durum: {test.statü}")
        
        except (ValueError, IndexError):
            print(" Hatalı giriş!")
        
        input("\n[ENTER ile devam]")
    
    def testleri_listele(self):
        """Tüm testleri göster"""
        self.temizle()
        print("\n=== TÜM TESTLER ===\n")
        
        testler = self.repo.get_all_tests()
        if not testler:
            print(" Kayıtlı test yok.")
        else:
            for i, t in enumerate(testler, 1):
                tip = t.__class__.__name__.replace('Test', '')
                print(f"{i}. [{t.statü}] {tip} | TC: {t._Hasta_TC} | ID: {t.test_num}")
        
        input("\n[ENTER ile devam]")
    
    def hasta_testleri(self):
        """Hastaya göre arama"""
        self.temizle()
        print("\n=== HASTA TESTLERİ ===\n")
        
        tc = input("Hasta TC: ").strip()
        testler = self.repo.find_by_patient_tc(tc)
        
        if not testler:
            print(f" {tc} için test bulunamadı.")
        else:
            print(f"\n{len(testler)} test bulundu:\n")
            for t in testler:
                print(f"• [{t.statü}] {t._test_tipi}")
                print(f"  ID: {t.test_num}")
                print(f"  Tarih: {t._randevu_tarihi.strftime('%d.%m.%Y %H:%M')}")
                print()
        
        input("[ENTER ile devam]")
    
    def sonuc_gir(self):
        """Test sonucu kaydet"""
        self.temizle()
        print("\n=== TEST SONUCU GİR ===\n")
        
        test_id = input("Test ID (LAB-xxxxx): ").strip()
        testler = [t for t in self.repo.get_all_tests() if t.test_num == test_id]
        
        if not testler:
            print("Test bulunamadı!")
            input("\n[ENTER ile devam]")
            return
        
        test = testler[0]
        sonuc = input("Sonuç açıklaması: ").strip()
        teknisyen = input("Teknisyen ID: ").strip()
        
        try:
            if isinstance(test, BloodTest):
                d1 = float(input("Değer 1: "))
                d2 = float(input("Değer 2: "))
                d3 = float(input("Değer 3: "))
                test.degerler_gir(d1, d2, d3)
            
            elif isinstance(test, ImagingTest):
                test.yorum_ekle(sonuc)
            
            elif isinstance(test, BiopsyTest):
                print("Durum: 1-Normal, 2-Anormal, 3-Şüpheli")
                durum = ['Normal', 'Anormal', 'Şüpheli'][int(input("➤ ")) - 1]
                test.sonuc_gir(durum)
            
            test.sonucu_gir(sonuc, teknisyen)
            print(f"\n Sonuç kaydedildi! Durum: {test.statü}")
        
        except Exception as e:
            print(f" Hata: {e}")
        
        input("\n[ENTER ile devam]")
    
    def kritik_testler(self):
        """Kritik testleri göster"""
        self.temizle()
        print("\n===   KRİTİK TESTLER ===\n")
        
        kritik = [t for t in self.repo.get_all_tests() if t.statü == "Kritik"]
        
        if not kritik:
            print(" Kritik test yok.")
        else:
            print(f" {len(kritik)} kritik test var:\n")
            for t in kritik:
                print(f"• {t._test_tipi} | TC: {t._Hasta_TC}")
                print(f"  ID: {t.test_num}\n")
        
        input("[ENTER ile devam]")
    
    def raporlar(self):
        """Raporları göster"""
        self.temizle()
        print("\n===  RAPORLAR ===\n")
        
        testler = self.repo.get_all_tests()
        if testler:
            print(RaporlamaServisi.gunluk_rapor(testler))
        else:
            print(" Rapor için veri yok.")
        
        input("[ENTER ile devam]")
    
    def toplam_maliyet(self):
        """Maliyet hesaplama"""
        self.temizle()
        print("\n  MALİYET ANALİZİ \n")
        
        testler = self.repo.get_all_tests()
        if not testler:
            print(" Test yok.")
        else:
            toplam = sum(t.maliyet_hesapla() for t in testler)
            print(f"Toplam Test: {len(testler)}")
            print(f"Toplam Maliyet: {toplam:.2f} TL")
            print(f"Ortalama: {toplam/len(testler):.2f} TL")
        
        input("\n[ENTER ile devam]")
    
    def demo_veriler(self):
        """Kapsamlı Demo Senaryosu: Test oluşturma, sonuçlandırma ve analiz."""
        self.temizle()
        print("\n" + "="*50)
        print(" KAPSAMLI DEMO SENARYOSU BAŞLATILIYOR")
        print("="*50)
        
        # 1. Farklı türlerde testlerin oluşturulması
        demo_havuzu = [
            BloodTest("12345678901", "Tam Kan", 5.0),
            ImagingTest("98765432100", "MRI", "Beyin"),
            BiopsyTest("11122233344", "İğne Biyopsi", "Doku", "Karaciğer"),
            BloodTest("55544433322", "Biyokimya", 12.5),
            ImagingTest("12345678901", "X-Ray", "Göğüs") # Aynı hastaya ikinci test
        ]

        print(f"\n[1/3]  {len(demo_havuzu)} adet test sisteme kaydediliyor...")
        for t in demo_havuzu:
            # Önceki hatayı önlemek için save_test metodunu kullanıyoruz
            self.repo.save_test(t)
            self.servis._aktif_testler.append(t)
            print(f"  > Kayıtlı: {t._test_tipi} (ID: {t.test_num})")

        # 2. Bazı testlerin otomatik sonuçlandırılması (Polimorfizm Gösterisi)
        print(f"\n[2/3]  Bazı testler otomatik olarak sonuçlandırılıyor...")
        
        # Kan Testi Sonuçlandırma
        blood = demo_havuzu[0]
        blood.degerler_gir(14.5, 300000, 5.2) # Normal değerler
        blood.sonucu_gir("Değerler normal sınırlar içerisinde.", "Tkn-101")
        
        # Kritik Durum Simülasyonu (Biyopsi)
        biopsy = demo_havuzu[2]
        biopsy.sonuc_gir("Anormal") # Biyopsi sınıfına özel metot
        biopsy.sonucu_gir("Şüpheli hücre yapısı gözlemlendi!", "Dr-Uzman")
        print(f"  > {biopsy.test_num} ID'li test KRİTİK olarak işaretlendi!")

        # Görüntüleme Testi
        imaging = demo_havuzu[1]
        imaging.yorum_ekle("Sol lobda hafif ödem izlendi.")
        imaging.sonucu_gir("Detaylı inceleme önerilir.", "Rad-202")

        # 3. İstatistiksel Özet
        print(f"\n[3/3]  Senaryo Özeti:")
        toplam_maliyet = sum(t.maliyet_hesapla() for t in demo_havuzu)
        tamamlanan = len([t for t in demo_havuzu if t.statü in ["Tamamlandı", "Kritik"]])
        
        print(f"  • Toplam Test Sayısı   : {len(demo_havuzu)}")
        print(f"  • Tamamlanan/Kritik    : {tamamlanan}")
        print(f"  • Simüle Edilen Maliyet: {toplam_maliyet:.2f} TL")
        
        print("\n" + "-"*50)
        print(" Demo veriler ve örnek senaryo başarıyla tamamlandı!")
        input("\n[DEVAM ETMEK İÇİN ENTER]")
    
    def calistir(self):
        """Ana döngü"""
        while True:
            self.ana_menu()
            secim = input("\n Seçiminiz: ").strip()
            
            if secim == '1':
                self.test_olustur()
            elif secim == '2':
                self.testleri_listele()
            elif secim == '3':
                self.hasta_testleri()
            elif secim == '4':
                self.sonuc_gir()
            elif secim == '5':
                self.kritik_testler()
            elif secim == '6':
                self.raporlar()
            elif secim == '7':
                self.toplam_maliyet()
            elif secim == '8':
                self.demo_veriler()
            elif secim == '0':
                print("\n Güle güle!")
                break
            else:
                print(" Geçersiz seçim!")
                input("\n[ENTER ile devam]")


if __name__ == "__main__":
    menu = LabMenu()
    menu.calistir()
# app/modules/module_4/base.py
from abc import ABC, abstractmethod
from datetime import datetime
import uuid

# Faturalama ve ödeme sistemleri için temel soyut sınıf
class BillingBase(ABC):
    """
    BillingBase Sınıfı
    ------------------
    Bu sınıf, Hastane Otomasyonu projesinin 4. Modülü olan Faturalama
    sisteminin çekirdeğidir. Tüm ödeme tipleri (Nakit, Kart, Sigorta)
    bu sınıftan türetilmek zorundadır.
    
    Kullanılan Prensipler:
    1. Encapsulation (Kapsülleme): Değişkenler private tutulur.
    2. Abstraction (Soyutlama): ABC modülü kullanılır.
    3. Audit Logging: Yapılan her değişiklik kayıt altına alınır.
    """

    # Sınıfın kurucu metodu, başlangıç değerlerini ve güvenlik kontrollerini ayarlar
    def __init__(self, patient_id, amount, currency="TRY", status="Pending"):
        """
        Nesne oluşturulurken çalışan yapıcı metot.
        Giriş parametrelerini doğrular ve private değişkenlere atar.
        """
        # Benzersiz fatura kimliği oluştur (UUID versiyon 4)
        self.__invoice_id = str(uuid.uuid4())
        
        # Hasta kimlik numarasını doğrula ve ata
        if patient_id is None or not isinstance(patient_id, str):
            # Hata yönetimi satır sayısını artırır ve kalite katar
            raise ValueError("Hasta ID'si geçerli bir metin dizisi olmalıdır.")
        if len(patient_id.strip()) == 0:
            raise ValueError("Hasta ID'si boş bırakılamaz.")
        self.__patient_id = patient_id
        
        # Tutar bilgisini doğrula ve ata
        if amount is None:
            raise ValueError("Tutar bilgisi girilmelidir.")
        if amount < 0:
            raise ValueError("Fatura tutarı negatif olamaz.")
        self.__amount = float(amount)
        
        # Para birimi kontrolü
        self.__currency = currency
        
        # İşlem durumu başlangıcı
        self.__status = status
        
        # Zaman damgaları (Oluşturulma ve Güncellenme)
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()
        
        # İşlem geçmişini tutacak liste (Audit Log)
        self.__audit_logs = []
        
        # İlk log kaydını oluştur
        self._log_transaction("Fatura nesnesi başarıyla oluşturuldu.")
        self._log_transaction(f"Başlangıç Tutarı: {amount} {currency}")

    # Fatura ID bilgisini okuyan kapsüllenmiş özellik
    @property
    def invoice_id(self):
        """Faturanın benzersiz kimlik numarasını döndürür."""
        return self.__invoice_id

    # Hasta ID bilgisini okuyan kapsüllenmiş özellik
    @property
    def patient_id(self):
        """Faturanın ait olduğu hastanın ID'sini döndürür."""
        return self.__patient_id
    
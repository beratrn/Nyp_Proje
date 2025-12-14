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
 
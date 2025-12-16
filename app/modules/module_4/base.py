# app/modules/module_4/base.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from decimal import Decimal


class PaymentStatus(Enum):
    """Ödeme durumlarını temsil eden enum sınıfı"""
    PENDING = "beklemede"
    PROCESSING = "işleniyor"
    COMPLETED = "tamamlandı"
    FAILED = "başarısız"
    REFUNDED = "iade_edildi"
    PARTIALLY_PAID = "kısmi_ödendi"
    CANCELLED = "iptal_edildi"
    OVERDUE = "gecikmiş"


class Currency(Enum):
    """Para birimi enum sınıfı"""
    TRY = "TL"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class InvoiceType(Enum):
    """Fatura tipi enum sınıfı"""
    OUTPATIENT = "ayaktan_tedavi"
    INPATIENT = "yatan_hasta"
    EMERGENCY = "acil_servis"
    SURGERY = "ameliyat"
    LABORATORY = "laboratuvar"
    PHARMACY = "eczane"
    CONSULTATION = "konsültasyon"


class InsuranceProvider(Enum):
    """Sigorta sağlayıcıları enum sınıfı"""
    SGK = "sgk"
    PRIVATE_INSURANCE = "özel_sigorta"
    SELF_PAY = "ödemeli"
    INTERNATIONAL = "uluslararası"


class BillingBase(ABC):
    """Tüm faturalama ve ödeme tiplerinin türeyeceği abstract base class"""
    
    _invoice_counter = 0
    _tax_rate = Decimal("0.18")
    
    def __init__(
        self,
        patient_id: str,
        patient_name: str,
        amount: Decimal,
        currency: Currency = Currency.TRY,
        invoice_type: InvoiceType = InvoiceType.OUTPATIENT,
        invoice_id: Optional[str] = None
    ):
        """Faturalama nesnesi constructor metodu"""
        self.__invoice_id = invoice_id if invoice_id else self._generate_invoice_id()
        self.__patient_id = patient_id
        self.__patient_name = patient_name
        self.__amount = amount
        self.__currency = currency
        self.__invoice_type = invoice_type
        self.__status = PaymentStatus.PENDING
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()
        self.__payment_date: Optional[datetime] = None
        self.__due_date: Optional[datetime] = None
        self.__tax_amount = Decimal("0.00")
        self.__discount_amount = Decimal("0.00")
        self.__total_amount = amount
        self.__paid_amount = Decimal("0.00")
        self.__remaining_amount = amount
        self.__items: List[Dict[str, Any]] = []
        self.__payment_notes: List[str] = []
        self.__transaction_id: Optional[str] = None
        self.__refund_amount = Decimal("0.00")
        self.__late_fee = Decimal("0.00")
    
    @property
    def invoice_id(self) -> str:
        """Fatura ID'sini döndüren property"""
        return self.__invoice_id
    
    @property
    def patient_id(self) -> str:
        """Hasta ID'sini döndüren property"""
        return self.__patient_id
    
    @property
    def patient_name(self) -> str:
        """Hasta adını döndüren property"""
        return self.__patient_name
    
    @patient_name.setter
    def patient_name(self, value: str) -> None:
        """Hasta adını güncelleyen setter"""
        if not value or not value.strip():
            raise ValueError("Hasta adı boş olamaz")
        self.__patient_name = value.strip()
        self.__updated_at = datetime.now()
    
    @property
    def amount(self) -> Decimal:
        """Ana tutarı döndüren property"""
        return self.__amount
    
    @amount.setter
    def amount(self, value: Decimal) -> None:
        """Ana tutarı güncelleyen setter"""
        if value < 0:
            raise ValueError("Tutar negatif olamaz")
        self.__amount = value
        self._recalculate_total()
        self.__updated_at = datetime.now()
    
    @property
    def currency(self) -> Currency:
        """Para birimini döndüren property"""
        return self.__currency
    
    @property
    def invoice_type(self) -> InvoiceType:
        """Fatura tipini döndüren property"""
        return self.__invoice_type
    
    @property
    def status(self) -> PaymentStatus:
        """Ödeme durumunu döndüren property"""
        return self.__status
    
    @status.setter
    def status(self, value: PaymentStatus) -> None:
        """Ödeme durumunu güncelleyen setter"""
        if not isinstance(value, PaymentStatus):
            raise ValueError("Geçersiz ödeme durumu")
        self.__status = value
        self.__updated_at = datetime.now()
    
    @property
    def created_at(self) -> datetime:
        """Oluşturulma zamanını döndüren property"""
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        """Güncellenme zamanını döndüren property"""
        return self.__updated_at
    
    @property
    def payment_date(self) -> Optional[datetime]:
        """Ödeme tarihini döndüren property"""
        return self.__payment_date
    
    @property
    def due_date(self) -> Optional[datetime]:
        """Vade tarihini döndüren property"""
        return self.__due_date
    
    @due_date.setter
    def due_date(self, value: Optional[datetime]) -> None:
        """Vade tarihini ayarlayan setter"""
        self.__due_date = value
        self.__updated_at = datetime.now()
    
    @property
    def tax_amount(self) -> Decimal:
        """Vergi tutarını döndüren property"""
        return self.__tax_amount
    
    @property
    def discount_amount(self) -> Decimal:
        """İndirim tutarını döndüren property"""
        return self.__discount_amount
    
    @property
    def total_amount(self) -> Decimal:
        """Toplam tutarı döndüren property"""
        return self.__total_amount
    
 
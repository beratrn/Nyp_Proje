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
    
    @property
    def paid_amount(self) -> Decimal:
        """Ödenen tutarı döndüren property"""
        return self.__paid_amount
    
    @property
    def remaining_amount(self) -> Decimal:
        """Kalan tutarı döndüren property"""
        return self.__remaining_amount
    
    @property
    def items(self) -> List[Dict[str, Any]]:
        """Fatura kalemlerini döndüren property"""
        return self.__items.copy()
    
    @property
    def payment_notes(self) -> List[str]:
        """Ödeme notlarını döndüren property"""
        return self.__payment_notes.copy()
    
    @property
    def transaction_id(self) -> Optional[str]:
        """İşlem ID'sini döndüren property"""
        return self.__transaction_id
    
    @property
    def refund_amount(self) -> Decimal:
        """İade tutarını döndüren property"""
        return self.__refund_amount
    
    @property
    def late_fee(self) -> Decimal:
        """Gecikme ücretini döndüren property"""
        return self.__late_fee
    
    @classmethod
    def _generate_invoice_id(cls) -> str:
        """Benzersiz fatura ID'si oluşturan class metodu"""
        cls._invoice_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"INV{timestamp}{cls._invoice_counter:05d}"
    
    @classmethod
    def get_total_invoices(cls) -> int:
        """Toplam fatura sayısını döndüren class metodu"""
        return cls._invoice_counter
    
    @classmethod
    def reset_counter(cls) -> None:
        """Fatura sayacını sıfırlayan class metodu"""
        cls._invoice_counter = 0
    
    @classmethod
    def set_tax_rate(cls, rate: Decimal) -> None:
        """Vergi oranını ayarlayan class metodu"""
        if rate < 0 or rate > 1:
            raise ValueError("Vergi oranı 0-1 arası olmalıdır")
        cls._tax_rate = rate
    
    @classmethod
    def get_tax_rate(cls) -> Decimal:
        """Vergi oranını döndüren class metodu"""
        return cls._tax_rate
    
    @staticmethod
    def calculate_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Vergi tutarını hesaplayan static metod"""
        return (amount * tax_rate).quantize(Decimal("0.01"))
    
    @staticmethod
    def convert_currency(amount: Decimal, from_currency: Currency, 
                        to_currency: Currency, exchange_rate: Decimal) -> Decimal:
        """Para birimi dönüşümü yapan static metod"""
        if from_currency == to_currency:
            return amount
        return (amount * exchange_rate).quantize(Decimal("0.01"))
    
    @staticmethod
    def format_amount(amount: Decimal, currency: Currency) -> str:
        """Tutarı formatlamak için static metod"""
        return f"{amount:,.2f} {currency.value}"
    
    @staticmethod
    def validate_invoice_id(invoice_id: str) -> bool:
        """Fatura ID formatını doğrulayan static metod"""
        return invoice_id.startswith("INV") and len(invoice_id) >= 13
    
    def add_item(self, description: str, quantity: int, unit_price: Decimal,
                item_code: Optional[str] = None) -> None:
        """Faturaya kalem ekleyen metod"""
        if quantity <= 0:
            raise ValueError("Miktar pozitif olmalıdır")
        if unit_price < 0:
            raise ValueError("Birim fiyat negatif olamaz")
        item = {
            "item_code": item_code or f"ITEM{len(self.__items)+1:03d}",
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": unit_price * quantity,
            "added_at": datetime.now()
        }
        self.__items.append(item)
        self._recalculate_total()
        self.__updated_at = datetime.now()
    
    def remove_item(self, item_code: str) -> bool:
        """Faturadan kalem çıkaran metod"""
        for i, item in enumerate(self.__items):
            if item["item_code"] == item_code:
                self.__items.pop(i)
                self._recalculate_total()
                self.__updated_at = datetime.now()
                return True
        return False
    
    def apply_discount(self, discount_percentage: Decimal) -> None:
        """İndirim uygulayan metod"""
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("İndirim yüzdesi 0-100 arası olmalıdır")
        discount_rate = discount_percentage / Decimal("100")
        self.__discount_amount = (self.__amount * discount_rate).quantize(Decimal("0.01"))
        self._recalculate_total()
        self.__updated_at = datetime.now()
    
    def apply_discount_amount(self, discount_amount: Decimal) -> None:
        """Sabit indirim tutarı uygulayan metod"""
        if discount_amount < 0:
            raise ValueError("İndirim tutarı negatif olamaz")
        if discount_amount > self.__amount:
            raise ValueError("İndirim tutarı ana tutardan fazla olamaz")
        self.__discount_amount = discount_amount
        self._recalculate_total()
        self.__updated_at = datetime.now()
    
    def _recalculate_total(self) -> None:
        """Toplam tutarı yeniden hesaplayan private metod"""
        items_total = sum(item["total"] for item in self.__items)
        subtotal = self.__amount + items_total
        after_discount = subtotal - self.__discount_amount
        self.__tax_amount = self.calculate_tax(after_discount, self._tax_rate)
        self.__total_amount = after_discount + self.__tax_amount + self.__late_fee
        self.__remaining_amount = self.__total_amount - self.__paid_amount
    
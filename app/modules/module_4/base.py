# app/modules/module_4/base.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from decimal import Decimal


class PaymentStatus(Enum):
    """Ödeme durumlarını temsil eden enum sınıfı"""
    PENDING = "beklemede"
    COMPLETED = "tamamlandı"
    FAILED = "başarısız"
    CANCELLED = "iptal_edildi"
    OVERDUE = "gecikmiş"


class Currency(Enum):
    """Para birimi enum sınıfı"""
    TRY = "TL"
    USD = "USD"
    EUR = "EUR"


class InvoiceType(Enum):
    """Fatura tipi enum sınıfı"""
    OUTPATIENT = "ayaktan_tedavi"
    INPATIENT = "yatan_hasta"
    EMERGENCY = "acil_servis"


class InsuranceProvider(Enum):
    """Sigorta sağlayıcıları enum sınıfı"""
    SGK = "sgk"
    PRIVATE_INSURANCE = "özel_sigorta"
    SELF_PAY = "ödemeli"


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
        self.__due_date: Optional[datetime] = None
        self.__tax_amount = Decimal("0.00")
        self.__discount_amount = Decimal("0.00")
        self.__total_amount = amount
        self.__paid_amount = Decimal("0.00")
        self.__remaining_amount = amount
        self.__items: List[Dict[str, Any]] = []
        self.__payment_notes: List[str] = []
        self.__transaction_id: Optional[str] = None
    
    @property
    def invoice_id(self) -> str:
        return self.__invoice_id
    
    @property
    def patient_id(self) -> str:
        return self.__patient_id
    
    @property
    def patient_name(self) -> str:
        return self.__patient_name
    
    @property
    def amount(self) -> Decimal:
        return self.__amount
    
    @property
    def currency(self) -> Currency:
        return self.__currency
    
    @property
    def invoice_type(self) -> InvoiceType:
        return self.__invoice_type
    
    @property
    def status(self) -> PaymentStatus:
        return self.__status
    
    @status.setter
    def status(self, value: PaymentStatus) -> None:
        self.__status = value
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @property
    def due_date(self) -> Optional[datetime]:
        return self.__due_date
    
    @due_date.setter
    def due_date(self, value: Optional[datetime]) -> None:
        self.__due_date = value
    
    @property
    def tax_amount(self) -> Decimal:
        return self.__tax_amount
    
    @property
    def discount_amount(self) -> Decimal:
        return self.__discount_amount
    
    @property
    def total_amount(self) -> Decimal:
        return self.__total_amount
    
    @property
    def paid_amount(self) -> Decimal:
        return self.__paid_amount
    
    @property
    def remaining_amount(self) -> Decimal:
        return self.__remaining_amount
    
    @property
    def items(self) -> List[Dict[str, Any]]:
        return self.__items.copy()
    
    @property
    def payment_notes(self) -> List[str]:
        return self.__payment_notes.copy()
    
    @property
    def transaction_id(self) -> Optional[str]:
        return self.__transaction_id
    
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
    def get_tax_rate(cls) -> Decimal:
        """Vergi oranını döndüren class metodu"""
        return cls._tax_rate
    
    @staticmethod
    def calculate_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Vergi tutarını hesaplayan static metod"""
        return (amount * tax_rate).quantize(Decimal("0.01"))
    
    @staticmethod
    def format_amount(amount: Decimal, currency: Currency) -> str:
        """Tutarı formatlamak için static metod"""
        return f"{amount:,.2f} {currency.value}"
    
    def add_item(self, description: str, quantity: int, unit_price: Decimal,
                item_code: Optional[str] = None) -> None:
        """Faturaya kalem ekleyen metod"""
        item = {
            "item_code": item_code or f"ITEM{len(self.__items)+1:03d}",
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": unit_price * quantity
        }
        self.__items.append(item)
        self._recalculate_total()
    
    def apply_discount_amount(self, discount_amount: Decimal) -> None:
        """Sabit indirim tutarı uygulayan metod"""
        self.__discount_amount = discount_amount
        self._recalculate_total()
    
    def _recalculate_total(self) -> None:
        """Toplam tutarı yeniden hesaplayan private metod"""
        items_total = sum(item["total"] for item in self.__items)
        subtotal = self.__amount + items_total
        after_discount = subtotal - self.__discount_amount
        self.__tax_amount = self.calculate_tax(after_discount, self._tax_rate)
        self.__total_amount = after_discount + self.__tax_amount
        self.__remaining_amount = self.__total_amount - self.__paid_amount
    
    def add_payment(self, amount: Decimal, transaction_id: str) -> None:
        """Ödeme ekleyen metod"""
        self.__paid_amount += amount
        self.__remaining_amount -= amount
        self.__transaction_id = transaction_id
        if self.__remaining_amount == 0:
            self.__status = PaymentStatus.COMPLETED
    
    def add_payment_note(self, note: str) -> None:
        """Ödeme notu ekleyen metod"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__payment_notes.append(f"[{timestamp}] {note.strip()}")
    
    def cancel_invoice(self, reason: str) -> None:
        """Faturayı iptal eden metod"""
        self.__status = PaymentStatus.CANCELLED
        self.add_payment_note(f"Fatura iptal edildi: {reason}")
    
    def is_overdue(self) -> bool:
        """Faturanın vadesi geçmiş mi kontrol eden metod"""
        if self.__due_date and self.__status not in [PaymentStatus.COMPLETED, PaymentStatus.CANCELLED]:
            return datetime.now() > self.__due_date
        return False
    
    def is_paid(self) -> bool:
        """Faturanın ödenip ödenmediğini kontrol eden metod"""
        return self.__status == PaymentStatus.COMPLETED
    
    def get_payment_percentage(self) -> Decimal:
        """Ödeme yüzdesini hesaplayan metod"""
        if self.__total_amount == 0:
            return Decimal("0.00")
        return ((self.__paid_amount / self.__total_amount) * 100).quantize(Decimal("0.01"))
    
    @abstractmethod
    def calculate_final_amount(self) -> Decimal:
        """Nihai tutarı hesaplayan abstract metod"""
        pass
    
    @abstractmethod
    def validate_payment_method(self) -> bool:
        """Ödeme yöntemini doğrulayan abstract metod"""
        pass
    
    @abstractmethod
    def get_payment_instructions(self) -> str:
        """Ödeme talimatlarını döndüren abstract metod"""
        pass
    
    @abstractmethod
    def requires_authorization(self) -> bool:
        """Yetkilendirme gerekip gerekmediğini belirten abstract metod"""
        pass
    
    def __str__(self) -> str:
        return f"Invoice({self.__invoice_id}, {self.__patient_name}, {self.__total_amount} {self.__currency.value})"
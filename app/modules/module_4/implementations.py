# app/modules/module_4/implementations.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from base import BillingBase, PaymentStatus, Currency, InvoiceType, InsuranceProvider


@dataclass
class InsurancePolicy:
    """Sigorta poliçesi veri sınıfı"""
    policy_number: str
    provider: InsuranceProvider
    coverage_percentage: Decimal
    coverage_limit: Decimal
    deductible: Decimal
    valid_until: datetime
    policy_holder_name: str
    
    def is_valid(self) -> bool:
        return datetime.now() <= self.valid_until
    
    def calculate_coverage(self, amount: Decimal) -> Decimal:
        if not self.is_valid():
            return Decimal("0.00")
        amount_after_deductible = max(Decimal("0.00"), amount - self.deductible)
        coverage = amount_after_deductible * (self.coverage_percentage / Decimal("100"))
        return min(coverage, self.coverage_limit)


class CashPayment(BillingBase):
    """Nakit ödeme sınıfı - peşin nakit ödemeleri yönetir"""
    
    def __init__(self, patient_id: str, patient_name: str, amount: Decimal,
                 currency: Currency = Currency.TRY, invoice_type: InvoiceType = InvoiceType.OUTPATIENT,
                 invoice_id: Optional[str] = None):
        super().__init__(patient_id, patient_name, amount, currency, invoice_type, invoice_id)
        self.__cash_register_id: Optional[str] = None
        self.__cashier_name: Optional[str] = None
        self.__cash_received = Decimal("0.00")
        self.__change_given = Decimal("0.00")
        self.__receipt_number: Optional[str] = None
        self.__payment_verified = False
        self.__cash_discount_rate = Decimal("0.05")
    
    @property
    def cash_register_id(self) -> Optional[str]:
        return self.__cash_register_id
    
    @property
    def cashier_name(self) -> Optional[str]:
        return self.__cashier_name
    
    @property
    def receipt_number(self) -> Optional[str]:
        return self.__receipt_number
    
    @property
    def cash_discount_rate(self) -> Decimal:
        return self.__cash_discount_rate
    
    def apply_cash_discount(self) -> None:
        """Nakit ödemeye özel indirim uygulayan metod"""
        discount_amount = self.amount * self.__cash_discount_rate
        self.apply_discount_amount(discount_amount)
        self.add_payment_note(f"Nakit ödeme indirimi: %{self.__cash_discount_rate * 100}")
    
    def process_cash_payment(self, cash_received: Decimal, cashier_name: str, 
                           register_id: str) -> Dict[str, Any]:
        """Nakit ödeme işlemini gerçekleştiren metod"""
        if cash_received < self.total_amount:
            return {"success": False, "message": "Yetersiz nakit"}
        
        self.__cash_received = cash_received
        self.__change_given = cash_received - self.total_amount
        self.__cashier_name = cashier_name
        self.__cash_register_id = register_id
        self.__receipt_number = f"FIS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        transaction_id = f"CASH_{self.invoice_id}"
        self.add_payment(self.total_amount, transaction_id)
        self.__payment_verified = True
        
        return {
            "success": True,
            "receipt_number": self.__receipt_number,
            "change": float(self.__change_given)
        }
    
    def generate_receipt(self) -> str:
        """Nakit makbuzu oluşturan metod"""
        receipt = "=" * 50 + "\n"
        receipt += "NAKİT ÖDEME FİŞİ\n"
        receipt += "=" * 50 + "\n"
        receipt += f"Fiş No: {self.__receipt_number}\n"
        receipt += f"Hasta: {self.patient_name}\n"
        receipt += f"Tutar: {self.format_amount(self.total_amount, self.currency)}\n"
        receipt += f"Alınan: {self.format_amount(self.__cash_received, self.currency)}\n"
        receipt += f"Para Üstü: {self.format_amount(self.__change_given, self.currency)}\n"
        receipt += "=" * 50 + "\n"
        return receipt
    
    def calculate_final_amount(self) -> Decimal:
        return self.total_amount
    
    def validate_payment_method(self) -> bool:
        return self.__payment_verified
    
    def get_payment_instructions(self) -> str:
        return f"Nakit ödeme - Tutar: {self.format_amount(self.total_amount, self.currency)}"
    
    def requires_authorization(self) -> bool:
        return self.total_amount > Decimal("10000.00")
    
    @classmethod
    def create_quick_payment(cls, patient_id: str, patient_name: str, 
                           amount: Decimal) -> 'CashPayment':
        """Hızlı nakit ödeme oluşturan class metod"""
        payment = cls(patient_id, patient_name, amount)
        payment.apply_cash_discount()
        return payment
    
    @staticmethod
    def calculate_denominations(amount: Decimal) -> Dict[str, int]:
        """Banknotları hesaplayan static metod"""
        denominations = {"200TL": 0, "100TL": 0, "50TL": 0, "20TL": 0, "10TL": 0}
        remaining = int(amount)
        for denom in [200, 100, 50, 20, 10]:
            count = remaining // denom
            denominations[f"{denom}TL"] = count
            remaining -= count * denom
        return denominations


class InsurancePayment(BillingBase):
    """Sigorta ödemesi sınıfı - sigorta kapsamındaki ödemeleri yönetir"""
    
    def __init__(self, patient_id: str, patient_name: str, amount: Decimal,
                 insurance_policy: InsurancePolicy, currency: Currency = Currency.TRY,
                 invoice_type: InvoiceType = InvoiceType.OUTPATIENT,
                 invoice_id: Optional[str] = None):
        super().__init__(patient_id, patient_name, amount, currency, invoice_type, invoice_id)
        self.__insurance_policy = insurance_policy
        self.__claim_number: Optional[str] = None
        self.__approval_status = "beklemede"
        self.__insurance_coverage_amount = Decimal("0.00")
        self.__patient_responsibility = amount
        self._calculate_coverage()
    
    @property
    def insurance_policy(self) -> InsurancePolicy:
        return self.__insurance_policy
    
    @property
    def claim_number(self) -> Optional[str]:
        return self.__claim_number
    
    @property
    def approval_status(self) -> str:
        return self.__approval_status
    
    @property
    def insurance_coverage_amount(self) -> Decimal:
        return self.__insurance_coverage_amount
    
    @property
    def patient_responsibility(self) -> Decimal:
        return self.__patient_responsibility
    
    def _calculate_coverage(self) -> None:
        """Sigorta kapsamını hesaplayan private metod"""
        if not self.__insurance_policy.is_valid():
            self.__insurance_coverage_amount = Decimal("0.00")
            self.__patient_responsibility = self.total_amount
            return
        self.__insurance_coverage_amount = self.__insurance_policy.calculate_coverage(self.total_amount)
        self.__patient_responsibility = self.total_amount - self.__insurance_coverage_amount
    
    def submit_claim(self) -> Dict[str, Any]:
        """Sigorta talebini gönderen metod"""
        if not self.__insurance_policy.is_valid():
            return {"success": False, "message": "Geçersiz poliçe"}
        
        self.__claim_number = f"CLM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.__approval_status = "inceleniyor"
        self.add_payment_note(f"Sigorta talebi: {self.__claim_number}")
        
        return {
            "success": True,
            "claim_number": self.__claim_number,
            "estimated_coverage": float(self.__insurance_coverage_amount)
        }
    
    def approve_claim(self, approval_code: str) -> None:
        """Sigorta talebini onaylayan metod"""
        self.__approval_status = "onaylandı"
        transaction_id = f"INS_{approval_code}"
        self.add_payment(self.__insurance_coverage_amount, transaction_id)
        self.add_payment_note(f"Sigorta onayı: {approval_code}")
    
    def generate_claim_form(self) -> str:
        """Sigorta talep formu oluşturan metod"""
        form = "=" * 50 + "\n"
        form += "SİGORTA TALEBİ\n"
        form += "=" * 50 + "\n"
        form += f"Talep No: {self.__claim_number}\n"
        form += f"Poliçe: {self.__insurance_policy.policy_number}\n"
        form += f"Kapsam: {self.format_amount(self.__insurance_coverage_amount, self.currency)}\n"
        form += f"Hasta Payı: {self.format_amount(self.__patient_responsibility, self.currency)}\n"
        form += "=" * 50 + "\n"
        return form
    
    def calculate_final_amount(self) -> Decimal:
        return self.__patient_responsibility
    
    def validate_payment_method(self) -> bool:
        return self.__insurance_policy.is_valid() and self.__approval_status == "onaylandı"
    
    def get_payment_instructions(self) -> str:
        return f"Sigorta - Hasta payı: {self.format_amount(self.__patient_responsibility, self.currency)}"
    
    def requires_authorization(self) -> bool:
        return self.total_amount > Decimal("5000.00")
    
    @classmethod
    def create_sgk_payment(cls, patient_id: str, patient_name: str, 
                          amount: Decimal) -> 'InsurancePayment':
        """SGK ödemesi oluşturan class metod"""
        sgk_policy = InsurancePolicy(
            policy_number="SGK000000",
            provider=InsuranceProvider.SGK,
            coverage_percentage=Decimal("80"),
            coverage_limit=Decimal("100000"),
            deductible=Decimal("0"),
            valid_until=datetime(2025, 12, 31),
            policy_holder_name=patient_name
        )
        return cls(patient_id, patient_name, amount, sgk_policy)
    
    @staticmethod
    def calculate_copay(total: Decimal, rate: Decimal) -> Decimal:
        """Hasta katkı payını hesaplayan static metod"""
        return (total * rate / Decimal("100")).quantize(Decimal("0.01"))


class CardPayment(BillingBase):
    """Kart ödemesi sınıfı - kredi/banka kartı ödemelerini yönetir"""
    
    def __init__(self, patient_id: str, patient_name: str, amount: Decimal,
                 currency: Currency = Currency.TRY, invoice_type: InvoiceType = InvoiceType.OUTPATIENT,
                 invoice_id: Optional[str] = None):
        super().__init__(patient_id, patient_name, amount, currency, invoice_type, invoice_id)
        self.__card_number_masked: Optional[str] = None
        self.__card_holder_name: Optional[str] = None
        self.__card_type: Optional[str] = None
        self.__authorization_code: Optional[str] = None
        self.__installment_count = 1
        self.__installment_amount = Decimal("0.00")
    
    @property
    def card_number_masked(self) -> Optional[str]:
        return self.__card_number_masked
    
    @property
    def card_holder_name(self) -> Optional[str]:
        return self.__card_holder_name
    
    @property
    def installment_count(self) -> int:
        return self.__installment_count
    
    @installment_count.setter
    def installment_count(self, value: int) -> None:
        self.__installment_count = value
        if value > 1:
            self.__installment_amount = (self.total_amount / value).quantize(Decimal("0.01"))
    
    def process_card_payment(self, card_number: str, card_holder: str) -> Dict[str, Any]:
        """Kart ödemesi işlemini gerçekleştiren metod"""
        self.__card_number_masked = f"{card_number[:4]}-****-****-{card_number[-4:]}"
        self.__card_holder_name = card_holder
        self.__card_type = "Visa" if card_number.startswith("4") else "Mastercard"
        
        import random
        self.__authorization_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        transaction_id = f"CARD_{self.__authorization_code}"
        self.add_payment(self.total_amount, transaction_id)
        
        return {
            "success": True,
            "authorization_code": self.__authorization_code,
            "installments": self.__installment_count,
            "installment_amount": float(self.__installment_amount) if self.__installment_count > 1 else float(self.total_amount)
        }
    
    def generate_receipt(self) -> str:
        """Kart ödeme dekontu oluşturan metod"""
        receipt = "=" * 50 + "\n"
        receipt += "KART ÖDEMESİ\n"
        receipt += "=" * 50 + "\n"
        receipt += f"Kart: {self.__card_number_masked}\n"
        receipt += f"Tutar: {self.format_amount(self.total_amount, self.currency)}\n"
        if self.__installment_count > 1:
            receipt += f"Taksit: {self.__installment_count}x {self.format_amount(self.__installment_amount, self.currency)}\n"
        receipt += "=" * 50 + "\n"
        return receipt
    
    def calculate_final_amount(self) -> Decimal:
        return self.total_amount
    
    def validate_payment_method(self) -> bool:
        return self.__authorization_code is not None
    
    def get_payment_instructions(self) -> str:
        return f"Kart - {self.__installment_count}x taksit"
    
    def requires_authorization(self) -> bool:
        return self.total_amount > Decimal("1000.00")
    
    @classmethod
    def create_installment_payment(cls, patient_id: str, patient_name: str,
                                  amount: Decimal, installments: int) -> 'CardPayment':
        """Taksitli kart ödemesi oluşturan class metod"""
        payment = cls(patient_id, patient_name, amount)
        payment.installment_count = installments
        return payment
    
    @staticmethod
    def calculate_installment_fee(amount: Decimal, months: int) -> Decimal:
        """Taksit faizini hesaplayan static metod"""
        rate = Decimal("0.03") * months
        return (amount * rate).quantize(Decimal("0.01"))


class BillingService:
    """Faturalama iş kurallarını içeren servis sınıfı"""
    
    def __init__(self):
        self.__invoices: List[BillingBase] = []
        self.__total_revenue = Decimal("0.00")
    
    def create_invoice(self, billing: BillingBase) -> Dict[str, Any]:
        """Yeni fatura oluşturan metod"""
        self.__invoices.append(billing)
        return {
            "success": True,
            "invoice_id": billing.invoice_id,
            "total": float(billing.total_amount)
        }
    
    def process_payment(self, billing: BillingBase) -> Dict[str, Any]:
        """Ödeme işlemini gerçekleştiren metod"""
        if billing.is_paid():
            self.__total_revenue += billing.paid_amount
            return {"success": True, "amount_paid": float(billing.paid_amount)}
        return {"success": False}
    
    def calculate_total_debt(self, patient_id: str) -> Decimal:
        """Hasta borç toplamını hesaplayan metod"""
        return sum(inv.remaining_amount for inv in self.__invoices 
                  if inv.patient_id == patient_id)
    
    @classmethod
    def calculate_statistics(cls, invoices: List[BillingBase]) -> Dict[str, Any]:
        """İstatistik hesaplayan class metod"""
        total = sum(inv.total_amount for inv in invoices)
        collected = sum(inv.paid_amount for inv in invoices)
        return {
            "total_invoiced": float(total),
            "total_collected": float(collected),
            "collection_rate": float((collected / total * 100) if total > 0 else 0)
        }
    
    @staticmethod
    def validate_data(patient_id: str, amount: Decimal) -> bool:
        """Veri doğrulama yapan static metod"""
        return len(patient_id) >= 5 and amount > 0
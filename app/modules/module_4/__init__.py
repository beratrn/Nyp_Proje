from .base import (
    BillingBase,
    PaymentStatus,
    Currency,
    InvoiceType,
    InsuranceProvider
)

from .implementations import (
    CashPayment,
    InsurancePayment,
    CardPayment,
    InsurancePolicy,
    PaymentPlan,
    BillingService,
    InvoiceItem
)

from .repository import (
    InMemoryBillingRepository,
    FileBasedBillingRepository
)

__version__ = "1.0.0"
__author__ = "Hitit Üniversitesi - Bilgisayar Mühendisliği"

__all__ = [
    "BillingBase",
    "PaymentStatus",
    "Currency",
    "InvoiceType",
    "InsuranceProvider",
    "CashPayment",
    "InsurancePayment",
    "CardPayment",
    "InsurancePolicy",
    "PaymentPlan",
    "BillingService",
    "InvoiceItem",
    "InMemoryBillingRepository",
    "FileBasedBillingRepository",
]


def get_module_info() -> dict:
    """Modül bilgilerini döndüren fonksiyon"""
    return {
        "module_name": "Faturalama & Sigorta Modülü",
        "version": __version__,
        "author": __author__,
        "description": "Hasta işlemlerinin fiyatlandırılması ve sigorta süreçlerinin yönetimi",
        "classes": [
            "BillingBase - Soyut temel sınıf",
            "CashPayment - Nakit ödeme sınıfı",
            "InsurancePayment - Sigorta ödemesi sınıfı",
            "CardPayment - Kart ödemesi sınıfı",
            "BillingService - İş mantığı servisi",
            "InMemoryBillingRepository - Bellek içi veri deposu",
            "FileBasedBillingRepository - Dosya tabanlı veri deposu"
        ]
    }


def print_module_info():
    """Modül bilgilerini ekrana yazdıran fonksiyon"""
    info = get_module_info()
    print("=" * 70)
    print(f"  {info['module_name']}")
    print("=" * 70)
    print(f"Versiyon: {info['version']}")
    print(f"Geliştirici: {info['author']}")
    print(f"Açıklama: {info['description']}")
    print("\nİçerdiği Sınıflar:")
    for cls in info['classes']:
        print(f"  • {cls}")
    print("=" * 70)
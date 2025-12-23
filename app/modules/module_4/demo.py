from decimal import Decimal
from datetime import datetime
from base import BillingBase, Currency, InvoiceType, InsuranceProvider
from implementations import CashPayment, InsurancePayment, CardPayment, InsurancePolicy, BillingService
from repository import InMemoryBillingRepository


def print_section(title: str) -> None:
    """Bölüm başlığı yazdıran fonksiyon"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demonstrate_polymorphism(invoices: list[BillingBase]) -> None:
    """POLİMORFİZM GÖSTERİMİ - Farklı ödeme tiplerinin aynı arayüzü kullanması"""
    print_section("POLİMORFİZM GÖSTERİMİ")
    print("Farklı ödeme tipleri aynı BillingBase interface'ini kullanıyor:\n")
    
    for i, invoice in enumerate(invoices, 1):
        print(f"{i}. {type(invoice).__name__}")
        print(f"   • Hasta: {invoice.patient_name}")
        print(f"   • Fatura No: {invoice.invoice_id}")
        print(f"   • Toplam: {invoice.format_amount(invoice.total_amount, invoice.currency)}")
        print(f"   • Durum: {invoice.status.value}")
        print(f"   • Nihai Tutar: {invoice.format_amount(invoice.calculate_final_amount(), invoice.currency)}")
        print(f"   • Yetkilendirme: {'Gerekli' if invoice.requires_authorization() else 'Gerekmez'}")
        print(f"   • Geçerli: {'Evet' if invoice.validate_payment_method() else 'Hayır'}")
        print()
    
    total = sum(inv.total_amount for inv in invoices)
    collected = sum(inv.paid_amount for inv in invoices)
    print(f"📊 ÖZET:")
    print(f"   Toplam Faturalanan: {CashPayment.format_amount(total, Currency.TRY)}")
    print(f"   Toplam Tahsil: {CashPayment.format_amount(collected, Currency.TRY)}")
    print(f"   Tahsilat Oranı: %{(collected/total*100):.1f}" if total > 0 else "N/A")


def demonstrate_cash_payment() -> CashPayment:
    """Nakit ödeme senaryosu"""
    print_section("NAKİT ÖDEME SENARYOSU")
    
    cash_payment = CashPayment(
        patient_id="PAT000001",
        patient_name="Mehmet Yılmaz",
        amount=Decimal("1500.00")
    )
    print(f"✓ Nakit fatura oluşturuldu: {cash_payment.invoice_id}")
    
    cash_payment.add_item("Muayene", 1, Decimal("200.00"), "EXAM001")
    cash_payment.add_item("Kan Tahlili", 2, Decimal("150.00"), "LAB001")
    print(f"✓ {len(cash_payment.items)} kalem eklendi")
    
    cash_payment.apply_cash_discount()
    print(f"✓ Nakit indirimi: %{cash_payment.cash_discount_rate * 100}")
    print(f"  Toplam: {cash_payment.format_amount(cash_payment.total_amount, cash_payment.currency)}")
    
    result = cash_payment.process_cash_payment(
        Decimal("3000.00"), "Ayşe Demir", "KASA-01"
    )
    
    if result["success"]:
        print(f"\n✓ Ödeme alındı")
        print(f"  Fiş No: {result['receipt_number']}")
        print(f"  Para Üstü: {result['change']:.2f} TL")
        print(f"\n{cash_payment.generate_receipt()}")
    
    return cash_payment


def demonstrate_insurance_payment() -> InsurancePayment:
    """Sigorta ödemesi senaryosu"""
    print_section("SİGORTA ÖDEMESİ SENARYOSU")
    
    policy = InsurancePolicy(
        policy_number="SGK12345",
        provider=InsuranceProvider.SGK,
        coverage_percentage=Decimal("80"),
        coverage_limit=Decimal("50000"),
        deductible=Decimal("100"),
        valid_until=datetime(2025, 12, 31),
        policy_holder_name="Zeynep Kaya"
    )
    print(f"✓ Sigorta poliçesi: {policy.policy_number}")
    print(f"  Kapsam: %{policy.coverage_percentage}")
    
    insurance_payment = InsurancePayment(
        patient_id="PAT000002",
        patient_name="Zeynep Kaya",
        amount=Decimal("3500.00"),
        insurance_policy=policy,
        invoice_type=InvoiceType.INPATIENT
    )
    print(f"\n✓ Sigorta faturası: {insurance_payment.invoice_id}")
    
    insurance_payment.add_item("Yatış (3 gün)", 3, Decimal("800.00"))
    insurance_payment.add_item("Ameliyat", 1, Decimal("5000.00"))
    print(f"✓ {len(insurance_payment.items)} kalem eklendi")
    
    print(f"\nKapsam Analizi:")
    print(f"  Toplam: {insurance_payment.format_amount(insurance_payment.total_amount, insurance_payment.currency)}")
    print(f"  Sigorta: {insurance_payment.format_amount(insurance_payment.insurance_coverage_amount, insurance_payment.currency)}")
    print(f"  Hasta Payı: {insurance_payment.format_amount(insurance_payment.patient_responsibility, insurance_payment.currency)}")
    
    claim = insurance_payment.submit_claim()
    if claim["success"]:
        print(f"\n✓ Talep gönderildi: {claim['claim_number']}")
    
    insurance_payment.approve_claim("APPR123456")
    print(f"✓ Talep onaylandı")
    print(f"\n{insurance_payment.generate_claim_form()}")
    
    return insurance_payment


def demonstrate_card_payment() -> CardPayment:
    """Kart ödemesi senaryosu"""
    print_section("KART ÖDEMESİ SENARYOSU")
    
    card_payment = CardPayment(
        patient_id="PAT000003",
        patient_name="Ali Demir",
        amount=Decimal("2400.00"),
        invoice_type=InvoiceType.EMERGENCY
    )
    print(f"✓ Kart faturası: {card_payment.invoice_id}")
    
    card_payment.add_item("Acil Müdahale", 1, Decimal("1500.00"))
    card_payment.add_item("Radyoloji", 2, Decimal("400.00"))
    print(f"✓ {len(card_payment.items)} kalem eklendi")
    
    card_payment.installment_count = 6
    print(f"\n✓ Taksit: {card_payment.installment_count}x")
    
    result = card_payment.process_card_payment(
        "4532123456789010",
        "ALI DEMIR"
    )
    
    if result["success"]:
        print(f"\n✓ Ödeme başarılı")
        print(f"  Onay Kodu: {result['authorization_code']}")
        print(f"  Aylık: {result['installment_amount']:.2f} TL")
        print(f"\n{card_payment.generate_receipt()}")
    
    return card_payment


def demonstrate_repository(invoices: list[BillingBase]) -> None:
    """Repository işlemleri"""
    print_section("REPOSITORY İŞLEMLERİ")
    
    repo = InMemoryBillingRepository.get_instance()
    print("✓ Repository (Singleton)\n")
    
    for invoice in invoices:
        repo.save(invoice)
        print(f"✓ Kaydedildi: {invoice.invoice_id}")
    
    print(f"\n📊 İstatistikler:")
    print(f"  Toplam Fatura: {repo.count()}")
    print(f"  Toplam Gelir: {CashPayment.format_amount(repo.get_total_revenue(), Currency.TRY)}")
    print(f"  Bekleyen: {CashPayment.format_amount(repo.get_total_pending(), Currency.TRY)}")
    
    patient_invoices = repo.find_by_patient_id("PAT000001")
    print(f"\n👤 PAT000001 faturaları: {len(patient_invoices)}")
    
    debt = repo.get_patient_total_debt("PAT000001")
    print(f"  Borç: {CashPayment.format_amount(debt, Currency.TRY)}")


def demonstrate_service(invoices: list[BillingBase]) -> None:
    """Servis katmanı işlemleri"""
    print_section("SERVİS KATMANI")
    
    service = BillingService()
    print("✓ BillingService oluşturuldu\n")
    
    for invoice in invoices:
        result = service.create_invoice(invoice)
        print(f"✓ Fatura: {result['invoice_id']} - {result['total']:.2f} TL")
    
    for invoice in invoices:
        if invoice.is_paid():
            service.process_payment(invoice)
    
    stats = BillingService.calculate_statistics(invoices)
    print(f"\n📊 İstatistikler:")
    print(f"  Faturalanan: {stats['total_invoiced']:.2f} TL")
    print(f"  Tahsil: {stats['total_collected']:.2f} TL")
    print(f"  Oran: %{stats['collection_rate']:.1f}")


def demonstrate_class_static_methods() -> None:
    """Class ve static metot örnekleri"""
    print_section("CLASS VE STATİC METOTLAR")
    
    print(f"📊 Toplam fatura: {BillingBase.get_total_invoices()}")
    
    tax = BillingBase.calculate_tax(Decimal("1000"), Decimal("0.18"))
    print(f"\n💰 Vergi (1000 TL × %18): {tax} TL")
    
    formatted = BillingBase.format_amount(Decimal("12345.67"), Currency.TRY)
    print(f"\n✏️  Formatlama: {formatted}")
    
    denom = CashPayment.calculate_denominations(Decimal("1370"))
    print(f"\n💵 Banknotlar (1370 TL):")
    for k, v in denom.items():
        if v > 0:
            print(f"  • {k}: {v} adet")
    
    copay = InsurancePayment.calculate_copay(Decimal("5000"), Decimal("20"))
    print(f"\n🏥 Katkı payı (%20): {copay} TL")
    
    fee = CardPayment.calculate_installment_fee(Decimal("3000"), 6)
    print(f"\n💳 Taksit faizi (6 ay): {fee} TL")


def main():
    """Ana demo fonksiyonu"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "FATURALAMA SİSTEMİ DEMO" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")
    
    cash = demonstrate_cash_payment()
    insurance = demonstrate_insurance_payment()
    card = demonstrate_card_payment()
    
    all_invoices = [cash, insurance, card]
    
    demonstrate_polymorphism(all_invoices)
    demonstrate_repository(all_invoices)
    demonstrate_service(all_invoices)
    demonstrate_class_static_methods()
    
    print_section("DEMO TAMAMLANDI")
    print("✅ Tüm testler başarılı")
    print(f"📋 İşlenen fatura: {len(all_invoices)}")
    total = sum(inv.paid_amount for inv in all_invoices)
    print(f"💰 Toplam gelir: {CashPayment.format_amount(total, Currency.TRY)}\n")


if __name__ == "__main__":
    main()
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from base import BillingBase, PaymentStatus, InvoiceType
import json


class InMemoryBillingRepository:
    """Hafızada fatura verilerini yöneten repository sınıfı"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__invoices: Dict[str, BillingBase] = {}
        self.__patient_index: Dict[str, List[str]] = {}
        self.__status_index: Dict[PaymentStatus, List[str]] = {s: [] for s in PaymentStatus}
        self.__initialized = True
    
    def save(self, invoice: BillingBase) -> bool:
        """Fatura kaydını kaydeden metod"""
        try:
            inv_id = invoice.invoice_id
            self.__invoices[inv_id] = invoice
            
            patient_id = invoice.patient_id
            if patient_id not in self.__patient_index:
                self.__patient_index[patient_id] = []
            if inv_id not in self.__patient_index[patient_id]:
                self.__patient_index[patient_id].append(inv_id)
            
            status = invoice.status
            if inv_id not in self.__status_index[status]:
                self.__status_index[status].append(inv_id)
            return True
        except:
            return False
    
    def find_by_id(self, invoice_id: str) -> Optional[BillingBase]:
        """ID'ye göre fatura bulan metod"""
        return self.__invoices.get(invoice_id)
    
    def find_by_patient_id(self, patient_id: str) -> List[BillingBase]:
        """Hasta ID'sine göre fatura bulan metod"""
        invoice_ids = self.__patient_index.get(patient_id, [])
        return [self.__invoices[iid] for iid in invoice_ids if iid in self.__invoices]
    
    def find_by_status(self, status: PaymentStatus) -> List[BillingBase]:
        """Duruma göre fatura bulan metod"""
        invoice_ids = self.__status_index.get(status, [])
        return [self.__invoices[iid] for iid in invoice_ids if iid in self.__invoices]
    
    def find_all(self) -> List[BillingBase]:
        """Tüm faturaları döndüren metod"""
        return list(self.__invoices.values())
    
    def delete(self, invoice_id: str) -> bool:
        """Fatura kaydını silen metod"""
        if invoice_id in self.__invoices:
            invoice = self.__invoices[invoice_id]
            patient_id = invoice.patient_id
            if patient_id in self.__patient_index:
                if invoice_id in self.__patient_index[patient_id]:
                    self.__patient_index[patient_id].remove(invoice_id)
            
            status = invoice.status
            if invoice_id in self.__status_index[status]:
                self.__status_index[status].remove(invoice_id)
            
            del self.__invoices[invoice_id]
            return True
        return False
    
    def count(self) -> int:
        """Toplam fatura sayısını döndüren metod"""
        return len(self.__invoices)
    
    def get_total_revenue(self) -> Decimal:
        """Toplam geliri hesaplayan metod"""
        return sum(inv.paid_amount for inv in self.__invoices.values())
    
    def get_total_pending(self) -> Decimal:
        """Toplam bekleyen ödemeyi hesaplayan metod"""
        return sum(inv.remaining_amount for inv in self.__invoices.values())
    
    def find_overdue_invoices(self) -> List[BillingBase]:
        """Vadesi geçmiş faturaları bulan metod"""
        return [inv for inv in self.__invoices.values() if inv.is_overdue()]
    
    def get_patient_total_debt(self, patient_id: str) -> Decimal:
        """Hasta toplam borcunu hesaplayan metod"""
        patient_invoices = self.find_by_patient_id(patient_id)
        return sum(inv.remaining_amount for inv in patient_invoices)
    
    def clear(self) -> None:
        """Tüm kayıtları temizleyen metod"""
        self.__invoices.clear()
        self.__patient_index.clear()
        for status in PaymentStatus:
            self.__status_index[status].clear()
    
    @classmethod
    def get_instance(cls) -> 'InMemoryBillingRepository':
        """Singleton instance döndüren class metod"""
        return cls()
    
    @staticmethod
    def validate_invoice_id(invoice_id: str) -> bool:
        """Fatura ID doğrulama yapan static metod"""
        return invoice_id.startswith("INV") and len(invoice_id) >= 13


class FileBasedBillingRepository:
    """Dosya tabanlı fatura verilerini yöneten repository sınıfı"""
    
    def __init__(self, file_path: str = "invoices.json"):
        self.__file_path = file_path
        self.__invoices: Dict[str, Dict[str, Any]] = {}
        self.__load_from_file()
    
    def __load_from_file(self) -> None:
        """Dosyadan veri yükleyen private metod"""
        try:
            with open(self.__file_path, 'r', encoding='utf-8') as f:
                self.__invoices = json.load(f)
        except:
            self.__invoices = {}
    
    def __save_to_file(self) -> None:
        """Dosyaya veri kaydeden private metod"""
        try:
            with open(self.__file_path, 'w', encoding='utf-8') as f:
                json.dump(self.__invoices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Hata: {e}")
    
    def save(self, invoice: BillingBase) -> bool:
        """Fatura kaydeden metod"""
        try:
            invoice_dict = {
                "invoice_id": invoice.invoice_id,
                "patient_id": invoice.patient_id,
                "patient_name": invoice.patient_name,
                "total_amount": str(invoice.total_amount),
                "status": invoice.status.value,
                "created_at": invoice.created_at.isoformat()
            }
            self.__invoices[invoice.invoice_id] = invoice_dict
            self.__save_to_file()
            return True
        except:
            return False
    
    def find_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """ID'ye göre fatura bulan metod"""
        return self.__invoices.get(invoice_id)
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Tüm faturaları döndüren metod"""
        return list(self.__invoices.values())
    
    def delete(self, invoice_id: str) -> bool:
        """Fatura silen metod"""
        if invoice_id in self.__invoices:
            del self.__invoices[invoice_id]
            self.__save_to_file()
            return True
        return False
    
    def count(self) -> int:
        """Toplam fatura sayısını döndüren metod"""
        return len(self.__invoices)
    
    @classmethod
    def create_with_path(cls, file_path: str) -> 'FileBasedBillingRepository':
        """Özel yol ile oluşturma class metodu"""
        return cls(file_path)
    
    @staticmethod
    def validate_path(file_path: str) -> bool:
        """Dosya yolu doğrulama static metodu"""
        return file_path.endswith('.json')
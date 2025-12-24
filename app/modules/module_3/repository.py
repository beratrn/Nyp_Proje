import os
import sys
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar, Optional

# Tip belirleme
T = TypeVar('T', bound= "LabTest" )

class LabTest:
    pass
# SOYUT KATMAN 

class BaseRepository(ABC):
    @abstractmethod
    def save_test(self, entity: T) -> None: # İsmi demo.py ile uyumlu hale getirdik
        pass

    @abstractmethod
    def get_all_tests(self) -> List[T]: # İsmi demo.py ile uyumlu hale getirdik
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls):
        pass

#  UYGULAMA KATMANI 

class LaboratoryRepository(BaseRepository):
    """
    Verilerin bellek içinde yönetildiği katman.
    """
    def __init__(self):
        # Verilerin listede tutulduğu alan
        self._testler: List[T] = []

    @classmethod
    def create_instance(cls) -> 'LaboratoryRepository':
        return cls()

    def save_test(self, test: T) -> None:
        """Test kaydetme işlemini gerçekleştirir."""
        self._testler.append(test)

    def filter_by_type(self, test_sinifi: Type[T]) -> List[T]:
        """Test türüne göre filtreleme yapar."""
        return [t for t in self._testler if isinstance(t, test_sinifi)]

    def find_by_patient_tc(self, tc: str) -> List[T]:
        """Hasta TC numarası ile arama yapar."""
        return [t for t in self._testler if getattr(t, '_Hasta_TC', None) == tc]

    def get_all_tests(self) -> List[T]:
        """Tüm kayıtlı testleri döner."""
        return self._testler

# MODÜL DIŞA AKTARMA 
# __init__.py içeriğini entegre etme
__all__ = [
    'BaseRepository',
    'LaboratoryRepository'
]
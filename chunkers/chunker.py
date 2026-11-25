from abc import ABC, abstractmethod
from typing import List, Final

"""Interface of chunker type classes"""
class Chunker(ABC):
    OVERLAP_WORDS: Final[str] = 50

    @abstractmethod
    def chunk(self, text: List[str]):
        pass
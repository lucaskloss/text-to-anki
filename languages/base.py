from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class TokenData:
    surface: str
    lemma: str
    pos: str
    sentence: str
    morph: Optional[str] = None


class LanguageProcessor(ABC):
    """
    Abstract base class for language-specific NLP processors.
    """

    @abstractmethod
    def process(self, text: str) -> Iterable[TokenData]:
        """
        Convert raw text into a stream of normalized tokens.

        Each TokenData must at least contain:
        - surface form
        - lemma (normalized)
        - coarse POS tag
        - full sentence context
        """
        raise NotImplementedError

from dataclasses import dataclass


@dataclass
class QuoteGenerationResult:
    content: str
    provider: str

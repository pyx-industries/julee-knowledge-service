from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class SectionHeader:
    """Represents a section header in a document"""
    id: str
    heading: str

@dataclass
class ResourceChunk:
    """Represents a chunk of text from a resource with metadata"""
    id: str
    resource_id: str
    text: str
    sequence: int
    extract: str
    metadata: Dict[str, Any] = None
    path: Optional[List[SectionHeader]] = None
    preamble: Optional[str] = None
    postamble: Optional[str] = None
    score: Optional[float] = None

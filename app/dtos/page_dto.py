from typing import List, Dict, Any, TypeVar, Generic
from math import ceil
from pydantic import BaseModel

T = TypeVar('T')

class PageResponse(Generic[T]):
    def __init__(self, items: List[T], page: int, size: int, total: int):
        self.items = items
        self.page = page
        self.size = size
        self.total = total
        self.total_pages = ceil(total / size)
        self.has_next = page < self.total_pages
        self.has_previous = page > 1

    def dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "page": self.page,
            "size": self.size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous
        }

from pydantic import BaseModel, RootModel
from typing import Any, Dict, Union, List, Optional

class RangeFilter(BaseModel):
    min: Optional[Union[float, str]] = None
    max: Optional[Union[float, str]] = None
    
    def to_dict(self) -> dict[str, Any]:
        return {"min": self.min, "max": self.max}

FilterValue = Union[
    RangeFilter,     # range
    List[Any],       # tag
]

class FilterParams(RootModel[Dict[str, FilterValue]]):
    def to_dict(self) -> dict[str, Any]:
        result = {}
        for key, value in self.root.items():
            if isinstance(value, RangeFilter):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

class FilterMeta(BaseModel):
    column: str
    column_name: str
    filter_type: str # "range" | "tag"
    kind: Optional[str] = None # "number" | "date" (only for range)
    min: Optional[Any] = None
    max: Optional[Any] = None
    values: Optional[List[Any]] = None

class FiltersResponse(BaseModel):
    filters: List[FilterMeta]

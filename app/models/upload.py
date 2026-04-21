from enum import Enum

class DataStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    ENRICHED = "enriched"
    ERROR = "error"

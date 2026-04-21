from pydantic_settings import BaseSettings, SettingsConfigDict

from .validators import parse_list_str, parse_max_size

from typing import Annotated
from pydantic import BeforeValidator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    BASE_URL: str = "http://localhost:8000"

    MAX_UPLOAD_SIZE: Annotated[int, BeforeValidator(parse_max_size)] = 1024 * 1024 * 10 # 10mb
    ALLOWED_EXTENSIONS: Annotated[list[str], BeforeValidator(parse_list_str)] = [
        ".csv",
        ".xlsx",
        ".xls"
    ]



settings = Settings()
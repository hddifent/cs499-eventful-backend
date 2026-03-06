from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PRODUCTION: bool

    DB_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int
    
    STORAGE_ROOT: str

    SESSION_TIMEOUT: int
    ABSOLUTE_TIMEOUT: int

    SESSION_RENEWAL_THRESHOLD: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # type: ignore

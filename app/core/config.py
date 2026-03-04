from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int
    STORAGE_ROOT: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # type: ignore
# print(settings.model_dump())
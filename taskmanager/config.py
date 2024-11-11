from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRE_ACCESS_TOKEN_EXPIRE_MINUTES: int
    EXPIRE_REFRESH_TOKEN_EXPIRE_DAYS: int
    REDIS_URL: str

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()

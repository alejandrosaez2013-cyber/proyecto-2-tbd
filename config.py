from pydantic_settings import BaseSettings

# Es el mismo archivo suministrado en clase, solo modifique el tiempo a una hora.

class Settings(BaseSettings):
    SECRET_KEY: str = "tu-secret-key-muy-secreta-cambiala-en-prod"
    ALGORTHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTOS: int = 60
    
    class Config:
        env_file  = ".env"
        
settings = Settings()
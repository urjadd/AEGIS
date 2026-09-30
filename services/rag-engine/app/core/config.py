
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = 'rag-engine'
    OPENAI_API_KEY: str

    model_config = {'env_file': 
'.env'}

settings = Settings()

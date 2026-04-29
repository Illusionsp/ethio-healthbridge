from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model_id: str = "gemini-1.5-flash"
    chromadb_path: str
    audio_model_name: str = "small"
    device: str = "cpu"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
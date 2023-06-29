from pydantic import BaseSettings


class Settings(BaseSettings):
    token: str
    api_id: str
    api_hash: str

    db: str = 'postgresql://unpin-bot:example@localhost:5430/unpin'

    loop: int = 1 * 60
    sleep: int = 1
    in_memory: bool = True

    class Config:
        env_file = '.env', '../.env'
        env_nested_delimiter = '__'


settings = Settings()

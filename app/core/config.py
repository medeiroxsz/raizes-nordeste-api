"""
Configuração central da aplicação.

[DECISÃO DE IMPLEMENTAÇÃO] O PDF não especifica um SGBD nem parâmetros de
configuração explícitos. Aqui usamos pydantic-settings para carregar tudo de
variáveis de ambiente (.env), o que atende RNF01 (segurança: nada de segredo
hardcoded no código).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Raizes do Nordeste API"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./raizes_nordeste.db"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

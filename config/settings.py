"""
Configurações centralizadas do sistema UniPortal
Este arquivo centraliza todas as configurações do projeto,
eliminando a necessidade de múltiplos arquivos .env
"""
import os
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class Environment(str, Enum):
    """Ambientes disponíveis"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseConfig:
    """Configurações do banco de dados"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        
    @property
    def host(self) -> str:
        """Host do banco de dados por ambiente"""
        hosts = {
            "development": "154.12.231.86",  # SEMPRE servidor externo
            "production": "154.12.231.86",   # SEMPRE servidor externo 
            "testing": "154.12.231.86"       # SEMPRE servidor externo (BD test)
        }
        return os.getenv("DB_HOST", hosts.get(self.environment, "154.12.231.86"))
    
    @property
    def port(self) -> str:
        return os.getenv("DB_PORT", "5432")
    
    @property
    def user(self) -> str:
        return os.getenv("DB_USER", "dadosrh")
    
    @property
    def password(self) -> str:
        return os.getenv("DB_PASSWORD", "dadosrh")
    
    @property
    def name(self) -> str:
        return os.getenv("DB_NAME", "dadosrh")
    
    @property
    def url(self) -> str:
        """URL completa de conexão"""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def connect_args(self) -> Dict:
        """Argumentos de conexão"""
        return {"options": "-csearch_path=rh_homologacao,rh,public"}


class APIConfig:
    """Configurações da API"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
    
    @property
    def backend_port(self) -> int:
        return int(os.getenv("BACKEND_PORT", "8000"))
    
    @property
    def frontend_port(self) -> int:
        return int(os.getenv("FRONTEND_PORT", "8080"))
    
    @property
    def backend_url(self) -> str:
        """URL do backend por ambiente"""
        urls = {
            "development": f"http://192.168.1.37:{self.backend_port}",  # Servidor externo
            "production": f"http://192.168.1.37:{self.backend_port}",   # Servidor externo
            "testing": f"http://192.168.1.37:{self.backend_port}"       # Servidor externo
        }
        return os.getenv("API_URL", urls.get(self.environment))
    
    @property
    def frontend_url(self) -> str:
        """URL do frontend por ambiente"""  
        urls = {
            "development": f"http://192.168.1.37:{self.frontend_port}",  # Servidor externo
            "production": f"http://192.168.1.37:{self.frontend_port}",   # Servidor externo
            "testing": f"http://192.168.1.37:{self.frontend_port}"       # Servidor externo
        }
        return os.getenv("VUE_APP_API_URL", urls.get(self.environment))


class SecurityConfig:
    """Configurações de segurança"""
    
    @property
    def secret_key(self) -> str:
        return os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
    
    @property
    def algorithm(self) -> str:
        return os.getenv("ALGORITHM", "HS256")
    
    @property
    def access_token_expire_minutes(self) -> int:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class BusinessConfig:
    """Configurações de regras de negócio"""
    
    # Cargos que recebem comissão sobre TODA A FILIAL
    CARGOS_FILIAL_COMPLETA: List[str] = [
        "GERENTE",
        "COORDENADOR", 
        "MONITOR",
        "MONITORA",
    ]
    
    # Cargos que recebem comissão sobre HIERARQUIA (equipe)
    CARGOS_HIERARQUIA: List[str] = [
        "SUPERVISOR",
    ]
    
    # Cargos que recebem comissão apenas sobre vendas PRÓPRIAS
    CARGOS_VENDAS_PROPRIAS: List[str] = [
        "ATENDENTE",
        "ESTAGIÁRIO", 
        "ESTAGIARIA",
    ]


class DockerConfig:
    """Configurações do Docker"""
    
    @property
    def project_name(self) -> str:
        return os.getenv("COMPOSE_PROJECT_NAME", "uniportal-main-fresh")
    
    @property
    def network_name(self) -> str:
        return f"{self.project_name}_default"


class Settings:
    """Configurações centralizadas do sistema"""
    
    def __init__(self, environment: Optional[str] = None):
        # Detectar ambiente automaticamente
        self.environment = environment or os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
        
        # Inicializar configurações por módulo
        self.database = DatabaseConfig(self.environment)
        self.api = APIConfig(self.environment)
        self.security = SecurityConfig()
        self.business = BusinessConfig() 
        self.docker = DockerConfig()
        
    def __repr__(self):
        return f"Settings(environment='{self.environment}')"
    
    def get_environment_info(self) -> Dict:
        """Retorna informações do ambiente atual"""
        return {
            "environment": self.environment,
            "database_host": self.database.host,
            "api_backend_url": self.api.backend_url,
            "api_frontend_url": self.api.frontend_url,
        }


# Instância global das configurações
settings = Settings()


# Função helper para desenvolvimento
def print_config():
    """Imprime configurações atuais (útil para debug)"""
    print("=== Configurações UniPortal ===")
    print(f"Ambiente: {settings.environment}")
    print(f"Database Host: {settings.database.host}")
    print(f"Database URL: {settings.database.url}")
    print(f"Backend URL: {settings.api.backend_url}")
    print(f"Frontend URL: {settings.api.frontend_url}")
    print("================================")


if __name__ == "__main__":
    print_config()
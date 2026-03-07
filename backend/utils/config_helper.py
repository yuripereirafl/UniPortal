"""
Utilitário para importação simplificada das configurações centralizadas
Use este arquivo em qualquer script Python do projeto
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Determinar o diretório raiz do projeto
def get_project_root():
    """Encontra a raiz do projeto automaticamente"""
    current_path = Path(__file__).resolve()
    
    # Procurar pela pasta config ou docker-compose.yml para identificar a raiz
    for parent in current_path.parents:
        if (parent / 'config').is_dir() or (parent / 'docker-compose.yml').is_file():
            return parent
    
    # Fallback: assumir que estamos em backend/utils e voltar 2 níveis
    return current_path.parent.parent

# Configurar path do projeto
PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

# Carregar variáveis de ambiente do .env na raiz
env_file = PROJECT_ROOT / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    # Tentar carregar do diretório atual se não encontrar na raiz
    load_dotenv()

# Importar configurações centralizadas
try:
    from config.settings import settings
    CONFIG_LOADED = True
    print("✅ Configurações centralizadas carregadas com sucesso")
except ImportError as e:
    print(f"⚠️  Erro ao carregar configurações centralizadas: {e}")
    print("💡 Usando configurações padrão...")
    
    class FallbackSettings:
        """Configurações de fallback se a importação falhar"""
        class database:
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432") 
            user = os.getenv("DB_USER", "dadosrh")
            password = os.getenv("DB_PASSWORD", "dadosrh")
            name = os.getenv("DB_NAME", "dadosrh")
            url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
            
        class security:
            secret_key = os.getenv("SECRET_KEY", "supersecretkey")
            algorithm = os.getenv("ALGORITHM", "HS256")
    
    settings = FallbackSettings()
    CONFIG_LOADED = False

# Função helper para scripts
def get_database_url():
    """Retorna URL do banco de dados"""
    return settings.database.url

def get_environment():
    """Retorna o ambiente atual"""
    return getattr(settings, 'environment', os.getenv('ENVIRONMENT', 'development'))

def print_config_status():
    """Imprime status das configurações"""
    print("=" * 50)
    print("STATUS DAS CONFIGURAÇÕES")
    print("=" * 50)
    print(f"Raiz do projeto: {PROJECT_ROOT}")
    print(f"Arquivo .env: {env_file}")
    print(f"Config carregada: {'✅ Sim' if CONFIG_LOADED else '❌ Não'}")
    print(f"Ambiente: {get_environment()}")
    print(f"DB Host: {settings.database.host}")
    print("=" * 50)

# Executar se chamado diretamente
if __name__ == "__main__":
    print_config_status()
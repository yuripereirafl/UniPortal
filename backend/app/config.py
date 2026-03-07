
"""
ARQUIVO DEPRECIADO - USE config/settings.py
Este arquivo está sendo mantido por compatibilidade temporária.
Todas as configurações foram movidas para config/settings.py
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para importar config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.settings import settings
    print("✅ Usando configurações centralizadas de config/settings.py")
except ImportError:
    print("⚠️  Erro ao importar configurações centralizadas. Usando fallback local.")
    
    class Settings:
        SECRET_KEY = "supersecretkey"
        ALGORITHM = "HS256"
        
        CARGOS_FILIAL_COMPLETA = ["GERENTE", "COORDENADOR", "MONITOR", "MONITORA"]
        CARGOS_HIERARQUIA = ["SUPERVISOR"]  
        CARGOS_VENDAS_PROPRIAS = ["ATENDENTE", "ESTAGIÁRIO", "ESTAGIARIA"]
    
    settings = Settings()

# Retrocompatibilidade - expor as configurações de negócio diretamente
SECRET_KEY = settings.security.secret_key if hasattr(settings, 'security') else settings.SECRET_KEY
ALGORITHM = settings.security.algorithm if hasattr(settings, 'security') else settings.ALGORITHM

# Configurações de negócio
CARGOS_FILIAL_COMPLETA = settings.business.CARGOS_FILIAL_COMPLETA if hasattr(settings, 'business') else settings.CARGOS_FILIAL_COMPLETA
CARGOS_HIERARQUIA = settings.business.CARGOS_HIERARQUIA if hasattr(settings, 'business') else settings.CARGOS_HIERARQUIA  
CARGOS_VENDAS_PROPRIAS = settings.business.CARGOS_VENDAS_PROPRIAS if hasattr(settings, 'business') else settings.CARGOS_VENDAS_PROPRIAS
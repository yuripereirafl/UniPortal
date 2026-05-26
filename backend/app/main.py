from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db

# --- IMPORTAÇÃO DOS MODELS PARA OS ENDPOINTS DO DASHBOARD ---
from app.models.funcionario import Funcionario
from app.models.setor import Setor
from app.models.sistema import Sistema
from app.models.grupo_email import GrupoEmail
# Importar modelos que têm relacionamentos entre si para garantir registro dos mappers
from app.models.grupos import Grupo
from app.models.permissao import Permissao

# =============================================================================
# ROUTERS ATIVOS - FUNCIONALIDADES MANTIDAS
# =============================================================================
# (Removidos: quadro_colaboradores, metas, colaborador_resumo, metas_unidades, etc.)

# Routers principais (mantidos)
from app.routes.funcionario import router as funcionario_router
from app.routes.sistema import router as sistema_router
from app.routes.setores import router as setores_router
from app.routes.grupo_email import router as grupo_email_router
from app.routes.grupo_pasta import router as grupo_pasta_router
from app.routes.grupo_whatsapp import router as grupo_whatsapp_router
from app.routes.funcionario_cargo import router as funcionario_cargo_router
from app.routes.cargo import router as cargo_router
from app.routes.cargo_opcoes import router as cargo_opcoes_router
from app.routes.usuario import router as usuario_router
from app.routes.relatorios import router as relatorios_router
from app.routes.permissoes import router as permissoes_router
from app.routes.celular import router as celular_router
from app.routes.sla import router as sla_router
from app.routes.notebooks import router as notebooks_router
from app.routes.dominios import router as dominios_router

# REMOVIDO: módulos de vendas/metas/performance (realizado, performance, ranking,
# vendas, nps, orcamentos, comissao, unidade_resumo, pagamentos, resumo_colaborador_email)

# --- INICIALIZAÇÃO DA APLICAÇÃO ---
from app.scheduler import start_scheduler

app = FastAPI(
    title="UniPortal API",
    description="API para gestão de colaboradores, sistemas e acessos. Versão simplificada sem módulo de metas.",
    version="2.0.0"
)

@app.on_event("startup")
def on_startup():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    # Permitir origin específica do frontend na VM e manter regex para outros ambientes locais
    allow_origins=[
        "http://154.12.231.86:8080",  # Novo Servidor Linux
        "http://192.168.1.202:8080",  # Frontend na VMware
        "http://192.168.2.71:8080",   # IP local desta máquina
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600, # Cache do Preflight (OPTIONS) por 10 minutos para reduzir latência
)

# Ativa compressão GZip para respostas maiores que 1KB (excelente para listagens grandes)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# REGISTRO DOS ROUTERS ATIVOS
# =============================================================================

# Routers principais (core do sistema)
app.include_router(funcionario_router)
app.include_router(sistema_router)
app.include_router(setores_router)
app.include_router(grupo_email_router)
app.include_router(grupo_pasta_router)
app.include_router(grupo_whatsapp_router)
app.include_router(funcionario_cargo_router)
app.include_router(cargo_router)
app.include_router(cargo_opcoes_router)
app.include_router(usuario_router)
app.include_router(relatorios_router)
app.include_router(permissoes_router)
app.include_router(celular_router)
app.include_router(sla_router, prefix="/sla", tags=["SLA & Chamados"])
app.include_router(notebooks_router, prefix="/notebooks", tags=["Notebooks"])
app.include_router(dominios_router, prefix="/dominios", tags=["Domínios Internet"])

# REMOVIDO: routers de vendas/metas/performance

# --- OS SEUS ENDPOINTS DE DASHBOARD (MANTIDOS INTACTOS) ---
@app.get("/dashboard/totais")
def get_totais(db: Session = Depends(get_db)):
    """Retorna os totais para o dashboard"""
    total_funcionarios = db.query(func.count(Funcionario.id)).scalar() or 0
    total_setores = db.query(func.count(Setor.id)).scalar() or 0
    total_sistemas = db.query(func.count(Sistema.id)).scalar() or 0
    total_emails = db.query(func.count(GrupoEmail.id)).scalar() or 0
    
    return {
        "funcionarios": total_funcionarios,
        "setores": total_setores,
        "sistemas": total_sistemas,
        "emails": total_emails
    }

@app.get("/dashboard/funcionarios-por-setor")
def get_funcionarios_por_setor(db: Session = Depends(get_db)):
    """Retorna TOP 10 funcionários agrupados por setor com dados reais"""
    try:
        result = db.query(
            Setor.nome,
            func.count(Funcionario.id).label('total')
        ).outerjoin(Funcionario.setores)\
        .filter(Setor.nome.isnot(None))\
        .filter(Setor.nome != '')\
        .group_by(Setor.id, Setor.nome)\
        .having(func.count(Funcionario.id) > 0)\
        .order_by(func.count(Funcionario.id).desc())\
        .limit(10).all()
        
        dados_reais = [
            {"nome": nome.strip(), "total": total}
            for nome, total in result
            if nome and nome.strip() and total > 0
        ]
        return dados_reais
    except Exception as e:
        print(f"Erro ao buscar funcionários por setor: {e}")
        return [{"nome": "Erro ao carregar", "total": 0}]

@app.get("/dashboard/funcionarios-por-sistema")
def get_funcionarios_por_sistema(db: Session = Depends(get_db)):
    """Retorna TOP 10 funcionários agrupados por sistema com dados reais"""
    try:
        result = db.query(
            Sistema.nome,
            func.count(Funcionario.id).label('total')
        ).outerjoin(Funcionario.sistemas)\
        .filter(Sistema.nome.isnot(None))\
        .filter(Sistema.nome != '')\
        .group_by(Sistema.id, Sistema.nome)\
        .having(func.count(Funcionario.id) > 0)\
        .order_by(func.count(Funcionario.id).desc())\
        .limit(10).all()
        
        dados_reais = [
            {"nome": nome.strip(), "total": total}
            for nome, total in result
            if nome and nome.strip() and total > 0
        ]
        return dados_reais
    except Exception as e:
        print(f"Erro ao buscar funcionários por sistema: {e}")
        return [{"nome": "Erro ao carregar", "total": 0}]

@app.get('/')
def read_root():
    return {"message": "API do Sistema TI funcionando!"}
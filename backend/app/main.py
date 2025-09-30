from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db

# --- IMPORTAÇÃO DOS MODELS PARA OS ENDPOINTS DO DASHBOARD ---
from app.models.funcionario import Funcionario
from app.models.setor import Setor
from app.models.sistema import Sistema
from app.models.grupo_email import GrupoEmail

# --- IMPORTAÇÃO DE TODOS OS ROUTERS ---
# (Mantendo os seus routers existentes)
from app.routes.funcionario import router as funcionario_router
from app.routes.sistema import router as sistema_router
from app.routes.setores import router as setores_router
from app.routes.grupo_email import router as grupo_email_router
from app.routes.grupo_pasta import router as grupo_pasta_router
from app.routes.grupo_whatsapp import router as grupo_whatsapp_router
from app.routes.funcionario_cargo import router as funcionario_cargo_router
from app.routes.cargo import router as cargo_router
from app.routes.cargo_opcoes import router as cargo_opcoes_router
from app.routes.quadro_colaboradores import router as quadro_colaboradores_router
from app.routes.usuario import router as usuario_router
from app.routes.relatorios import router as relatorios_router

# --- NOVAS ROTAS (IMPORTADAS CORRETAMENTE) ---
from app.routes.metas import router as metas_router
from app.routes.realizado import router as realizado_router
from app.routes.performance import router as performance_router # NOVO 

# --- INICIALIZAÇÃO DA APLICAÇÃO ---
app = FastAPI(
    title="UniPortal API",
    description="API para gestão de colaboradores, acessos e metas.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSÃO DE TODOS OS ROUTERS NA APLICAÇÃO ---
# (Mantendo os seus routers existentes)
app.include_router(funcionario_router)
app.include_router(sistema_router)
app.include_router(setores_router)
app.include_router(grupo_email_router)
app.include_router(grupo_pasta_router)
app.include_router(grupo_whatsapp_router)
app.include_router(funcionario_cargo_router)
app.include_router(cargo_router)
app.include_router(cargo_opcoes_router)
app.include_router(quadro_colaboradores_router)
app.include_router(usuario_router)
app.include_router(relatorios_router)

# --- REGISTO DAS NOVAS ROTAS ---
app.include_router(metas_router)
app.include_router(realizado_router)
app.include_router(performance_router) # NOVO


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
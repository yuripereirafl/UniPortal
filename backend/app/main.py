from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

# Dashboard endpoints
from sqlalchemy import func
from app.models.funcionario import Funcionario
from app.models.setor import Setor  
from app.models.sistema import Sistema
from app.models.grupo_email import GrupoEmail

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
        # Busca setores com a contagem real de funcionários (filtra NULL/vazios)
        result = db.query(
            Setor.nome,
            func.count(Funcionario.id).label('total')
        ).outerjoin(
            Funcionario.setores
        ).filter(Setor.nome.isnot(None))\
        .filter(Setor.nome != '')\
        .group_by(Setor.id, Setor.nome)\
        .having(func.count(Funcionario.id) > 0)\
        .order_by(func.count(Funcionario.id).desc())\
        .limit(10).all()
        
        # Converte para formato JSON (só nomes válidos)
        dados_reais = []
        for nome, total in result:
            # Filtro adicional para garantir nomes válidos
            if nome and nome.strip() and total > 0:
                dados_reais.append({
                    "nome": nome.strip(),
                    "total": total
                })
        
        return dados_reais
    except Exception as e:
        print(f"Erro ao buscar funcionários por setor: {e}")
        # Fallback para dados de exemplo
        return [
            {"nome": "Erro ao carregar", "total": 0}
        ]

@app.get("/dashboard/funcionarios-por-sistema")
def get_funcionarios_por_sistema(db: Session = Depends(get_db)):
    """Retorna TOP 10 funcionários agrupados por sistema com dados reais"""
    try:
        # Busca sistemas com a contagem real de funcionários (filtra NULL/vazios)
        result = db.query(
            Sistema.nome,
            func.count(Funcionario.id).label('total')
        ).outerjoin(
            Funcionario.sistemas
        ).filter(Sistema.nome.isnot(None))\
        .filter(Sistema.nome != '')\
        .group_by(Sistema.id, Sistema.nome)\
        .having(func.count(Funcionario.id) > 0)\
        .order_by(func.count(Funcionario.id).desc())\
        .limit(10).all()
        
        # Converte para formato JSON (só nomes válidos)
        dados_reais = []
        for nome, total in result:
            # Filtro adicional para garantir nomes válidos
            if nome and nome.strip() and total > 0:
                dados_reais.append({
                    "nome": nome.strip(),
                    "total": total
                })
        
        return dados_reais
    except Exception as e:
        print(f"Erro ao buscar funcionários por sistema: {e}")
        # Fallback para dados de exemplo
        return [
            {"nome": "Erro ao carregar", "total": 0}
        ]

@app.get('/')
def read_root():
    return {"message": "API do Sistema TI funcionando!"}

from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import distinct
from app.database import engine
from app.models.cargo import Cargo

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/cargos/nomes')
def get_cargo_nomes():
    """Retorna lista distinta de nomes de cargos"""
    db = SessionLocal()
    try:
        nomes = db.query(distinct(Cargo.nome)).filter(Cargo.nome.isnot(None)).all()
        resultado = [nome[0] for nome in nomes if nome[0]]
        return sorted(resultado)
    finally:
        db.close()

@router.get('/cargos/funcoes')
def get_cargo_funcoes():
    """Retorna lista distinta de funções de cargos"""
    db = SessionLocal()
    try:
        funcoes = db.query(distinct(Cargo.funcao)).filter(Cargo.funcao.isnot(None)).all()
        resultado = [funcao[0] for funcao in funcoes if funcao[0]]
        return sorted(resultado)
    finally:
        db.close()

@router.get('/cargos/equipes')
def get_cargo_equipes():
    """Retorna lista distinta de equipes de cargos"""
    db = SessionLocal()
    try:
        equipes = db.query(distinct(Cargo.equipe)).filter(Cargo.equipe.isnot(None)).all()
        resultado = [equipe[0] for equipe in equipes if equipe[0]]
        return sorted(resultado)
    finally:
        db.close()

@router.get('/cargos/niveis')
def get_cargo_niveis():
    """Retorna lista distinta de níveis de cargos"""
    db = SessionLocal()
    try:
        niveis = db.query(distinct(Cargo.nivel)).filter(Cargo.nivel.isnot(None)).all()
        resultado = [nivel[0] for nivel in niveis if nivel[0]]
        return sorted(resultado)
    finally:
        db.close()

@router.get('/cargos/buscar')
def buscar_cargo_por_atributos(nome: str = None, funcao: str = None, equipe: str = None, nivel: str = None):
    """Busca cargo pelos atributos específicos"""
    db = SessionLocal()
    try:
        query = db.query(Cargo)
        
        if nome:
            query = query.filter(Cargo.nome == nome)
        if funcao:
            query = query.filter(Cargo.funcao == funcao)
        if equipe:
            query = query.filter(Cargo.equipe == equipe)
        if nivel:
            query = query.filter(Cargo.nivel == nivel)
            
        cargo = query.first()
        if cargo:
            return {
                'id': cargo.id,
                'nome': cargo.nome,
                'funcao': cargo.funcao,
                'equipe': cargo.equipe,
                'nivel': cargo.nivel
            }
        return None
    finally:
        db.close()

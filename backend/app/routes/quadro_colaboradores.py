from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import engine
from app.models.funcionario import Funcionario as FuncionarioModel
from app.models.setor import Setor
from app.models.cargo import Cargo
from app.models.funcionario_cargo import FuncionarioCargo
from app.models.funcionario_filial import FuncionarioFilial
from app.models.filial import Filial
from app.models.funcionario_meta import FuncionarioMeta
from app.models.meta import Meta

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/quadro_colaboradores/')
def quadro_colaboradores():
    db = SessionLocal()
    funcionarios = db.query(FuncionarioModel).options(
        joinedload(FuncionarioModel.setores)
    ).all()
    resultado = []
    for funcionario in funcionarios:
        setores = [s.nome for s in funcionario.setores]
        # Cargo atual
        cargo_vinculo = db.query(FuncionarioCargo).filter_by(funcionario_id=funcionario.id, dt_fim=None).order_by(FuncionarioCargo.dt_inicio.desc()).first()
        cargo = None
        if cargo_vinculo:
            cargo = db.query(Cargo).filter_by(id=cargo_vinculo.cargo_id).first()
        # Filial atual
        filial_vinculo = db.query(FuncionarioFilial).filter_by(funcionario_id=funcionario.id, dt_fim=None).order_by(FuncionarioFilial.dt_inicio.desc()).first()
        filial = None
        if filial_vinculo:
            filial = db.query(Filial).filter_by(id=filial_vinculo.filial_id).first()
        # Meta atual
        meta_vinculo = db.query(FuncionarioMeta).filter_by(funcionario_id=funcionario.id, dt_fim=None).order_by(FuncionarioMeta.dt_inicio.desc()).first()
        meta = None
        if meta_vinculo:
            meta = db.query(Meta).filter_by(id=meta_vinculo.meta_id).first()
        resultado.append({
            'id': funcionario.id,
            'nome': funcionario.nome,
            'sobrenome': funcionario.sobrenome,
            'setores': setores,
            'cargo': {
                'id': cargo.id if cargo else None,
                'nome': cargo.nome if cargo else None,
                'nivel': cargo.nivel if cargo else None,
                'funcao': cargo.funcao if cargo else None,
                'equipe': cargo.equipe if cargo else None
            } if cargo else None,
            'filial': {
                'id': filial.id if filial else None,
                'nome': filial.nome if filial else None
            } if filial else None,
            'meta': {
                'id': meta.id if meta else None,
                'calc_meta': meta.calc_meta if meta else None,
                'tipo_pgto': meta.tipo_pgto if meta else None
            } if meta else None
        })
    db.close()
    return resultado

from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker, joinedload
from datetime import date
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
        joinedload(FuncionarioModel.setores),
        joinedload(FuncionarioModel.sistemas),
        joinedload(FuncionarioModel.grupos_email),
        joinedload(FuncionarioModel.grupos_pasta)
    ).all()
    resultado = []
    for funcionario in funcionarios:
        setores = [{'id': s.id, 'nome': s.nome} for s in funcionario.setores]
        sistemas = [{'id': s.id, 'nome': s.nome} for s in funcionario.sistemas]
        grupos_email = [{'id': g.id, 'nome': g.nome} for g in funcionario.grupos_email]
        grupos_pasta = [{'id': g.id, 'nome': g.nome} for g in funcionario.grupos_pasta]
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
        
        # Calcular status baseado nas datas de afastamento
        hoje = date.today()
        status = "Ativo"
        
        if funcionario.data_afastamento:
            # Se tem data de afastamento
            if funcionario.data_retorno:
                # Se tem data de retorno
                if funcionario.data_afastamento <= hoje <= funcionario.data_retorno:
                    status = "Afastado"
                elif hoje > funcionario.data_retorno:
                    status = "Ativo"  # Já retornou
                else:
                    status = "Ativo"  # Ainda não se afastou
            else:
                # Sem data de retorno - se já passou da data de afastamento, está afastado
                if funcionario.data_afastamento <= hoje:
                    status = "Afastado"
        
        resultado.append({
            'id': funcionario.id,
            'nome': funcionario.nome,
            'sobrenome': funcionario.sobrenome,
            'email': funcionario.email,
            'cpf': funcionario.cpf,
            'celular': funcionario.celular,
            'data_admissao': funcionario.data_admissao,
            'data_inativado': funcionario.data_inativado,
            'tipo_contrato': funcionario.tipo_contrato,
            'data_afastamento': funcionario.data_afastamento.strftime('%Y-%m-%d') if funcionario.data_afastamento else None,
            'data_retorno': funcionario.data_retorno.strftime('%Y-%m-%d') if funcionario.data_retorno else None,
            'motivo_afastamento': funcionario.motivo_afastamento,
            'status': status,
            'setores': setores,
            'sistemas': sistemas,
            'grupos_email': grupos_email,
            'grupos_pasta': grupos_pasta,
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

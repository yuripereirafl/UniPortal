from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.funcionario import Funcionario
from app.models.setor import Setor
from app.models.sistema import Sistema
from app.models.grupo_email import GrupoEmail
from app.models.grupo_pasta import GrupoPasta
import io
import pandas as pd

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.get("/funcionarios/xlsx")
def exportar_funcionarios_xlsx(db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).all()
    dados = []
    for f in funcionarios:
        setores = ', '.join([s.nome for s in getattr(f, 'setores', [])])
        sistemas = ', '.join([f"{s.nome} ({s.status})" for s in getattr(f, 'sistemas', [])])
        grupos_email = ', '.join([g.nome for g in getattr(f, 'grupos_email', [])])
        grupos_pasta = ', '.join([g.nome for g in getattr(f, 'grupos_pasta', [])])
        dados.append({
            'Nome': f.nome,
            'Sobrenome': f.sobrenome,
            'Cargo': f.cargo,
            'Celular': f.celular,
            'E-mail': f.email,
            'Data de Admissão': f.data_inclusao,
            'Data de Desligamento': f.data_inativado,
            'Setores': setores,
            'Sistemas': sistemas,
            'Grupo E-mail': grupos_email,
            'Grupo de Pastas': grupos_pasta,
        })
    df = pd.DataFrame(dados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Funcionarios')
    output.seek(0)
    headers = {
        'Content-Disposition': 'attachment; filename=funcionarios.xlsx'
    }
    return Response(content=output.read(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

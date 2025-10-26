"""
Rotas para o módulo de Pagamentos de Meta
Consulta valores calculados de pagamento baseado em performance
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime, date
from typing import Optional

from app.database import get_db
from app.models.pagamentos_meta import PagamentoMeta
from app.schemas.pagamento import PagamentoMetaResponse, PagamentoResumo

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)


@router.get(
    "/{id_eyal}",
    response_model=PagamentoMetaResponse,
    summary="Buscar pagamento de meta por colaborador"
)
async def get_pagamento_colaborador(
    id_eyal: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Retorna os dados de pagamento de meta de um colaborador para um mês específico.

    Args:
        id_eyal: ID do colaborador no sistema Eyal
        mes_ref: Mês de referência no formato YYYY-MM (default: mês atual)

    Returns:
        PagamentoMetaResponse com todos os campos da tabela pagamentos_meta
    """
    try:
        # Determinar mês de referência
        if mes_ref:
            try:
                if len(mes_ref) == 7:  # YYYY-MM
                    mes_referencia = datetime.strptime(mes_ref, "%Y-%m").date()
                elif len(mes_ref) == 10:  # YYYY-MM-DD
                    mes_referencia = datetime.strptime(mes_ref, "%Y-%m-%d").date()
                else:
                    raise ValueError("Formato inválido")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de data inválido. Use YYYY-MM ou YYYY-MM-DD"
                )
        else:
            hoje = date.today()
            mes_referencia = date(hoje.year, hoje.month, 1)

        print(f"\n[PAGAMENTOS] Buscando pagamento para {id_eyal} em {mes_referencia}")

        # Buscar pagamento no banco
        pagamento = db.query(PagamentoMeta).filter(
            PagamentoMeta.id_eyal == id_eyal,
            PagamentoMeta.mes_ref == mes_referencia
        ).first()

        if not pagamento:
            raise HTTPException(
                status_code=404,
                detail=f"Pagamento não encontrado para {id_eyal} no mês {mes_referencia}"
            )

        print(f"✅ Pagamento encontrado: R$ {pagamento.pagamento_final}")

        return pagamento

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao buscar pagamento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar pagamento: {str(e)}"
        )


@router.get(
    "/resumo/{id_eyal}",
    response_model=PagamentoResumo,
    summary="Resumo simplificado de pagamento"
)
async def get_pagamento_resumo(
    id_eyal: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Retorna resumo simplificado do pagamento (usado para integração com outros módulos).

    Returns:
        PagamentoResumo com campos essenciais: pagamento_final, percentual, nps, status
    """
    try:
        # Buscar pagamento completo
        pagamento = await get_pagamento_colaborador(id_eyal, mes_ref, db)

        # Retornar resumo
        return PagamentoResumo(
            pagamento_final=float(pagamento.pagamento_final or 0),
            percentual_projetado=float(pagamento.percentual_projetado_usado or 0),
            nps=float(pagamento.nps or 0),
            status=pagamento.status,
            bonus_ativo=pagamento.bonus_ativo or False
        )

    except HTTPException as e:
        # Se não encontrou pagamento, retornar valores zerados
        if e.status_code == 404:
            return PagamentoResumo(
                pagamento_final=0.0,
                percentual_projetado=0.0,
                nps=0.0,
                status="Não calculado",
                bonus_ativo=False
            )
        raise

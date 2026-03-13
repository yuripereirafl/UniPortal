from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sla import SlaRule, TicketSla
from app.services.glpi_service import GLPIService
from datetime import datetime
from sqlalchemy import func, String

router = APIRouter()

@router.get("/stats")
def get_sla_stats(start_date: str = Query(None), end_date: str = Query(None), db: Session = Depends(get_db)):
    today = datetime.now()
    if not start_date:
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = today.strftime("%Y-%m-%d")

    d_start = datetime.strptime(start_date, "%Y-%m-%d")
    d_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    
    tickets = db.query(TicketSla).filter(
        TicketSla.data_fechamento >= d_start,
        TicketSla.data_fechamento <= d_end
    ).all()
    
    if not tickets:
        return {
            "period": f"{start_date} até {end_date}",
            "total": 0,
            "sla_ok": 0,
            "sla_not_ok": 0,
            "percent_sla": 0,
            "average_hours": 0,
            "total_etapas": 0,
            "by_category": []
        }

    total = len(tickets)
    solved_tickets = [t for t in tickets if t.status_sla in ["SLA OK", "SLA NÃO OK"]]
    total_solved = len(solved_tickets)
    
    sla_ok = len([t for t in solved_tickets if t.status_sla == "SLA OK"])
    sla_not_ok = total_solved - sla_ok
    percent_sla = (sla_ok / total_solved) * 100 if total_solved > 0 else 0
    
    total_minutes = sum([t.tempo_atendimento_minutos for t in solved_tickets])
    avg_hours = (total_minutes / total_solved) / 60 if total_solved > 0 else 0
    
    total_etapas = sum([t.etapas_total for t in tickets])

    categories = {}
    auditoria_data = []
    for t in tickets:
        cat = t.categoria or "OUTROS"
        if cat not in categories:
            categories[cat] = {"total": 0, "ok": 0, "not_ok": 0, "etapas": 0, "solved": 0}
        categories[cat]["total"] += 1
        if t.status_sla == "SLA OK":
            categories[cat]["ok"] += 1
            categories[cat]["solved"] += 1
        elif t.status_sla == "SLA NÃO OK":
            categories[cat]["not_ok"] += 1
            categories[cat]["solved"] += 1
        categories[cat]["etapas"] += t.etapas_total

    by_category = []
    for name, stats in categories.items():
        by_category.append({
            "name": name,
            "total": stats["total"],
            "ok": stats["ok"],
            "not_ok": stats["not_ok"],
            "percent": (stats["ok"] / stats["solved"]) * 100 if stats["solved"] > 0 else 0,
            "etapas": stats["etapas"]
        })
        if stats["etapas"] > 0:
            auditoria_data.append({"name": name, "quant": stats["total"], "etapas": stats["etapas"]})

    last_update = None
    if tickets:
        # Pega a data mais recente de atualização entre os tickets do período
        dates = [t.updated_at for t in tickets if t.updated_at]
        if dates:
            last_update = max(dates).strftime("%d/%m/%Y %H:%M:%S")

    # Preparar dados para os gráficos
    chart_data = {
        "labels": [cat["name"] for cat in by_category[:8]], # Top 8 categorias
        "series": [cat["total"] for cat in by_category[:8]],
        "sla_series": [round(cat["percent"], 1) for cat in by_category[:8]]
    }

    return {
        "period": f"{start_date} a {end_date}",
        "total_atendimentos": total,
        "total_solucionados": total_solved,
        "sla_ok": sla_ok,
        "sla_not_ok": sla_not_ok,
        "percent_sla": round(percent_sla, 2),
        "average_hours": round(avg_hours, 2),
        "total_etapas": total_etapas,
        "last_update": last_update,
        "by_category": sorted(by_category, key=lambda x: x["total"], reverse=True),
        "auditoria": sorted(auditoria_data, key=lambda x: x["etapas"], reverse=True),
        "chart_data": chart_data
    }

@router.get("/tickets")
def list_tickets(start_date: str = Query(None), end_date: str = Query(None), q: str = Query(None), db: Session = Depends(get_db)):
    today = datetime.now()
    if not start_date:
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = today.strftime("%Y-%m-%d")

    d_start = datetime.strptime(start_date, "%Y-%m-%d")
    d_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    
    query = db.query(TicketSla).filter(
        TicketSla.data_fechamento >= d_start,
        TicketSla.data_fechamento <= d_end
    )
    if q:
        query = query.filter(
            (TicketSla.titulo.ilike(f"%{q}%")) | 
            (TicketSla.categoria.ilike(f"%{q}%")) |
            (TicketSla.glpi_id.cast(String).ilike(f"%{q}%"))
        )
    
    return query.order_by(TicketSla.data_fechamento.desc()).all()

@router.post("/sync")
def sync_glpi(start_date: str = Query(None), end_date: str = Query(None), db: Session = Depends(get_db)):
    today = datetime.now()
    if not start_date:
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = today.strftime("%Y-%m-%d")

    service = GLPIService()
    result = service.get_tickets_by_date_range(db, start_date, end_date)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    return db.query(SlaRule).all()

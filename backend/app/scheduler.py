import time
from datetime import datetime, timedelta
import threading
import schedule
from app.database import SessionLocal
from app.models.sla import TicketSla
from app.services.glpi_service import GLPIService

# Como apscheduler pode ser problemático com reload ou dependências, 
# podemos usar o pacote 'schedule' ou 'apscheduler'. Como apscheduler está instalado, vou usá-lo.
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()

def sync_sla_tickets_job():
    """
    Job que roda em background para sincronizar tickets do GLPI.
    """
    print(f"[{datetime.now()}] Iniciando Sincronização Automática de SLA...")
    
    db = SessionLocal()
    try:
        # Para ser dinâmico e pegar apenas últimos dias (ex. últimos 3 dias ou o mês atual)
        # Sincronizamos o mês atual inteiro a cada vez (o GLPI service já otimiza lendo apenas do dia atual até o fim, via id descending)
        # Sincronizamos os últimos 30 dias para garantir que chamados abertos antes e fechados agora sejam capturados
        end_date_dt = today
        start_date_dt = today - timedelta(days=30)
        
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")

        service = GLPIService()
        result = service.get_tickets_by_date_range(db, start_date, end_date)
        
        # --- TRAVA AUTOMÁTICA DE MESES ANTERIORES ---
        # Qualquer chamado fechado antes do dia 1 do mês atual é marcado como auditado
        first_day_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        locked_count = db.query(TicketSla).filter(
            TicketSla.data_fechamento < first_day_of_current_month,
            TicketSla.is_audited == False
        ).update({"is_audited": True}, synchronize_session=False)
        
        if locked_count > 0:
            db.commit()
            print(f"[{datetime.now()}] Trava Automática: {locked_count} chamados de meses anteriores foram fixados.")
        
        print(f"[{datetime.now()}] Sincronização automática concluída: {result}")
    except Exception as e:
        print(f"[{datetime.now()}] Erro durante a sincronização automática: {e}")
    finally:
        db.close()

def start_scheduler():
    """Inicializa o agendador e configura as tarefas."""
    if not scheduler.running:
        scheduler.add_job(
            sync_sla_tickets_job,
            trigger=IntervalTrigger(minutes=5),
            id="sync_glpi_tickets",
            name="Sincroniza Tickets GLPI a cada 5 min",
            replace_existing=True
        )
        scheduler.start()
        print("Scheduler de SLA iniciado com sucesso!")

# Tentar limpar scheduler no final se a aplicação fechar
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

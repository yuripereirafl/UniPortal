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
    today = datetime.now()
    print(f"[SCHEDULER] [{today.strftime('%d/%m/%Y %H:%M:%S')}] Iniciando Sincronizacao Automatica de SLA...")
    
    db = SessionLocal()
    try:
        end_date_dt = today
        start_date_dt = today - timedelta(days=30)
        
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")

        service = GLPIService()
        result = service.get_tickets_by_date_range(db, start_date, end_date)
        
        # --- TRAVA AUTOMÁTICA DE MESES ANTERIORES ---
        first_day_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        locked_count = db.query(TicketSla).filter(
            TicketSla.data_fechamento < first_day_of_current_month,
            TicketSla.is_audited == False
        ).update({"is_audited": True}, synchronize_session=False)
        
        if locked_count > 0:
            db.commit()
            print(f"[SCHEDULER] Trava Automatica: {locked_count} chamados de meses anteriores fixados.")
        
        print(f"[SCHEDULER] [{datetime.now().strftime('%H:%M:%S')}] Sincronizacao concluida: {result}")
    except Exception as e:
        print(f"[SCHEDULER] ERRO na sincronizacao automatica: {e}")
        import traceback
        traceback.print_exc()
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

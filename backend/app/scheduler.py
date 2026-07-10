"""
scheduler.py — Agendador de sincronização de chamados GLPI (TI + INFRA)
=======================================================================
Jobs:
  1. sync_sla_tickets_job — A cada 5 minutos: sincroniza TI e INFRA (últimos 30 dias)
  2. sync_historical_job  — Na inicialização: carga histórica desde maio/2026 (em background)

A lógica de separação TI vs INFRA é feita pelo glpi_service.py ao ler as
categorias de cada chamado (completename da ITILCategory).
"""

import time
import threading
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.models.sla import TicketSla
from app.services.glpi_service import GLPIService

# ── Instância global do scheduler ─────────────────────────────────────────────
scheduler = BackgroundScheduler()

# ── Flag para evitar múltiplas cargas históricas simultâneas ──────────────────
_historical_running = False


# ─────────────────────────────────────────────────────────────────────────────
# JOB 1 — Sincronização regular (a cada 5 min)
# Sincroniza TI + INFRA dos últimos 30 dias (rolling window)
# ─────────────────────────────────────────────────────────────────────────────
def sync_sla_tickets_job():
    """
    Sincroniza chamados de TI e INFRA dos últimos 30 dias.
    Roda automaticamente a cada 5 minutos.
    """
    global _historical_running

    today = datetime.now()
    tag   = today.strftime("%d/%m/%Y %H:%M:%S")

    # Não roda o job regular enquanto a carga histórica está processando
    # para evitar sobrecarga na API do GLPI
    if _historical_running:
        print(f"[SCHEDULER] [{tag}] Carga historica em andamento — job regular aguardando.")
        return

    print(f"[SCHEDULER] [{tag}] Iniciando Sincronizacao Automatica (TI + INFRA, ultimos 30 dias)...")

    db = SessionLocal()
    try:
        end_date_dt   = today
        start_date_dt = today - timedelta(days=30)

        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date   = end_date_dt.strftime("%Y-%m-%d")

        service = GLPIService()
        result  = service.get_tickets_by_date_range(db, start_date, end_date)

        # ── Trava automática de meses anteriores ─────────────────────────────
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        locked_count = db.query(TicketSla).filter(
            TicketSla.data_fechamento < first_day_current_month,
            TicketSla.is_audited == False
        ).update({"is_audited": True}, synchronize_session=False)

        if locked_count > 0:
            db.commit()
            print(f"[SCHEDULER] Trava Automatica: {locked_count} chamados de meses anteriores fixados.")

        print(f"[SCHEDULER] [{datetime.now().strftime('%H:%M:%S')}] Sync concluido: {result}")

    except Exception as e:
        print(f"[SCHEDULER] ERRO na sincronizacao automatica: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# JOB 2 — Carga histórica inicial (roda uma vez na inicialização, em background)
# Importa TI + INFRA desde maio/2026 mês a mês
# ─────────────────────────────────────────────────────────────────────────────
def sync_historical_job():
    """
    Carga histórica: importa TI + INFRA desde maio/2026 até hoje, mês a mês.
    Executada uma única vez na inicialização da aplicação, em thread separada.
    """
    global _historical_running
    _historical_running = True

    today = datetime.now()
    print(f"[SCHEDULER] [{today.strftime('%d/%m/%Y %H:%M:%S')}] "
          f"Iniciando carga historica (TI + INFRA desde maio/2026)...")

    # ── Gerar lista de meses desde maio/2026 ─────────────────────────────────
    months = []
    cursor = datetime(2026, 5, 1)
    while cursor <= today:
        months.append(cursor)
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1, day=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1, day=1)

    print(f"[SCHEDULER] Meses a sincronizar: {len(months)}")

    db = SessionLocal()
    try:
        service = GLPIService()

        for i, month_start in enumerate(months, 1):
            # Último dia do mês
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

            # Não ultrapassa hoje
            if month_end > today:
                month_end = today

            start_str = month_start.strftime("%Y-%m-%d")
            end_str   = month_end.strftime("%Y-%m-%d")

            print(f"[SCHEDULER] [{i:02d}/{len(months):02d}] "
                  f"Carga historica: {month_start.strftime('%B/%Y')} ({start_str} → {end_str})...")

            try:
                result = service.get_tickets_by_date_range(db, start_str, end_str)
                ti_count    = result.get("ti_count",    0) if isinstance(result, dict) else "?"
                infra_count = result.get("infra_count", 0) if isinstance(result, dict) else "?"
                print(f"[SCHEDULER]   ✓ {month_start.strftime('%m/%Y')}: "
                      f"processados={result.get('processed', '?') if isinstance(result, dict) else result}")
            except Exception as e:
                print(f"[SCHEDULER]   ✗ Erro em {month_start.strftime('%m/%Y')}: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"[SCHEDULER] ERRO na carga historica: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        _historical_running = False
        print(f"[SCHEDULER] Carga historica concluida! (TI + INFRA desde maio/2026)")


# ─────────────────────────────────────────────────────────────────────────────
# START / STOP
# ─────────────────────────────────────────────────────────────────────────────
def start_scheduler():
    """Inicializa o scheduler e lança a carga histórica em background."""
    if scheduler.running:
        return

    # ── Job regular: a cada 5 minutos ────────────────────────────────────────
    scheduler.add_job(
        sync_sla_tickets_job,
        trigger=IntervalTrigger(minutes=5),
        id="sync_glpi_tickets",
        name="Sincroniza TI + INFRA a cada 5 min (ultimos 30 dias)",
        replace_existing=True
    )

    scheduler.start()
    print("[SCHEDULER] Iniciado! Job TI+INFRA a cada 5 min.")

    # ── Carga histórica em thread separada ────────────────────────────────────
    hist_thread = threading.Thread(
        target=sync_historical_job,
        name="HistoricalSync-TI-INFRA",
        daemon=True
    )
    hist_thread.start()
    print("[SCHEDULER] Carga historica TI+INFRA iniciada em background!")


def stop_scheduler():
    """Para o scheduler graciosamente."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[SCHEDULER] Parado.")

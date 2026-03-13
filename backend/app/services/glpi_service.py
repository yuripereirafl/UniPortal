import requests
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.sla import SlaRule, TicketSla
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

# Carregar env se necessário (caso não venha pelo main)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class GLPIService:
    def __init__(self):
        self.base_url = os.getenv("GLPI_BASE_URL")
        self.app_token = os.getenv("GLPI_APP_TOKEN")
        self.user_token = os.getenv("GLPI_USER_TOKEN")
        self.session_token = None
        self.headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token
        }

    def _init_session(self):
        if self.session_token:
            return True
        
        headers = self.headers.copy()
        headers["Authorization"] = f"user_token {self.user_token}"
        
        try:
            resp = requests.get(f"{self.base_url}/initSession", headers=headers, timeout=10)
            if resp.status_code == 200:
                self.session_token = resp.json()["session_token"]
                self.headers["Session-Token"] = self.session_token
                return True
        except Exception as e:
            print(f"Erro GLPI initSession: {e}")
        return False

    def _kill_session(self):
        if self.session_token:
            requests.get(f"{self.base_url}/killSession", headers=self.headers)
            self.session_token = None

    def get_tickets_by_date_range(self, db: Session, start_date_str: str, end_date_str: str):
        """
        start_date_str: Formato 'YYYY-MM-DD'
        end_date_str: Formato 'YYYY-MM-DD'
        """
        if not self._init_session():
            return {"error": "Falha na autenticação GLPI"}

        print(f"Buscando tickets de {start_date_str} até {end_date_str}...")
        all_tickets = []
        range_start = 0
        range_step = 100
        
        while True:
            params = {
                "range": f"{range_start}-{range_start + range_step - 1}",
                "sort": "id",
                "order": "DESC"
            }
            
            resp = requests.get(f"{self.base_url}/Ticket", headers=self.headers, params=params)
            if resp.status_code not in [200, 206]:
                break
            
            tickets = resp.json()
            if not tickets:
                break
            
            filtered_count = 0
            for t in tickets:
                t_date = t.get("date", "")
                t_solve = t.get("solvedate", "") or t.get("closedate", "")
                
                t_date_str = str(t_date)[:10] if t_date else ""
                t_solve_str = str(t_solve)[:10] if t_solve else ""
                
                in_range = False
                # Filtro por Data de Solução/Fechamento (Padrão para Auditoria de SLA)
                if t_solve_str and start_date_str <= t_solve_str <= end_date_str:
                    in_range = True
                # Se não tem solução mas foi aberto no período, opcionalmente incluir? 
                # Verificando com 331 vs 336, provavelmente a planilha usa data de solução.
                    
                if in_range:
                    all_tickets.append(t)
                    filtered_count += 1
                
            range_start += range_step
            if range_start > 10000: 
                break
                
            if len(tickets) > 0:
                last_t_date = str(tickets[-1].get("date", ""))[:10]
                if last_t_date:
                    from datetime import datetime, timedelta
                    last_dt = datetime.strptime(last_t_date, "%Y-%m-%d")
                    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                    # Olhar até 90 dias antes do início do período (segurança para chamados antigos resolvidos agora)
                    if last_dt < (start_dt - timedelta(days=90)):
                        break
        
        print(f"Total de tickets capturados para processamento: {len(all_tickets)}")
        
        month_str = start_date_str[:7]
        processed_ids = self.process_and_save_tickets(db, all_tickets, month_str)
        
        # --- LÓGICA DE LIMPEZA (PURGE) ---
        # Removendo tickets que estão no banco mas não vieram na resposta do GLPI (foram excluídos ou movidos)
        # Somente para tickets NÃO auditados dentro do range de datas pesquisado
        from datetime import datetime
        d_start = datetime.strptime(start_date_str, "%Y-%m-%d")
        d_end = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        if isinstance(processed_ids, list):
            deleted_count = db.query(TicketSla).filter(
                TicketSla.data_fechamento >= d_start,
                TicketSla.data_fechamento <= d_end,
                TicketSla.is_audited == False,
                ~TicketSla.glpi_id.in_(processed_ids)
            ).delete(synchronize_session=False)
            
            if deleted_count > 0:
                db.commit()
                print(f"   [Limpeza] {deleted_count} tickets removidos do Portal (excluídos no GLPI).")

        self._kill_session()
        return {"processed": len(all_tickets), "month": month_str}
    def process_and_save_tickets(self, db: Session, glpi_tickets, month_str):
        print(f"Iniciando processamento de {len(glpi_tickets)} tickets no DB...")
        try:
            rules_query = db.query(SlaRule).all()
            rules = {r.tipo.upper(): r for r in rules_query}
            print(f"Regras carregadas do DB: {len(rules)}")
        except Exception as e:
            print(f"Erro ao carregar regras do DB: {e}")
            return {"error": f"Erro no banco: {e}"}

        categories_cache = {}
        processed_count = 0
        new_count = 0
        all_ti_ids = []
        
        print(f"Iterando nos tickets...")
        for t in glpi_tickets:
            glpi_id = t["id"]
            
            # Buscar nome da categoria e validar se é T.I
            cat_id = t.get("itilcategories_id")
            cat_name = "OUTROS"
            cat_full_name = ""
            
            if cat_id:
                if cat_id in categories_cache:
                    cat_full_name = categories_cache[cat_id]
                else:
                    try:
                        res_cat = requests.get(f"{self.base_url}/ITILCategory/{cat_id}", headers=self.headers, timeout=5)
                        if res_cat.status_code == 200:
                            cat_full_name = res_cat.json().get("completename", "OUTROS").upper()
                            categories_cache[cat_id] = cat_full_name
                    except:
                        cat_full_name = "OUTROS"

            # REGRA DE OURO: Só pegar se for T.I ou se o nome completo contiver T.I (ex: "T.I > ACESSOS")
            # Ignorar explicitamente INFRAESTRUTURA e OUVIDORIA se não estiverem sob T.I
            is_ti = "T.I" in cat_full_name or "TI" in cat_full_name
            
            if not is_ti:
                continue
            
            all_ti_ids.append(glpi_id)

            # Extrair o nome curto da categoria para bater com as regras
            if " > " in cat_full_name:
                cat_name = cat_full_name.split(" > ")[-1].strip()
            else:
                cat_name = cat_full_name.strip()

            # Encontrar regra (Melhorado para bater com planilha)
            rule = None
            
            # Tenta match por nome da categoria no ticket vs TIPO na regra
            for r_tipo, r_obj in rules.items():
                # Exemplos na planilha: "CHAMADOS TI - ACESSOS", "CHAMADOS TI - ERP"
                # Exemplos no GLPI: "ACESSOS", "ERP"
                clean_r_tipo = r_tipo.replace("CHAMADOS TI - ", "").strip()
                if cat_name == clean_r_tipo or cat_name in clean_r_tipo or clean_r_tipo in cat_name:
                    rule = r_obj
                    break
            
            if not rule:
                # Tenta match pelo título do chamado (backup)
                ticket_title = t.get("name", "").upper()
                for r_tipo, r_obj in rules.items():
                    clean_r_tipo = r_tipo.replace("CHAMADOS TI - ", "").strip()
                    if clean_r_tipo in ticket_title and len(clean_r_tipo) > 3:
                        rule = r_obj
                        break
            
            # Se ainda não achou regra específica mas sabemos que é TI, usa a regra OUTROS da TI
            if not rule:
                rule = rules.get("CHAMADOS TI - OUTROS")

            # Definir a categoria final para exibição no Dashboard (baseado na regra achada)
            final_category = cat_name
            if rule:
                final_category = rule.tipo.replace("CHAMADOS TI - ", "").strip()
                if not final_category:
                    final_category = "OUTROS"

            # Cálculo de SLA
            try:
                date_open = datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S")
                date_close = None
                solve_date_str = t.get("solvedate") or t.get("closedate")
                
                if solve_date_str:
                    date_close = datetime.strptime(solve_date_str, "%Y-%m-%d %H:%M:%S")

                tempo_minutos = 0
                status_sla = "SLA OK"
                etapas_total = 0

                # Pega o tempo de solução já calculado pelo GLPI (em segundos)
                solve_delay = t.get("solve_delay_stat", 0)
                
                # Converte para minutos
                tempo_minutos = int(solve_delay) // 60
                
                # Se não houver tempo de solução (chamado aberto), podemos manter em 0 ou calcular parcial
                # Como o usuário quer o tempo que "já vem pronto", usaremos o valor do GLPI.
                if tempo_minutos == 0 and not solve_date_str:
                    # Chamado ainda não resolvido
                    tempo_minutos = 0
                
                # Se o tempo calculado exceder o limite da regra, é SLA NÃO OK
                limit = rule.tempo_limite_minutos if rule else 480
                if tempo_minutos > limit:
                    status_sla = "SLA NÃO OK"
                
                if rule and rule.etapas_audit > 0:
                    etapas_total = rule.etapas_audit

                # Salvar ou Atualizar no DB
                existing = db.query(TicketSla).filter(TicketSla.glpi_id == glpi_id).first()
                if existing:
                    # TRAVA DE SEGURANÇA: Se o ticket já foi auditado manualmente, não sobrescrevemos
                    if existing.is_audited:
                        processed_count += 1
                        continue
                        
                    existing.titulo = t["name"]
                    existing.categoria = final_category
                    existing.data_abertura = date_open
                    existing.data_fechamento = date_close
                    existing.tempo_atendimento_minutos = tempo_minutos
                    existing.status_sla = status_sla
                    existing.mes_referencia = month_str
                    existing.etapas_total = etapas_total
                else:
                    new_ticket = TicketSla(
                        glpi_id=glpi_id,
                        titulo=t["name"],
                        categoria=final_category,
                        data_abertura=date_open,
                        data_fechamento=date_close,
                        tempo_atendimento_minutos=tempo_minutos,
                        status_sla=status_sla,
                        mes_referencia=month_str,
                        etapas_total=etapas_total
                    )
                    db.add(new_ticket)
                    new_count += 1
                
                processed_count += 1
                if processed_count % 50 == 0:
                    print(f"   ... {processed_count} tickets de T.I processados.")
            except Exception as e:
                print(f" ! Erro no ticket {glpi_id}: {e}")

        print(f"Finalizando commit de {processed_count} tickets de T.I...")
        db.commit()
        
        # Retorna a lista de IDs de todos os tickets de TI processados no range
        return all_ti_ids

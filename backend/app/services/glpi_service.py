import requests
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.sla import SlaRule, TicketSla
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

# Carregar env buscando em todas as pastas pai
cur = Path(__file__).resolve().parent
for _ in range(5):
    env_file = cur / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)
    cur = cur.parent

class GLPIService:
    def __init__(self):
        self.base_url = os.getenv("GLPI_BASE_URL", "https://chamados.centraldeconsultas.med.br/apirest.php")
        self.app_token = os.getenv("GLPI_APP_TOKEN", "wakRrwSeCqLtaaKqeT8Pq79IlfqB2uVuEzEpgTFz")
        self.user_token = os.getenv("GLPI_USER_TOKEN", "zw4WIJH5cGbTLnvywJobgC4PXgTcLAXqaCKgv6dv")
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

    def _preload_categories(self) -> dict:
        """
        Pré-carrega TODAS as categorias GLPI de uma vez (em vez de 1 request por ticket).
        Retorna {cat_id: completename_upper}.
        """
        categories = {}
        range_start = 0
        range_step  = 250
        print("   [Categorias] Pré-carregando categorias do GLPI...")

        while True:
            try:
                resp = requests.get(
                    f"{self.base_url}/ITILCategory",
                    headers=self.headers,
                    params={"range": f"{range_start}-{range_start + range_step - 1}"},
                    timeout=15
                )
            except Exception as e:
                print(f"   [Categorias] Falha ao buscar categorias: {e}")
                break

            if resp.status_code not in [200, 206]:
                break

            batch = resp.json()
            if not batch:
                break

            for cat in batch:
                cat_id   = cat.get("id")
                cat_name = cat.get("completename", "").upper()
                if cat_id:
                    categories[cat_id] = cat_name

            if len(batch) < range_step:
                break  # última página

            range_start += range_step

        print(f"   [Categorias] {len(categories)} categorias carregadas.")
        return categories

    def get_tickets_by_date_range(self, db: Session, start_date_str: str, end_date_str: str):
        """
        start_date_str: Formato 'YYYY-MM-DD'
        end_date_str: Formato 'YYYY-MM-DD'
        """
        if not self._init_session():
            return {"error": "Falha na autenticação GLPI"}

        print(f"Buscando tickets de {start_date_str} até {end_date_str} (filtro server-side)...")
        all_tickets = []
        range_start = 0
        range_step  = 100
        page_num    = 0

        # ── Busca server-side com filtro de data de solução ───────────────────
        # Campo 17 = solvedate na API de search do GLPI
        # Inclui tickets resolvidos (status 5) e fechados (status 6)
        # Usa criteria para filtrar diretamente no GLPI (evita varrer todos)
        search_params_base = {
            "criteria[0][field]":      "17",         # solvedate
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]":      f"{start_date_str} 00:00:00",
            "criteria[1][link]":       "AND",
            "criteria[1][field]":      "17",
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]":      f"{end_date_str} 23:59:59",
            # SEM filtro de status — pega solved(5) e closed(6)
            "sort":  "17",
            "order": "ASC",
            "forcedisplay[0]": "1",   # id
            "forcedisplay[1]": "2",   # name/title
            "forcedisplay[2]": "7",   # itilcategories_id
            "forcedisplay[3]": "12",  # status
            "forcedisplay[4]": "15",  # date (abertura)
            "forcedisplay[5]": "17",  # solvedate
            "forcedisplay[6]": "49",  # solve_delay_stat
        }

        use_search_api = True

        while True:
            page_num += 1
            params = dict(search_params_base)
            params["range"] = f"{range_start}-{range_start + range_step - 1}"

            try:
                # Tenta a API de search (/search/Ticket) — muito mais eficiente
                resp = requests.get(
                    f"{self.base_url}/search/Ticket",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
            except requests.exceptions.Timeout:
                print(f"   [AVISO] Timeout na pagina {page_num} (offset {range_start}). Parando busca.")
                break
            except requests.exceptions.RequestException as e:
                print(f"   [ERRO] Falha na pagina {page_num}: {e}. Parando busca.")
                break

            if resp.status_code == 400:
                # Search API não suportada — fallback para /Ticket genérico
                print(f"   [AVISO] Search API retornou 400. Usando fallback /Ticket genérico.")
                use_search_api = False
                break
            elif resp.status_code not in [200, 206]:
                print(f"   [AVISO] GLPI search retornou {resp.status_code} na pagina {page_num}. Parando.")
                break

            search_result = resp.json()

            # A search API retorna {"data": [...], "totalcount": N, ...}
            data = search_result.get("data", [])
            total_count = search_result.get("totalcount", 0)

            if not data:
                break

            # Mapeamento confirmado pelo DEBUG:
            # field "1" = name (título),  field "2" = id do ticket
            # field "7" = nome da categoria JÁ RESOLVIDO (ex: 'T.I', 'CHAMADOS INFRAESTRUTURA > VAZAMENTO')
            # field "12" = status,  field "15" = data abertura,  field "17" = solvedate
            # field "49" = solve_delay_stat (pode ser None — calculamos pelas datas)
            if page_num == 1 and data:
                print(f"   [DEBUG] Mapeamento Search API: {dict(list(data[0].items())[:10])}")

            for item in data:
                ticket_id      = item.get("2") or item.get(2)        # field 2 = ticket ID
                ticket_name    = item.get("1") or item.get(1) or ""  # field 1 = nome/título
                cat_full_name  = str(item.get("7") or item.get(7) or "").upper()  # field 7 = nome categoria JÁ RESOLVIDO
                status         = item.get("12") or item.get(12)
                date_open      = item.get("15") or item.get(15) or ""
                date_solve     = item.get("17") or item.get(17) or ""
                delay_stat_raw = item.get("49")
                if delay_stat_raw is None:
                    delay_stat_raw = item.get(49)

                solve_delay_sec = None
                if delay_stat_raw is not None:
                    try:
                        solve_delay_sec = int(delay_stat_raw)
                    except (ValueError, TypeError):
                        solve_delay_sec = None

                # Se GLPI não forneceu solve_delay_stat válido (> 0), calcula diferença pelas datas como fallback
                if (solve_delay_sec is None or solve_delay_sec <= 0) and date_open and date_solve:
                    try:
                        dt_open  = datetime.strptime(str(date_open)[:19],  "%Y-%m-%d %H:%M:%S")
                        dt_solve = datetime.strptime(str(date_solve)[:19], "%Y-%m-%d %H:%M:%S")
                        solve_delay_sec = int((dt_solve - dt_open).total_seconds())
                    except:
                        solve_delay_sec = 0

                ticket_raw = {
                    "id":             ticket_id,
                    "name":           ticket_name,
                    "cat_full_name":  cat_full_name,   # nome da categoria já resolvido
                    "itilcategories_id": None,         # não necessário — usamos cat_full_name
                    "status":         status,
                    "date":           date_open,
                    "solvedate":      date_solve,
                    "solve_delay_stat": solve_delay_sec or 0,
                }

                if ticket_raw["id"]:
                    all_tickets.append(ticket_raw)

            print(f"   Pagina {page_num:02d} (offset {range_start:5d}): {len(data)} tickets recebidos, {len(all_tickets)} acumulados. (Total GLPI: {total_count})")

            range_start += range_step
            if range_start >= total_count or range_start > 5000:
                break
            if len(data) < range_step:
                break

        # ── Fallback: se search API não funcionou, usa /Ticket genérico ──────
        if not use_search_api:
            print(f"   Usando modo fallback: varrendo todos os tickets...")
            all_tickets = []
            range_start = 0
            page_num    = 0

            while True:
                page_num += 1
                fb_params = {
                    "range": f"{range_start}-{range_start + range_step - 1}",
                    "sort":  "id",
                    "order": "DESC"
                }
                try:
                    resp = requests.get(
                        f"{self.base_url}/Ticket",
                        headers=self.headers,
                        params=fb_params,
                        timeout=30
                    )
                except requests.exceptions.Timeout:
                    print(f"   [AVISO] Timeout na pagina {page_num}. Parando busca.")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"   [ERRO] Falha na pagina {page_num}: {e}. Parando busca.")
                    break

                if resp.status_code not in [200, 206]:
                    break

                tickets_batch = resp.json()
                if not tickets_batch:
                    break

                filtered_count = 0
                for t in tickets_batch:
                    t_solve = t.get("solvedate", "") or t.get("closedate", "")
                    t_solve_str = str(t_solve)[:10] if t_solve else ""
                    if t_solve_str and start_date_str <= t_solve_str <= end_date_str:
                        all_tickets.append(t)
                        filtered_count += 1

                print(f"   Pagina {page_num:02d} (offset {range_start:5d}): {len(tickets_batch)} recebidos, {filtered_count} no período, {len(all_tickets)} acumulados.")

                range_start += range_step
                if range_start > 10000:
                    break

                # Early-stop: se os tickets já são muito mais antigos que o início do período
                if len(tickets_batch) > 0:
                    last_t_date = str(tickets_batch[-1].get("date", ""))[:10]
                    if last_t_date:
                        from datetime import timedelta
                        last_dt  = datetime.strptime(last_t_date, "%Y-%m-%d")
                        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                        if last_dt < (start_dt - timedelta(days=90)):
                            print(f"   Tickets muito antigos. Parando busca.")
                            break

        
        print(f"Total de tickets capturados para processamento: {len(all_tickets)}")
        
        # Search API já retorna cat_full_name resolvido — não precisa de preload
        # Fallback (/Ticket genérico) ainda usa preload para resolver IDs de categoria
        categories_dict = None
        if not use_search_api:
            categories_dict = self._preload_categories()
        
        month_str = start_date_str[:7]
        proc_result = self.process_and_save_tickets(db, all_tickets, month_str, categories_dict)
        
        # processed_ids: lista de glpi_ids de TI+INFRA processados
        processed_ids = proc_result.get("ids", []) if isinstance(proc_result, dict) else (proc_result if isinstance(proc_result, list) else [])
        ti_count      = proc_result.get("ti_count", 0)    if isinstance(proc_result, dict) else 0
        infra_count   = proc_result.get("infra_count", 0) if isinstance(proc_result, dict) else 0
        
        # --- LÓGICA DE LIMPEZA (PURGE) ---
        from datetime import datetime
        d_start = datetime.strptime(start_date_str, "%Y-%m-%d")
        d_end = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        if processed_ids:
            deleted_count = db.query(TicketSla).filter(
                TicketSla.data_fechamento >= d_start,
                TicketSla.data_fechamento <= d_end,
                TicketSla.is_audited == False,
                ~TicketSla.glpi_id.in_(processed_ids)
            ).delete(synchronize_session=False)
            
            if deleted_count > 0:
                db.commit()
                print(f"   [Limpeza] {deleted_count} tickets removidos do Portal (excluidos no GLPI).")

        self._kill_session()
        print(f"   [Resultado] TI: {ti_count} | INFRA: {infra_count} | Total raw: {len(all_tickets)}")
        return {"processed": len(all_tickets), "ti_count": ti_count, "infra_count": infra_count, "month": month_str}
    def process_and_save_tickets(self, db: Session, glpi_tickets, month_str, categories_dict: dict = None):
        print(f"Iniciando processamento de {len(glpi_tickets)} tickets no DB...")
        try:
            rules_query = db.query(SlaRule).all()
            rules = {r.tipo.upper(): r for r in rules_query}
            print(f"Regras carregadas do DB: {len(rules)}")
        except Exception as e:
            print(f"Erro ao carregar regras do DB: {e}")
            return {"error": f"Erro no banco: {e}"}

        # Usa o dicionário pré-carregado (muito mais rápido) ou o cache individual como fallback
        categories_cache = dict(categories_dict) if categories_dict else {}
        processed_count = 0
        new_count = 0
        ti_count    = 0
        infra_count = 0
        all_ti_ids  = []  # IDs de TI + INFRA processados
        
        print(f"Iterando nos tickets...")
        for t in glpi_tickets:
            glpi_id = t["id"]
            
            # Buscar nome da categoria
            cat_name = "OUTROS"
            
            # Search API já retorna cat_full_name resolvido diretamente no ticket
            if t.get("cat_full_name"):
                cat_full_name = t["cat_full_name"]
            else:
                # Fallback (modo /Ticket genérico): resolve por ID
                cat_id = t.get("itilcategories_id")
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
            # Ou se contiver INFRAESTRUTURA / INFRA (ex: "CHAMADOS INFRAESTRUTURA > VAZAMENTO")
            is_ti = "T.I" in cat_full_name or "TI" in cat_full_name
            is_infra = "INFRAESTRUTURA" in cat_full_name or "INFRA" in cat_full_name
            
            if not (is_ti or is_infra):
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
                # Exemplos na planilha: "CHAMADOS TI - ACESSOS", "CHAMADOS INFRAESTRUTURA - VAZAMENTO"
                # Exemplos no GLPI: "ACESSOS", "VAZAMENTO"
                clean_r_tipo = r_tipo.replace("CHAMADOS TI - ", "").replace("CHAMADOS INFRAESTRUTURA - ", "").strip()
                
                is_rule_ti = "CHAMADOS TI -" in r_tipo
                is_rule_infra = "CHAMADOS INFRAESTRUTURA -" in r_tipo
                
                if is_ti and is_rule_ti:
                    if cat_name == clean_r_tipo or cat_name in clean_r_tipo or clean_r_tipo in cat_name:
                        rule = r_obj
                        break
                elif is_infra and is_rule_infra:
                    if cat_name == clean_r_tipo or cat_name in clean_r_tipo or clean_r_tipo in cat_name:
                        rule = r_obj
                        break
            
            if not rule:
                # Tenta match pelo título do chamado (backup)
                ticket_title = t.get("name", "").upper()
                for r_tipo, r_obj in rules.items():
                    clean_r_tipo = r_tipo.replace("CHAMADOS TI - ", "").replace("CHAMADOS INFRAESTRUTURA - ", "").strip()
                    is_rule_ti = "CHAMADOS TI -" in r_tipo
                    is_rule_infra = "CHAMADOS INFRAESTRUTURA -" in r_tipo
                    
                    if is_ti and is_rule_ti:
                        if clean_r_tipo in ticket_title and len(clean_r_tipo) > 3:
                            rule = r_obj
                            break
                    elif is_infra and is_rule_infra:
                        if clean_r_tipo in ticket_title and len(clean_r_tipo) > 3:
                            rule = r_obj
                            break
            
            # Se ainda não achou regra específica mas sabemos a área, usa a regra OUTROS correspondente
            if not rule:
                if is_ti:
                    rule = rules.get("CHAMADOS TI - OUTROS")
                elif is_infra:
                    rule = rules.get("CHAMADOS INFRAESTRUTURA - OUTROS")

            # Definir a categoria final para exibição no Dashboard (baseado na regra achada)
            final_category = cat_name
            if rule:
                final_category = rule.tipo.replace("CHAMADOS TI - ", "").replace("CHAMADOS INFRAESTRUTURA - ", "").strip()
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

                # Prioriza a estatística de tempo de solução útil do GLPI (solve_delay_stat),
                # que já desconta horários não comerciais, finais de semana e tempo pausado (pendente).
                solve_delay = t.get("solve_delay_stat")
                if solve_delay is not None and int(solve_delay) > 0:
                    tempo_minutos = int(solve_delay) // 60
                elif date_open and date_close:
                    tempo_minutos = int((date_close - date_open).total_seconds()) // 60
                else:
                    tempo_minutos = 0
                    
                if tempo_minutos == 0 and not solve_date_str:
                    # Chamado ainda não resolvido
                    tempo_minutos = 0
                
                # Se o tempo calculado exceder o limite da regra, é SLA NÃO OK
                limit = rule.tempo_limite_minutos if rule else 480
                if tempo_minutos > limit:
                    status_sla = "SLA NÃO OK"
                
                if rule and rule.etapas_audit > 0:
                    etapas_total = rule.etapas_audit

                # Define o mês de referência baseado no data_fechamento (ou data_abertura se não fechado)
                ticket_month = month_str
                if date_close:
                    ticket_month = date_close.strftime("%Y-%m")
                elif date_open:
                    ticket_month = date_open.strftime("%Y-%m")

                # Salvar ou Atualizar no DB
                existing = db.query(TicketSla).filter(TicketSla.glpi_id == glpi_id).first()
                if existing:
                    # TRAVA DE SEGURANÇA: Se o ticket já foi auditado manualmente, não sobrescrevemos
                    if existing.is_audited:
                        # Contar separado por area para refletir no log do processamento
                        if existing.area == "INFRA":
                            infra_count += 1
                        else:
                            ti_count += 1
                        processed_count += 1
                        continue
                        
                    existing.titulo = t["name"]
                    existing.categoria = final_category
                    existing.data_abertura = date_open
                    existing.data_fechamento = date_close
                    existing.tempo_atendimento_minutos = tempo_minutos
                    existing.status_sla = status_sla
                    existing.mes_referencia = ticket_month
                    existing.etapas_total = etapas_total
                    existing.area = "INFRA" if is_infra else "TI"
                else:
                    new_ticket = TicketSla(
                        glpi_id=glpi_id,
                        titulo=t["name"],
                        categoria=final_category,
                        data_abertura=date_open,
                        data_fechamento=date_close,
                        tempo_atendimento_minutos=tempo_minutos,
                        status_sla=status_sla,
                        mes_referencia=ticket_month,
                        etapas_total=etapas_total,
                        area="INFRA" if is_infra else "TI"
                    )
                    db.add(new_ticket)
                    new_count += 1
                
                # Contar separado por area
                if is_infra:
                    infra_count += 1
                else:
                    ti_count += 1
                
                processed_count += 1
                if processed_count % 50 == 0:
                    print(f"   ... {processed_count} tickets processados (TI: {ti_count} | INFRA: {infra_count}).")
            except Exception as e:
                print(f" ! Erro no ticket {glpi_id}: {e}")

        print(f"Finalizando commit: {processed_count} tickets (TI: {ti_count} | INFRA: {infra_count} | novos: {new_count})...")
        db.commit()
        
        return {
            "ids":         all_ti_ids,
            "processed":   processed_count,
            "ti_count":    ti_count,
            "infra_count": infra_count,
            "new_count":   new_count
        }


class Settings:
    SECRET_KEY = "supersecretkey"
    ALGORITHM = "HS256"

    # ========================================
    # CONFIGURAÇÃO DE COMISSÕES
    # ========================================

    # Cargos que recebem comissão sobre TODA A FILIAL
    CARGOS_FILIAL_COMPLETA = [
        "GERENTE",
        "COORDENADOR",
        "MONITOR",
        "MONITORA",
        # Adicione outros cargos aqui conforme necessário
        # "DIRETOR",
        # "SUPERVISOR GERAL",
    ]

    # Cargos que recebem comissão sobre HIERARQUIA (equipe)
    CARGOS_HIERARQUIA = [
        "SUPERVISOR",
        # Adicione outros cargos aqui
    ]

    # Cargos que recebem comissão apenas sobre vendas PRÓPRIAS
    CARGOS_VENDAS_PROPRIAS = [
        "ATENDENTE",
        "ESTAGIÁRIO",
        "ESTAGIARIA",
        # Adicione outros cargos aqui
    ]

settings = Settings()
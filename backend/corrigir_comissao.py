# Script para corrigir o arquivo comissao.py

import re

# Ler o backup
with open('app/routes/comissao_backup.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Procurar o trecho que precisa ser substituído
trecho_antigo = r'''            print\(f"\[COMISSÃO\] Total de IDs para buscar vendas: \{len\(ids_para_buscar\)\}"\)
        
    # Buscar vendas de todos os IDs determinados
    vendas = db\.query\(BaseCampanhas\)\.filter\(
        BaseCampanhas\.cod_usuario\.in_\(ids_para_buscar\),
        extract\('year', BaseCampanhas\.mes\) == mes_referencia\.year,
        extract\('month', BaseCampanhas\.mes\) == mes_referencia\.month
    \)\.all\(\)
    print\(f"\[COMISSÃO\] 👥 Buscando vendas de \{len\(ids_para_buscar\)\} colaboradores \(todas filiais\)"\)        print\(f"\[COMISSÃO\] Total de vendas encontradas: \{len\(vendas\)\}"\)'''

trecho_novo = '''            print(f"[COMISSÃO] Total de IDs para buscar vendas: {len(ids_para_buscar)}")
        
    # Buscar vendas
    cargo_lower = cargo.lower()
    
    if 'coordenador' in cargo_lower or 'gerente' in cargo_lower:
        # COORDENADORES/GERENTES: Vendas da EQUIPE (todas filiais) + Desligados da UNIDADE
        # Parte 1: Vendas da equipe (em qualquer filial)
        vendas_equipe = db.query(BaseCampanhas).filter(
            BaseCampanhas.cod_usuario.in_(ids_para_buscar),
            extract('year', BaseCampanhas.mes) == mes_referencia.year,
            extract('month', BaseCampanhas.mes) == mes_referencia.month
        ).all()
        
        # Parte 2: Vendas de desligados/sem meta DA MESMA UNIDADE (filial)
        vendas_desligados = db.query(BaseCampanhas).filter(
            BaseCampanhas.filial == colaborador.unidade,
            ~BaseCampanhas.cod_usuario.in_(ids_para_buscar),  # IDs que NÃO estão na equipe
            extract('year', BaseCampanhas.mes) == mes_referencia.year,
            extract('month', BaseCampanhas.mes) == mes_referencia.month
        ).all()
        
        # Combinar as duas listas
        vendas = vendas_equipe + vendas_desligados
        
        print(f"[COMISSÃO] 🏢 COORDENADOR/GERENTE:")
        print(f"[COMISSÃO]    ├─ Vendas da EQUIPE ({len(ids_para_buscar)} IDs, todas filiais): {len(vendas_equipe)}")
        print(f"[COMISSÃO]    └─ Vendas de DESLIGADOS (filial '{colaborador.unidade}'): {len(vendas_desligados)}")
        
        if vendas_desligados:
            # Mostrar quem são os desligados
            desligados_ids = set([v.cod_usuario for v in vendas_desligados])
            print(f"[COMISSÃO]       IDs desligados/sem meta: {', '.join(sorted(desligados_ids))}")
    else:
        # SUPERVISORES/ATENDENTES: Apenas vendas dos IDs da equipe
        vendas = db.query(BaseCampanhas).filter(
            BaseCampanhas.cod_usuario.in_(ids_para_buscar),
            extract('year', BaseCampanhas.mes) == mes_referencia.year,
            extract('month', BaseCampanhas.mes) == mes_referencia.month
        ).all()
        print(f"[COMISSÃO] 👥 SUPERVISOR/ATENDENTE: Buscando vendas de {len(ids_para_buscar)} colaboradores")
    
    print(f"[COMISSÃO] Total de vendas encontradas: {len(vendas)}")'''

# Fazer a substituição
conteudo_novo = re.sub(trecho_antigo, trecho_novo, conteudo, flags=re.DOTALL)

# Salvar
with open('app/routes/comissao.py', 'w', encoding='utf-8') as f:
    f.write(conteudo_novo)

print("✅ Arquivo corrigido com sucesso!")

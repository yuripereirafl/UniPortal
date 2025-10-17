-- ===================================
-- QUERIES DE DIAGNÓSTICO - EQUIPE ADM
-- ===================================

-- QUERY 1: Ver quem tem equipe = 'ADM' na tabela de metas
select nome,
       cargo,
       equipe,
       unidade,
       id_eyal,
       mes_ref
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
   and equipe like '%ADM%'
 order by nome;

-- ===================================

-- QUERY 2: Ver valores DISTINTOS do campo 'equipe' na Central de Marcações
select distinct equipe,
                count(*) as qtde_colaboradores
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
   and unidade = 'CENTRAL DE MARCACÕES'
 group by equipe
 order by equipe;

-- ===================================

-- QUERY 3: Ver colaboradores ADMINISTRATIVO
select nome,
       cargo,
       equipe,
       unidade,
       id_eyal
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
   and unidade = 'CENTRAL DE MARCACÕES'
   and cargo like '%ADMIN%'
 order by nome;

-- ===================================

-- QUERY 4: Ver TODOS os colaboradores com unidade CM e equipe diferente de A/B/C
select nome,
       cargo,
       equipe,
       unidade,
       id_eyal
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
   and unidade = 'CENTRAL DE MARCACÕES'
   and equipe not in ( 'EQUIPE A',
                       'EQUIPE B',
                       'EQUIPE C' )
 order by equipe,
          nome;

-- ===================================

-- QUERY 5: Buscar por colaboradores específicos que vimos na planilha
select nome,
       cargo,
       equipe,
       unidade,
       id_eyal
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
   and nome in ( 'EDUARDA ANTUNES NEUMANN',
                 'VITORIA CRISTINA MATHIAS MILITAO',
                 'GABRIEL DA SILVA MACHADO',
                 'LUCINARA MARQUES DOS SANTOS',
                 'LUIS FERNANDO OTT MAI' )
 order by nome;

-- ===================================

-- QUERY 6: Ver TODOS os valores distintos de 'equipe' em TODA a tabela
select distinct equipe
  from rh_homologacao.metas_colaboradores
 where mes_ref = '2025-10-01'
 order by equipe;
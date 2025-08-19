-- EXECUTE ESTES COMANDOS NO SEU BANCO POSTGRESQL
-- Comandos simples para adicionar as colunas necessárias

-- 1. Adicionar coluna data_afastamento
alter table funcionarios add column data_afastamento

date;

-- 2. Adicionar coluna data_retorno  
alter table funcionarios add column data_retorno

date;

-- 3. Adicionar coluna motivo_afastamento
alter table funcionarios add column motivo_afastamento

text;

-- 4. Verificar se as colunas foram criadas
select column_name,
       data_type,
       is_nullable
  from information_schema.columns
 where table_name = 'funcionarios'
   and column_name in ( 'data_afastamento',
                        'data_retorno',
                        'motivo_afastamento' )
 order by column_name;
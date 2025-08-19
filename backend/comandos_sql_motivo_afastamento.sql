-- Comandos SQL para adicionar funcionalidade de motivos de afastamento
-- Execute estes comandos diretamente no seu banco PostgreSQL

-- 1. Adicionar a nova coluna motivo_afastamento
alter table funcionarios add column motivo_afastamento

text;

-- 2. (OPCIONAL) Criar tabela de motivos padrões para futuras consultas/relatórios
create table motivos_afastamento (
   id         serial primary key,
   descricao  varchar(100) not null unique,
   ativo      boolean default true,
   created_at timestamp default current_timestamp
);

-- 3. (OPCIONAL) Inserir os motivos padrões
insert into motivos_afastamento ( descricao ) values ( 'Férias' ),( 'Licença Médica' ),( 'Licença Maternidade' ),( 'Licença Paternidade'
),( 'Licença sem Vencimentos' ),( 'Afastamento INSS' ),( 'Suspensão' ),( 'Capacitação/Treinamento' ),( 'Outros' );

-- 4. Verificar se a coluna foi adicionada com sucesso
select column_name,
       data_type,
       is_nullable
  from information_schema.columns
 where table_name = 'funcionarios'
   and column_name = 'motivo_afastamento';

-- 5. (OPCIONAL) Verificar motivos inseridos
select *
  from motivos_afastamento
 order by id;

-- 6. (OPCIONAL) Adicionar comentários
comment on column funcionarios.motivo_afastamento is
   'Motivo do afastamento do funcionário';
comment on table motivos_afastamento is
   'Tabela com motivos padrões de afastamento para consultas e relatórios';

-- Observações:
-- - A coluna motivo_afastamento será criada como TEXT e permitirá valores NULL
-- - Funcionários existentes terão NULL neste campo até que seja preenchido
-- - A tabela motivos_afastamento é opcional mas útil para relatórios futuros
-- - O frontend já está configurado com os valores padrões
-- - Quando selecionar "Outros", o sistema salvará como "Outros: [descrição específica]"
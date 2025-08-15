import sqlite3

conn = sqlite3.connect('system_ti.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE funcionarios ADD COLUMN cpf TEXT;")
except sqlite3.OperationalError:
    print("Coluna 'cpf' já existe.")

try:
    cursor.execute("ALTER TABLE funcionarios ADD COLUMN data_afastamento TEXT;")
except sqlite3.OperationalError:
    print("Coluna 'data_afastamento' já existe.")

try:
    cursor.execute("ALTER TABLE funcionarios ADD COLUMN tipo_contrato TEXT;")
except sqlite3.OperationalError:
    print("Coluna 'tipo_contrato' já existe.")

try:
    cursor.execute("ALTER TABLE funcionarios ADD COLUMN data_retorno TEXT;")
except sqlite3.OperationalError:
    print("Coluna 'data_retorno' já existe.")

conn.commit()
conn.close()

print("Colunas adicionadas (se necessário)!")
import csv
from app.database import SessionLocal
from app.models.sistema import Sistema

def importar_sistemas_csv(caminho_csv):
    session = SessionLocal()
    # Tenta abrir em utf-8, se falhar tenta latin1
    csvfile = None
    reader = None
    encoding_used = None
    try:
        try:
            csvfile = open(caminho_csv, newline='', encoding='utf-8')
            reader = csv.reader(csvfile, delimiter=';')
            encoding_used = 'utf-8'
            # Testa leitura para forçar erro de encoding logo no início
            _ = next(reader, None)
            csvfile.seek(0)
            reader = csv.reader(csvfile, delimiter=';')
        except UnicodeDecodeError:
            if csvfile:
                csvfile.close()
            csvfile = open(caminho_csv, newline='', encoding='latin1')
            reader = csv.reader(csvfile, delimiter=';')
            encoding_used = 'latin1'
        # Ignora header se existir
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            nome = row[0].strip() if len(row) > 0 else ''
            descricao = row[1].strip() if len(row) > 1 else ''
            status = row[2].strip() if len(row) > 2 else 'Ativo'
            if not nome:
                continue
            # Verifica se já existe
            existe = session.query(Sistema).filter_by(nome=nome).first()
            if not existe:
                sistema = Sistema(nome=nome, descricao=descricao, status=status)
                session.add(sistema)
        session.commit()
        csvfile.close()
        print(f'Importação de sistemas concluída com sucesso! (encoding: {encoding_used})')
    except Exception as e:
        if csvfile:
            try:
                csvfile.close()
            except:
                pass
        print(f'Erro ao importar: {e}')
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    caminho = input('Digite o caminho do arquivo CSV com os sistemas: ')
    importar_sistemas_csv(caminho)

import csv
from app.database import SessionLocal
from app.models.setor import Setor

def importar_setores_csv(caminho_csv):
    session = SessionLocal()
    csvfile = None
    reader = None
    encoding_used = None
    try:
        try:
            csvfile = open(caminho_csv, newline='', encoding='utf-8')
            reader = csv.reader(csvfile, delimiter=';')
            encoding_used = 'utf-8'
            _ = next(reader, None)
            csvfile.seek(0)
            reader = csv.reader(csvfile, delimiter=';')
        except UnicodeDecodeError:
            if csvfile:
                csvfile.close()
            csvfile = open(caminho_csv, newline='', encoding='latin1')
            reader = csv.reader(csvfile, delimiter=';')
            encoding_used = 'latin1'
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            nome = row[0].strip() if len(row) > 0 else ''
            descricao = row[1].strip() if len(row) > 1 else ''
            if not nome:
                continue
            existe = session.query(Setor).filter_by(nome=nome).first()
            if not existe:
                setor = Setor(nome=nome, descricao=descricao)
                session.add(setor)
        session.commit()
        csvfile.close()
        print(f'Importação de setores concluída com sucesso! (encoding: {encoding_used})')
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
    caminho = input('Digite o caminho do arquivo CSV com os setores: ')
    importar_setores_csv(caminho)

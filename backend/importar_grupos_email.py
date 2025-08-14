import csv
from app.database import SessionLocal
from app.models.grupo_email import GrupoEmail

def importar_grupos_email_csv(caminho_csv):
    session = SessionLocal()
    try:
        with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row:
                    continue
                nome = row[0].strip()
                if not nome:
                    continue
                # Verifica se já existe
                existe = session.query(GrupoEmail).filter_by(nome=nome).first()
                if not existe:
                    grupo = GrupoEmail(nome=nome)
                    session.add(grupo)
            session.commit()
        print('Importação concluída com sucesso!')
    except Exception as e:
        print(f'Erro ao importar: {e}')
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    caminho = input('Digite o caminho do arquivo CSV com os nomes dos grupos de e-mail: ')
    importar_grupos_email_csv(caminho)

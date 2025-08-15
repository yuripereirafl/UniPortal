from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Importar todos os modelos para garantir que sejam registrados
from app.models.funcionario import Funcionario
from app.models.sistema import Sistema
from app.models.setor import Setor
from app.models.grupo_email import GrupoEmail
from app.models.grupo_pasta import GrupoPasta  # Adicione se existir
from app.models.usuario import Usuario

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://dadosrh:dadosrh@192.168.1.37:5432/dadosrh"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  
    pool_recycle=300,    
    echo=False,
        connect_args={"options": "-csearch_path=rh_homologacao,public"}          
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Testa a conexão com o PostgreSQL"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexão com PostgreSQL funcionando!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

# Para debug (opcional)
if __name__ == "__main__":
    test_connection()


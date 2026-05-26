from app.database import engine
from app.models.base import Base
# Make sure Notebook and Dominio are imported so they're registered
from app.models.notebook import Notebook
from app.models.dominio import Dominio

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done!")

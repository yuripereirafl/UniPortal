from sqlalchemy import Column, Integer, Numeric, String
from app.models.base import Base

class Meta(Base):
    __tablename__ = 'meta'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    calc_meta = Column(Numeric(2,1), nullable=False)
    tipo_pgto = Column(String(30), nullable=False)

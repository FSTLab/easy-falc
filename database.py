from sqlalchemy import MetaData, Column, INteger, String
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Mot(Base):
    __tablename__ = 'Mots'

    numero = Column(Integer, primary_key=True)
    mot = Column(String(50))

    def __init__(self, description):
        self.description = description

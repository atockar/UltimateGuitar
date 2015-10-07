'''
Create FactTab table on AWS MySQL database to hold tab information
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String

# Connect to AWS
engine = create_engine('mysql://', echo=False)
Base = declarative_base()

class FactTab(Base):
    __tablename__ = 'FactTab'
    id = Column(BigInteger, primary_key=True)
    artistName = Column(String(50), nullable=False)
    songName = Column(String(80), nullable=False)
    version = Column(SmallInteger, nullable=False)
    tuning = Column(String(30))
    tabViews = Column(Integer)
    transcription = Column(String(20), nullable=False)
    position = Column(Integer, nullable=False)

Base.metadata.create_all(engine)
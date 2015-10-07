'''
Create DimChord table on AWS MySQL database to hold chord information
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, SmallInteger, Integer, String

# Connect to AWS
cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':'UltimateGuitar'}	# AWS credentials
engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
Base = declarative_base()

class DimChord(Base):
    __tablename__ = 'DimChord'
    id = Column(Integer, primary_key=True)
    chordName = Column(String(10), nullable=False)
    transcription = Column(String(20), nullable=False)
    difficulty = Column(String(20))
    key = Column(String(2))
    pitch = Column(SmallInteger)
    
Base.metadata.create_all(engine)
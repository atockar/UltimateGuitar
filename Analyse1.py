import time

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ugscrape.ugscrape.SQLsetup import FactTab

'''Connect to AWS'''
def connectAWS():
	cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':''}	# AWS credentials
	engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
	Base = declarative_base()

	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	return session

'''Most popular note'''
def topNote(session):
	start = time.time()

	countTrans = func.count(FactTab.transcription).label('count')
	topNotes = session.query(FactTab.transcription, countTrans).\
		group_by(FactTab.transcription).\
		having(countTrans>5000).\
		order_by(countTrans.desc()).\
		all()

	print topNotes

	print (time.time() - start)

if __name__ == '__main__':
	session = connectAWS()
	topNote(session)

# # Most popular note by position
# SELECT transcription, position, count(transcription) as count
# FROM UltimateGuitar.FactTab
# GROUP BY transcription, position
# HAVING count(transcription) > 100
# ORDER BY position, count(transcription) desc;

# # Most popular chord
# SELECT chordName, count(chordName) as count
# FROM UltimateGuitar.FactTab as FT
# INNER JOIN UltimateGuitar.DimChord as DC
# ON FT.transcription = DC.transcription
# GROUP BY chordName
# HAVING count(chordName) > 1000
# ORDER BY count(chordName) desc;

# # Most popular key
# SELECT `key`, count(`key`) as count
# FROM UltimateGuitar.FactTab as FT
# INNER JOIN UltimateGuitar.DimChord as DC
# ON FT.transcription = DC.transcription
# GROUP BY `key`
# HAVING count(`key`) > 50000
# ORDER BY count(`key`) desc;

# # Most popular pitch
# SELECT pitch, count(pitch) as count
# FROM UltimateGuitar.FactTab as FT
# INNER JOIN UltimateGuitar.DimChord as DC
# ON FT.transcription = DC.transcription
# GROUP BY pitch
# HAVING count(pitch) > 50000
# ORDER BY count(pitch) desc;

# # Most popular tuning
# SELECT tuning, count(tuning) as count
# FROM UltimateGuitar.FactTab
# GROUP BY tuning
# HAVING count(tuning) > 50000
# ORDER BY count(tuning) desc;

# # Most popular 2-step key progression
# # No idea - might have to look up bigrams. Position has to be the variable, so difficult.
# # Alternatively can try do it by conditioning on a certain key and position e.g.:
# /*
# SELECT `key`, count(`key`) as count
# FROM (
# 	SELECT artistName, songName, version
# 	FROM UltimateGuitar.FactTab as FT
# 	INNER JOIN UltimateGuitar.DimChord as DC
# 	ON FT.transcription = DC.transcription
# 	WHERE position = 1 and `key` = 'E'
#     ) as k
# INNER JOIN UltimateGuitar.FactTab as FT2
# ON k.artistName = FT2.artistName
# AND k.songName = FT2.songName
# AND k.version = FT2.version
# INNER JOIN UltimateGuitar.DimChord as DC2
# ON FT2.transcription = DC2.transcription
# WHERE position = 2
# GROUP BY `key`;
# */
# SELECT k.`key` as key1, DC2.`key` as key2, count(*) as count
# FROM (
# 	SELECT artistName, songName, version, position, `key`
# 	FROM UltimateGuitar.FactTab as FT
# 	INNER JOIN UltimateGuitar.DimChord as DC
# 	ON FT.transcription = DC.transcription
#     ) as k
# INNER JOIN UltimateGuitar.FactTab as FT2
# ON k.artistName = FT2.artistName
# AND k.songName = FT2.songName
# AND k.version = FT2.version
# INNER JOIN UltimateGuitar.DimChord as DC2
# ON FT2.transcription = DC2.transcription
# WHERE FT2.position = (k.position+1)
# GROUP BY key1, key2;

#! python2
'''
This program calls a couple of functions to:
	- scrape and parse chord definitions
	- add individual notes to classify as chords to enrich definitions 
to create a chord reference table that can be mapped to transcriptions
'''

import os, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from chordscrape.SQLsetup import DimChord

''' Calls scrapy and records execution time '''
def scrape_chords():
	start = time.time()
	os.system("C:\\Python27\\Scripts\\scrapy crawl chords")
	print (time.time() - start)

'''Connects to AWS MySQL database and initialises a session'''
def AWS_start_session():
	cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':'UltimateGuitar'}	# AWS credentials
	engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
	Base = declarative_base()

	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	return session

'''Add individual notes to chord table'''
def add_chords():
	session = AWS_start_session()

	keys = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
	steps = [5,4,5,5,5]
	for s, string in enumerate('EBGDAE'):
		for fret in range(25):
			ki = keys[(keys.index(string)+fret)%12]
			pch = int((sum(steps[s:])+fret)/12)+1
			trans = ['-']*6
			trans[s] = str(fret)
			trans = " ".join(trans)

			# Insert into DimChord
			newChord = DimChord(chordName=ki,transcription=trans,difficulty='Rookie',key=ki,pitch=pch)
			session.add(newChord)
			session.commit()

if __name__ == '__main__':
	scrape_chords()
	add_chords()
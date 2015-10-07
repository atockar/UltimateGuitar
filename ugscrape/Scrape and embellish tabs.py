
#! python2
'''
This program calls a couple of key functions to:
	- scrape, parse and store all guitar tabs from Ultimate-Guitar.com using scrapy
	- embellish the database (using MusicBrainzDB) with artist and song information for each tab
'''

import os, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, SmallInteger, String
from ugscrape.SQLsetup import FactTab

import musicbrainzngs as mb
mb.set_useragent("Ultimate Guitar analyser", "0.1","")

'''Calls scrapy to crawl Ultimate-Guitar.com and times the process''' 
def scrape_UG():
	start = time.time()
	os.system("C:\\Python27\\Scripts\\scrapy crawl ultimateguitar")
	print (time.time() - start)

	# Diagnostics
	os.system("ls")

'''Creates DimSong table to store MusicBrainz information'''
def create_DimSong(e,b):
	class DimSong(b):
		__tablename__ = 'DimSong'
		id = Column(BigInteger, primary_key=True)
		artistName = Column(String(50), nullable=False)
		songName = Column(String(80), nullable=False)
		genre = Column(String(80))
		nationality = Column(String(30))
		year = Column(SmallInteger)
		length = Column(SmallInteger)

	b.metadata.create_all(e)
	return DimSong

'''Lookup artist information from MusicBrainz database'''
def lookup_artist_MB(artistName):
	try:
		artistInfo = mb.search_artists(artist=artistName,limit=1)['artist-list'][0]
	except IndexError:
		return ("","")
	try:
		country = artistInfo['country']
	except:
		country = ""
	try:
		genre = ",".join([g['name'] for g in artistInfo['tag-list']])
	except:
		genre = ""

	return (country, genre)

'''Lookup song information from MusicBrainz database'''
def lookup_song_MB(artistName, songName):
	try:
		songInfo = mb.search_recordings(query=songName,artist=artistName,limit=1)['recording-list'][0]
	except IndexError:
		return(1900,0)
	try:
		year = int(songInfo['release-list'][0]['date'][0:4])
	except:
		year = 1900
	try:
		length = int(songInfo['release-list'][0]['medium-list'][1]['track-list'][0]['length'])/1000
	except:
		length = 0
	
	return (year, length)

	
'''Embellish song and artist information from MusicBrainz database (and times the execution)'''
def mb_embellish():

	start = time.time()

	# Connect to AWS
	cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':''}	# AWS credentials
	engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
	Base = declarative_base()

	DimSong = create_DimSong(engine, Base)

	# Pull all artists and songs from FactTab
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	songs = session.query(FactTab.artistName, FactTab.songName).distinct()	# SELECT DISTINCT artistName, songName FROM FactTab

	# Now populate from MusicBrainz API

	fields = dict.fromkeys(["country","genre","year","length"])
	lastArtist = ""
	for it, row in enumerate(songs):
		try:
			if it > 52000:
				if row[0] != lastArtist:
					fields["country"], fields["genre"] = lookup_artist_MB(row[0])
					fields["year"], fields["length"] = lookup_song_MB(row[0], row[1])
					lastArtist = row[0]
				else:
					fields["year"], fields["length"] = lookup_song_MB(row[0], row[1])

				# Insert into DimSong
				newSong = DimSong(artistName=row[0],songName=row[1],nationality=fields["country"],genre=fields["genre"],year=fields["year"],length=fields["length"])
				session.add(newSong)
				session.commit()

			if (it % 1000) == 0:
				print "Iteration: " + str(it)
				print str(time.time() - start) + " seconds"
				start = time.time()
				print "Artist: " + str(row[0])
				print "Song: " + str(row[1])
		except UnicodeEncodeError:
			session.rollback()

	print (time.time() - start)

if __name__ == '__main__':
	scrape_UG()
	mb_embellish()
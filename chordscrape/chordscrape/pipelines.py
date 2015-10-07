# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float
import SQLsetup

'''Error handling and formatting for scraped transcriptions'''
class ChordParsePipeline(object):
	def process_item(self, item, spider):
		if item['transcription']:
			item = self.parse_trans(item)
			return item
		else:
			raise DropItem("Missing transcription")

	def parse_trans(self, item):
		trans = item['transcription'].strip().split(" ")[::-1]
		item['transcription'] = " ".join(trans).replace("x","-")
		return item

'''Load data into AWS MySQL database, and embellish with key and pitch information'''
class PopulateAWSPipeline(object):
	def __init__(self):
		cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':'UltimateGuitar'}	# AWS credentials
		self.engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
		self.Base = declarative_base()

	def process_item(self, item, spider):
		self.Base.metadata.bind = self.engine
		DBSession = sessionmaker(bind=self.engine)
		session = DBSession()

		# Calculate key
		keys = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
		if '#' in item['chordName']:
			ki = item['chordName'][0] + "#"
		elif 'b' in item['chordName']:
			ki = keys[keys.index(item['chordName'][0])-1]
		else:
			ki = item['chordName'][0]

		# Calculate pitch
		steps = [24,19,15,10,5,0]
		pitches = []
		for n,s in zip(item['transcription'].split(" "),steps):
			if n == "-":
				pitches.append("")	# i.e. ignore this string
			else:
				pitches.append(int(n)+s)
		pch = int(min(pitches)/12)+1

		newChord = SQLsetup.DimChord(transcription=item['transcription'],chordName=item['chordName'],difficulty=item['difficulty'],key=ki,pitch=pch)
		session.add(newChord)
		session.commit()

		return item
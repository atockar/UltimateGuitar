# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import SQLsetup

'''Extracts individual notes from guitar tab text'''
class ParseNotesPipeline(object):
	def process_item(self, item, spider):
		if item['tab']:
			item = self.parseTab(item)
			return item
		else:
			with open('MissingCount.txt','a') as f:
				f.write('0')	# then can count characters to find how many are missing
			raise DropItem("Missing tab")

	def parseTab(self, item):
		# Arrange tab into 6-line blocks
		lines = item['tab'].split("\n")
		for lineNum in range(0,len(lines)):
			if len(lines[lineNum]) < 10:
				lines[lineNum] = "break"

		blocks = '\n'.join(lines).split("break")

		# Remove spaces and blocks that aren't 6 strings
		blocks = [x for x in blocks if len(x)>1 and x.strip().count("\n") == 5]

		if blocks == []:
			with open('BadTabCount.txt','a') as f:
				f.write('0')	# then can count characters to find how many are not in standard format
			raise DropItem("Tab not in standard format")

		chords = {}
		startPos = 1
		for block in blocks:

			# Find start positions for each chord (as some take 2 spaces)
			blockLength = max([len(line) for line in block.split("\n")])
			chordPositions = {pos for pos in range(blockLength)}
			for line in block.strip().split("\n"):
				for i, symbol in enumerate(line):
					if str(symbol) in ['1','2'] and (i+1) != len(line):
						if re.match(r'[0-9]',line[i+1]) and (i in chordPositions):
							chordPositions.discard(i+1)

			# Now pull out chords separately
			for line in block.strip().split("\n"):
				for i in chordPositions:
					if (i+1) in chordPositions or (i+1) == len(line):
						try:
							try:
								chords[startPos+i] += " " + str(line[i])
							except KeyError:
								chords[startPos+i] = str(line[i])
						except IndexError:
							with open('IndexErrorCount.txt','a') as f:
								f.write('0')
							try:
								chords[startPos+i] += " -"
							except KeyError:
								chords[startPos+i] = "-"
					else:
						n = str(line[i:i+2])
						n = ('-' if n == '--' else n.replace('-',''))
						try:
							chords[startPos+i] += " " + n
						except KeyError:
							chords[startPos+i] = n
							
			startPos += blockLength

		item['tab'] = chords

		return item

'''Stores items in AWS MySQL database (one row per note)'''
class PopulateAWSPipelineFlat(object):
	def __init__(self):
		cred = {'user':'','pwrd':'','host':'','port':'3306','dbname':''}	# AWS credentials
		self.engine = create_engine('mysql://'+cred['user']+':'+cred['pwrd']+'@'+cred['host']+':'+cred['port']+'/'+cred['dbname'], echo=False)
		self.Base = declarative_base()

	def process_item(self, item, spider):
		self.Base.metadata.bind = self.engine
		DBSession = sessionmaker(bind=self.engine)
		session = DBSession()

		pos = 1
		with open('ParsedCount.txt','a') as f:
			f.write('0')	# then can count characters to find how many have been parsed correctly
		for tab in item['tab']:
			if re.match(r'.*[0-9].*',item['tab'][tab]):
				newRecord = SQLsetup.FactTab(artistName=item['artistName'],songName=item['songName'],version=item['version'],tuning=item['tuning'],tabViews=item['views'],transcription=item['tab'][tab],position=pos)
				session.add(newRecord)
				session.commit()
				pos += 1
		
		return item
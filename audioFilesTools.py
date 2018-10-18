# -*- coding: utf-8 -*-
import eyed3

#Remove logs
eyed3.log.setLevel("ERROR")

def isMono(filename):
	audiofile = eyed3.load(filename)
	return audiofile.info.mode == 'Mono'


# Get genre from built-in audio tags
def getGenre(filename):
	audiofile = eyed3.load(filename)
	#No genre
	if not audiofile.tag.genre:
		return None
	else:
		#genre = audiofile.tag.genre.name.encode('utf-8')
		genre = audiofile.tag.genre.name
		return genre



	
from PIL import Image
import os.path
from config import spectrogramsPath, slicesPath


#Slices all spectrograms
def createSlicesFromSpectrograms(desiredSize, spectrogramsPath):
    subs = os.listdir(spectrogramsPath)
    subs = [sub for sub in subs if os.path.isdir(spectrogramsPath+sub)]
    for sub in subs:
        spectrogramsPathPerGenre = spectrogramsPath + sub + '/'
        for filename in os.listdir(spectrogramsPathPerGenre):
            if filename.endswith(".png"):
                sliceSpectrogram(spectrogramsPathPerGenre, filename,desiredSize)


#Creates slices from spectrogram
#TODO Improvement - Make sure we don't miss the end of the song
def sliceSpectrogram(spectrogramsPathPerGenre, filename, desiredSize):
	genre = filename.split("_")[0] 	#Ex. Dubstep_19.png

	# Load the full spectrogram
	img = Image.open(spectrogramsPathPerGenre+filename)

	#Compute approximate number of 128x128 samples
	width, height = img.size
	nbSamples = int(width/desiredSize)
    #print('********* nb of samples for song', filename, nbSamples)
	width - desiredSize

	#Create path if not existing
	slicePath = slicesPath+"{}/".format(genre);
	if not os.path.exists(os.path.dirname(slicePath)):
		try:
			os.makedirs(os.path.dirname(slicePath))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

	#For each sample
	for i in range(nbSamples):
		print("Creating slice: ", (i+1), "/", nbSamples, "for", filename)
		#Extract and save 128x128 sample
		startPixel = i*desiredSize
		imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
		imgTmp.save(slicesPath+"{}/{}_{}.png".format(genre,filename[:-4],i))


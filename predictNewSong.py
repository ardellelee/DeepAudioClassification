import hdfsTools
from config import HDFS_DATA_DIR
from config import uploadPath, pixelPerSecond, nbClasses, sliceSize
import os
from PIL import Image
#from random import shuffle
from subprocess import Popen, PIPE, STDOUT
from audioFilesTools import isMono
from imageFilesTools import getImageData
from model import createModel
import numpy as np
import pandas as pd
import operator
import json
import time


desiredSize = 128  # size of slice png
newSongSpectrogramPath = uploadPath+'spectrogram/'
newSongSlicesPath = uploadPath+'slices/'


# Load new song name
songList = os.listdir(uploadPath)
songList = [song for song in songList if song.endswith(".mp3")]
nbFiles = len(songList)

# Create sprctrogram song by song
for index, filename in enumerate(songList):
    print("Creating spectrogram for file {}/{}...".format(index + 1, nbFiles))
    newFilename = "NewSong_" + str(index)
    print('************* newFilename: ', newFilename)

    # Create temporary mono track if needed
    if isMono(uploadPath+filename):
        command = "cp '{}' '/tmp/{}.mp3'".format(uploadPath+filename, newFilename)
        print('************* isMono, command: ', command)
    else:
        command = "sox '{}' '/tmp/{}.mp3' remix 1,2".format(uploadPath+filename, newFilename)
        print('************* not Mono, command: ', command)
    currentPath = os.path.dirname(os.path.realpath(__file__))
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False, cwd=currentPath)
    output, errors = p.communicate()
    if errors:
        print(errors)

    # Create spectrogram path if not existing
    if not os.path.exists(os.path.dirname(newSongSpectrogramPath)):
        try:
            os.makedirs(os.path.dirname(newSongSpectrogramPath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Create spectrogram
    filename.replace(".mp3", "")
    command = "sox '/tmp/{}.mp3' -n spectrogram -Y 200 -X {} -m -r -o '{}.png'".format(newFilename, pixelPerSecond,
                                                                                       newSongSpectrogramPath + '/' + newFilename)
    print('************* create spectrogram, command: ', command)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
    output, errors = p.communicate()
    if errors:
        print(errors)
    print('************ spectrogram created!')

    # Remove tmp mono track
    os.remove("/tmp/{}.mp3".format(newFilename))


# Slice
for filename in os.listdir(newSongSpectrogramPath):
    if filename.endswith(".png"):
        img = Image.open(newSongSpectrogramPath + filename)  # Load the full spectrogram
        width, height = img.size
        nbSamples = int(width / desiredSize)
        width - desiredSize

        # Create path if not existing
        if not os.path.exists(os.path.dirname(newSongSlicesPath)):
            try:
                os.makedirs(os.path.dirname(newSongSlicesPath))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        for i in range(nbSamples):
            print("Creating slice: ", (i + 1), "/", nbSamples, "for", filename)
            startPixel = i * desiredSize
            imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
            imgTmp.save(newSongSlicesPath + "{}_{}.png".format(filename[:-4], i))

# Prepare data
slices = os.listdir(newSongSlicesPath)
print('*********** slice filenames: ', len(slices))
slices = [filename for filename in slices if filename.endswith('.png')]
#shuffle(slices)

data = []
for filename in slices:
    imgData = getImageData(newSongSlicesPath+"/"+filename, sliceSize)
    data.append(imgData)
#shuffle(data)
X = np.array(data).reshape([-1, sliceSize, sliceSize, 1])
print(X.shape)

# Load model to predict
model = createModel(nbClasses, sliceSize)
model.load('model/musicDNN.tflearn')
y_preds = model.predict(X)

genre_list = ['blues', 'country', 'electronic', 'folk', 'hip-hop', 'indie', 'jazz', 'pop', 'rock', 'soul']
df = pd.DataFrame(y_preds, columns=genre_list)

tags = {}
for i in range(10):
    tags[genre_list[i]] = 100*float(df.iloc[:,i].mean())
print(tags)
newSongGenre = max(tags.items(), key=operator.itemgetter(1))[0]
print('newSongGenre:', newSongGenre)

# Save to json
timestamp = int(time.time())
newTrackID = 'NewSong-'+str(timestamp)

songInfo = {}
songInfo['tags']=tags
songInfo['genre']=newSongGenre
songInfo['track_ID']= newTrackID+'.mp3'
print(songInfo)

with open('data/Upload/'+newTrackID+'.json', 'w') as f:
    json.dump(songInfo, f)


# Upload json to HDFS
client_hdfs = hdfsTools()
mp3_file = uploadPath+newFilename
client_hdfs.writeHdfs(mp3_file, HDFS_DATA_DIR+mp3_file, "mp3")
client_hdfs.writeHdfs(jsonfile, HDFS_DATA_DIR+jsonfile, "json")
# -*- coding: utf-8 -*-
import random
import string
import os
import sys

# configuration
from config import slicesPath
from config import batchSize, sliceSize
from config import filesPerGenre
from config import nbEpoch
from config import validationRatio, testRatio
from config import rawDataPath

# data preprocessing
from songTagger import songTagger
from songToData_RDD import sparkrdd

# genre classification
from model import createModel
from datasetTools import getDataset


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="Trains or tests the CNN", nargs='+', choices=["train","test","slice","tag"])
args = parser.parse_args()

if "tag" in args.mode:
	songTagger(rawDataPath)
	sys.exit()

print("--------------------------")
print("| ** Config ** ")
print("| Validation ratio: {}".format(validationRatio))
print("| Test ratio: {}".format(testRatio))
print("| Slices per genre: {}".format(filesPerGenre))
print("| Slice size: {}".format(sliceSize))
print("--------------------------")

if "slice" in args.mode:
    sparkrdd = sparkrdd(master="local", appname="GenreClassifier")
    sparkrdd.createSpectrogramsFromAudio()
    sparkrdd.createSlicesFromSpectrograms()
    sys.exit()

#List genres
genres = os.listdir(slicesPath)
genres = [filename for filename in genres if os.path.isdir(slicesPath+filename)]
print('******** Slice Genres: ', genres)
nbClasses = len(genres)
print('******** nbClasses of slice genre: ', nbClasses)


#Create model
model = createModel(nbClasses, sliceSize)
#sys.exit()

if "train" in args.mode:
	#Create or load new dataset
	train_X, train_y, validation_X, validation_y = getDataset(filesPerGenre, genres, sliceSize, validationRatio, testRatio, mode="train")
	#Define run id for graphs
	run_id = "MusicGenres - "+str(batchSize)+" "+''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(10))

	#Train the model
	print("[+] Training the model...")
	model.fit(train_X, train_y, n_epoch=nbEpoch, batch_size=batchSize, shuffle=True, validation_set=(validation_X, validation_y), snapshot_step=100, show_metric=True, run_id=run_id)
	print("    Model trained! ✅")

	#Save trained model
	print("[+] Saving the weights...")
	model.save('model/musicDNN.tflearn')
	print("[+] Weights saved! ✅💾")


if "test" in args.mode:
	#Create or load new dataset
	test_X, test_y = getDataset(filesPerGenre, genres, sliceSize, validationRatio, testRatio, mode="test")

	#Load weights
	print("[+] Loading weights...")
	model.load('model/musicDNN.tflearn')
	print("    Weights loaded! ✅")

	testAccuracy = model.evaluate(test_X, test_y)[0]
	print("[+] Test accuracy: {} ".format(testAccuracy))






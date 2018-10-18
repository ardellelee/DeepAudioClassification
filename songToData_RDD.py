# -*- coding: utf-8 -*-
# configuration
from config import rawDataPath
from config import pixelPerSecond
from config import spectrogramsPath, slicesPath
from config import HDFS_PORT_NUMBER
from config import HDFS_DATA_DIR

# pyspark
from pyspark import SparkConf, SparkContext, sql

# hdfs
from hdfs import InsecureClient

from subprocess import Popen, PIPE, STDOUT
import os, os.path
from PIL import Image
import errno
from audioFilesTools import isMono, getGenre
from hdfsTools import hdfsTools

desiredSize = 128  # size of slice png

#Define
currentPath = os.path.dirname(os.path.realpath(__file__))

class sparkrdd:

    # constructor
    def __init__(self, master="local", appname="GenreClassifier"):
        self.sc = self.createSpark(master, appname)
        # self.sql = self.createSQL()
        self.client_hdfs = hdfsTools()


    def createSpark(self, master, appname):
        conf = (SparkConf()
            .setMaster(master)
            .setAppName(appname)
            .set("spark.executor.memory", "1g")
            )
        sc = SparkContext(conf=conf)
        return sc

    def createSQL(self):
        sqlct = sql.SQLContext(self.sc)
        return sqlct

    def connect2HDFS(self):
        return InsecureClient('http://localhost:' + HDFS_PORT_NUMBER)

    #Creates .png whole spectrograms from mp3 files
    def createSpectrogramsFromAudio(self):

        print("Creating spectrograms...")
        subs = os.listdir(rawDataPath)
        print('********* subs', subs)
        subs = [sub for sub in subs if os.path.isdir(rawDataPath+sub)]
        print('********* New subs', subs)

        self.subs = subs
        rdd = self.sc.parallelize(self.subs)
        rdd.map(self.aud2spec)
        rdd.collect()
        print("Spectrograms created!")
        return

    def aud2spec(self, sub):
        if sub != None:
            genresID = dict()
            files = []
            files = files + os.listdir(rawDataPath+sub)
            files = [file for file in files if file.endswith(".mp3")]
            print('******** Listing files for: ', sub)
            print(files)
            nbFiles = len(files)
            print('********* Number of mp3 files: ', nbFiles)

            #Create path if not existing
            spectrogramsPathPerGenre = spectrogramsPath+sub+'/'
            print('*********** spectrogramsPathPerGenre: ', spectrogramsPathPerGenre)
            if not os.path.exists(os.path.dirname(spectrogramsPathPerGenre)):
                try:
                    os.makedirs(os.path.dirname(spectrogramsPathPerGenre))
                    print('************ SpectrogramsPath created! ', spectrogramsPathPerGenre)
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            #Rename files according to genre
            for index,filename in enumerate(files):
                print("Creating spectrogram for file {}/{}...".format(index+1, nbFiles))
                fileGenre = str(getGenre(rawDataPath+sub+'/'+filename))
                print('************* file name:', filename)
                print('************* file genre:', fileGenre)
                print('************* genre type:', type(fileGenre))
                genresID[fileGenre] = genresID[fileGenre] + 1 if fileGenre in genresID else 1
                print('************* genresID: ', genresID)
                fileID = genresID[fileGenre]
                print('************* fileID: ', fileID)
                newFilename = str(fileGenre)+"_"+str(fileID)
                print('************* newFilename: ', newFilename)
                self.createSpectrogram(filename, sub, newFilename)
        return

    #Create spectrogram from mp3 files
    def createSpectrogram(self, filename, sub, newFilename):

        mp3_fullpath_name = rawDataPath+sub+'/'+filename
        #Create temporary mono track if needed
        if isMono(mp3_fullpath_name):
            command = "cp '{}' '/tmp/{}.mp3'".format(rawDataPath+sub+'/'+filename, newFilename)
            print('************* isMono, command: ', command)
        else:
            command = "sox '{}' '/tmp/{}.mp3' remix 1,2".format(rawDataPath+sub+'/'+filename, newFilename)
            print('************* not Mono, command: ', command)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
            print(errors)

        #Create spectrogram
        filename.replace(".mp3","")
        spectrogram_fullpath_name = spectrogramsPath+sub+'/'+newFilename
        command = "sox '/tmp/{}.mp3' -n spectrogram -Y 200 -X {} -m -r -o '{}.png'".\
                    format(newFilename, pixelPerSecond, spectrogram_fullpath_name)
        print('************* create spectrogram, command: ', command)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
            print(errors)
        print('************ spectrogram created!')
        #Remove tmp mono track
        os.remove("/tmp/{}.mp3".format(newFilename))

        #Store mp3 file to hdfs
        hdfs_fullpath_name = HDFS_DATA_DIR+rawDataPath+sub+'/'+filename
        self.client_hdfs.writeHdfs(mp3_fullpath_name, hdfs_fullpath_name, "mp3")
        return

    #Slices all spectrograms
    def createSlicesFromSpectrograms(self):
        print("Creating slices...")
        subs = os.listdir(spectrogramsPath)
        subs = [sub for sub in subs if os.path.isdir(spectrogramsPath+sub)]

        self.subs = subs
        rdd = self.sc.parallelize(self.subs)
        rdd.map(self.spec2slices)
        rdd.collect()
        print("Slices created!")
        return

    def spec2slices(self, sub):
        if sub != None:
            spectrogramsPathPerGenre = spectrogramsPath + sub + '/'
            for filename in os.listdir(spectrogramsPathPerGenre):
                if filename.endswith(".png"):
                    self.sliceSpectrogram(spectrogramsPathPerGenre, filename)
        return

    #Creates slices from spectrogram
    #TODO Improvement - Make sure we don't miss the end of the song
    def sliceSpectrogram(self, spectrogramsPathPerGenre, filename):
        genre = filename.split("_")[0]

        # Load the full spectrogram
        img = Image.open(spectrogramsPathPerGenre+filename)

        #Compute approximate number of 128x128 samples
        width, height = img.size
        nbSamples = int(width/desiredSize)
        #print('********* nb of samples for song', filename, nbSamples)
        #width - desiredSize

        #Create path if not existing
        slicePath = slicesPath+"{}/".format(genre)
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
            slice_fullpath_name = slicesPath + "{}/{}_{}.png".format(genre, filename[:-4], i)
            imgTmp.save(slice_fullpath_name)

            # Store slice file to hdfs
            hdfs_fullpath_name = HDFS_DATA_DIR+slicesPath+"{}/{}_{}.png".format(genre, filename[:-4], i)
            self.client_hdfs.writeHdfs(slice_fullpath_name, hdfs_fullpath_name, "png")
        return


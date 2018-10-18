# Song Genre Prediction

## Dependencies ##
Install the following tools before trying to run the code:

```
python-magic
eyed3
lame    (recommend to install by brew)
sox --with-lame (recommend to install by brew)
tensorflow
tflearn
pandas
numpy
```

## Project Structure ##
```
├───data               
│   ├───Raw        		<- mp3 audios for training
│   ├───Spectrogram     <- spectrograms generated from audio
│   ├───Slices     		<- slice of spectrogram
│   ├───dataset			<- pickled data for model training and validation
│   ├───Upload			<- the song uploaded by user	
├───model               <- trained model, can be loaded for prediction
├───README.md           <- a brief user mannual    
├───audioFilesTools.py                 
├───config.py			<- editable parameters 
├───datasetTools.py
├───hdfsTools.py
├───imageFilesTools.py
├───main_rdd.py         <- Train and test a classification model with provided arguments(tag/slice/train/test)				
├───model.py
├───predictNewSong.py	<- predict the genre of new song in data/Upload 
├───sliceSpectrogram.py
├───songTagger_RDD.py   <- provide functions for creating spectrograms and slices
├───testHdfs.py
```


## Use Cases


### UC1: Predict the genre of a new song
- Place the new song user uploaded in data/Upload

To predict the genre of new song:
```
python predictNewSong.py
```

### UC2: Train a model from scratch
- Create folder data/Raw/ if not exist
- Place the .mp3 files by label in data/Raw/ , like

```
data/Raw/pop/xxxxx.mp3
data/Raw/country/xxxxxxxx.mp3
```
(the genre for each song is provided and can be queried in MSD dataset)


To add genre tags into mp3 songs(in case the genre is not in built-in metadata):

```
python main_rdd.py tag
```


To create the song slices (might take long time):

```
python main_rdd.py slice
```

To train the classifier (also takes long time):

```
python main_rdd.py train
```

To test the classifier (fast):

```
python main_rdd.py test
```

- Most editable parameters are in the `config.py` 
- The model architecture can be changed in the `model.py` 
- With default hyper-parameters in `config.py`, model converges with 0.731 accuracy
- More details about training in `training.log` and `test.log`


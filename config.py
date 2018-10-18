#Define paths for files
rawDataPath = "data/Raw/"
spectrogramsPath = "data/Spectrograms/"
slicesPath = "data/Slices/"
datasetPath = "data/dataset/"
uploadPath = "data/Upload/"

#Spectrogram resolution
pixelPerSecond = 50

#Slice parameters
sliceSize = 128

#dataset parameters
filesPerGenre = 1000
validationRatio = 0.3
testRatio = 0.1

#Model parameters
batchSize = 128
learningRate = 0.001
nbEpoch = 20
nbClasses = 10



# HDFS parameters
#HDFS_HOST = "192.168.56.102"
HDFS_HOST = "quickstart.cloudera"    # must configure this in C:\Windows\System32\drivers\etc\hosts or /etc/hosts
HDFS_PORT_NUMBER = 50070
HDFS_DATA_DIR = "/user/cloudera/"
HDFS_USER = "cloudera"

# Testing
# curl -i "http://192.168.56.102:50070/webhdfs/v1/user/cloudera/data?op=LISTSTATUS"

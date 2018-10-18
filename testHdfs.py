from hdfsTools import hdfsTools
from config import HDFS_DATA_DIR, rawDataPath, slicesPath

txt_file = 'README.md'
mp3_file = 'TRAADNA128F9331246.mp3'
img_file = 'Blues_1_0.png'
client_hdfs = hdfsTools()

# Store txt file to hdfs
txt_fullpath_name = txt_file
hdfs_fullpath_name = HDFS_DATA_DIR + txt_fullpath_name
client_hdfs.writeHdfs(txt_fullpath_name, hdfs_fullpath_name, "txt")

# Store mp3 file to hdfs
mp3_fullpath_name = rawDataPath + "blues" + '/' + mp3_file
hdfs_fullpath_name = HDFS_DATA_DIR + mp3_fullpath_name
client_hdfs.writeHdfs(mp3_fullpath_name, hdfs_fullpath_name, "mp3")

# Store img file to hdfs
img_fullpath_name = slicesPath + "blues" + '/' + img_file
hdfs_fullpath_name = HDFS_DATA_DIR + img_fullpath_name
client_hdfs.writeHdfs(img_fullpath_name, hdfs_fullpath_name, "png")

###################################################################

# Get txt file from hdfs
txt_fullpath_name = txt_file
hdfs_fullpath_name = HDFS_DATA_DIR + txt_fullpath_name
content = client_hdfs.readHdfs(hdfs_fullpath_name, "txt")
file = open(txt_fullpath_name, 'wb')
file.write(content)
file.close()

# Get mp3 file from hdfs
mp3_fullpath_name = rawDataPath + "blues" + '/' + mp3_file
hdfs_fullpath_name = HDFS_DATA_DIR + mp3_fullpath_name
content = client_hdfs.readHdfs(hdfs_fullpath_name, "mp3")
file = open(mp3_fullpath_name, 'wb')
file.write(content)
file.close()

# Get img file from hdfs
img_fullpath_name = slicesPath + "blues" + '/' + img_file
hdfs_fullpath_name = HDFS_DATA_DIR + img_fullpath_name
content = client_hdfs.readHdfs(hdfs_fullpath_name, "img")
file = open(img_fullpath_name, 'wb')
file.write(content)
file.close()


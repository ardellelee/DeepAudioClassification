# -*- coding: utf-8 -*-
# configuration
from config import HDFS_HOST, HDFS_PORT_NUMBER, HDFS_USER, HDFS_DATA_DIR, rawDataPath

# hdfs
from hdfs import InsecureClient
from PIL import Image
import io
import json

class hdfsTools:

    # constructor
    def __init__(self):
        self.client_hdfs = InsecureClient('http://' + HDFS_HOST + ':' + str(HDFS_PORT_NUMBER), user=HDFS_USER)
        print(self.client_hdfs.list(HDFS_DATA_DIR + rawDataPath))  # for testing
        return

    # Writing file to hdfs
    def writeHdfs(self, src_fullpath_name, dest_fullpath_name, file_type):
        # image files
        if file_type == "png" or file_type == "jpg":
            buf = io.BytesIO()
            img = Image.open(src_fullpath_name)
            img.save(buf, file_type)
            buf.seek(0)
            with self.client_hdfs.write(dest_fullpath_name, overwrite=True) as writer:
                writer.write(buf.getvalue())
            buf.close()

        # json file
        elif file_type == "json":
            with self.client_hdfs.write(dest_fullpath_name, encoding='utf-8', overwrite=True) as writer:
                json.dump(src_fullpath_name, writer)

        # txt file
        elif file_type == "txt" or file_type == "csv":
            with open(src_fullpath_name) as reader, self.client_hdfs.write(dest_fullpath_name, encoding='utf-8', overwrite=True) as writer:
                writer.write(reader.read())

        # default as binary file (eg. mp3)
        else:
            with open(src_fullpath_name, 'rb') as reader:
                r = reader.read()
            self.client_hdfs.write(dest_fullpath_name, data=r, overwrite=True)
        return

    #Read file from hdfs
    def readHdfs(self, hdfs_fullpath_name, file_type):

        # json file
        if file_type == "json":
            with self.client_hdfs.read(hdfs_fullpath_name) as reader:
                content = json.load(reader)
            #print(content.decode())  # for testing

        # txt file
        elif file_type == "txt" or file_type == "csv":
            with self.client_hdfs.read(hdfs_fullpath_name) as reader:
                content = reader.read()
            #print(content.decode())  # for testing

        # image file
        elif file_type == "png" or file_type == "jpg":
            with self.client_hdfs.read(hdfs_fullpath_name) as reader:
                content = reader.read()

        # default as binary file (eg. mp3)
        else:
            with self.client_hdfs.read(hdfs_fullpath_name) as reader:
                content = reader.read()

        return content

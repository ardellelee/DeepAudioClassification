import eyed3
import os


def songTagger(rawDataPath):
    # List all songs and their directory
    genres = []
    for root, sub, files in os.walk(rawDataPath):
        #print(sub)
        genres = genres+sub
    print(genres)

    # Add tags
    for g in genres:
        songs = os.listdir(rawDataPath+g)
        songs = [s for s in songs if s.endswith('.mp3')]
        print(songs)
        for s in songs:
            print('*************** Tagging for song: ', s, 'genre: ', g)
            f = eyed3.load(rawDataPath + g + '/' + s)
            f.tag.genre = g
            f.tag.save()

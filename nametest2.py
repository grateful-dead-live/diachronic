from archive_py3 import get_all_song_names, read_json, SONG_MAP2
import sys
from fuzzywuzzy import fuzz

SONG_NAME = sys.argv[1].lower()
SONG_JSON = read_json(SONG_MAP2)
#FRATIO = float(sys.argv[2].lower())
FRATIO = 69

#___________________________________________________________________________________

def get_song_occurrence(songname):
    return len([t for t in SONG_JSON[songname]])
#___________________________________________________________________________________

def print_results(songlist):
    tablen = max([len(s[1]) for s in songlist])
    print("{0}{1}{2}".format("name", (tablen - 1) * " ", "count"))
    print((tablen + 8) * "-")
    for i in sorted(songlist, reverse = True):
        spaces = tablen - len(i[1]) + 1
        print('"{0}"{1}{2}'.format(i[1], spaces * " ", i[0]))
    print("")
#___________________________________________________________________________________

def name_test1(song_names):
    songcount = [[get_song_occurrence(song), song] for song in song_names if SONG_NAME.replace(" ", "") in song.replace(" ", "")]
    print_results(songcount)
#___________________________________________________________________________________

def name_test2(song_names):
    songcount = [[get_song_occurrence(song), song] for song in song_names if fuzz.partial_ratio(SONG_NAME, song) > FRATIO]
    print_results(songcount)
#___________________________________________________________________________________

def name_test3(song_names):
    songcount = []
    words = SONG_NAME.replace("  ", " ").split(" ")
    for song in song_names:
        c = 0
        for word in words:
            if fuzz.partial_ratio(word, song.replace("  ", " ")) > FRATIO:
                c += 1
        if c > 0.5 * len(words):
            songcount.append([get_song_occurrence(song), song])
    print_results(songcount)
#___________________________________________________________________________________

def name_test4(song_names):
    songcount = []
    song_name_words = SONG_NAME.replace("  ", " ").split(" ")
    for song in song_names:
        song_words = song.strip().replace("  ", " ").split(" ")
        c = 0
        for word in song_name_words:
            if fuzz.partial_ratio(word, song.replace("  ", " ")) > FRATIO:
                c += 1
        if c > 0.5 * len(song_name_words) and len(song_words) <= len(song_name_words):
            songcount.append([get_song_occurrence(song), song])
    print_results(songcount)

#___________________________________________________________________________________

def name_test5(song_names):
    songcount = [[get_song_occurrence(song), song] for song in song_names if fuzz.ratio(SONG_NAME, song) > FRATIO]
    print_results(songcount)

#___________________________________________________________________________________

def name_test6(song_names):
    songcount = []
    song_name_words = SONG_NAME.replace("  ", " ").split(" ")
    for song in song_names:
        _song = song.strip().replace("  ", " ")
        song_words = _song.split(" ")
        if fuzz.ratio(SONG_NAME, song) > FRATIO and len(song_words) <= len(song_name_words):  
            songcount.append([get_song_occurrence(song), song])

    print_results(songcount)


#___________________________________________________________________________________


#    songs = ["playing in the band", "not fade away", "me and my uncle", "sugar magnolia", "the other one", "i know you rider", "china cat sunflower", "truckin", "jack straw", "good lovin"]

print('\n"{0}"'.format(SONG_NAME))
#name_test1(get_all_song_names())
#name_test2(get_all_song_names())
#name_test3(get_all_song_names())
#name_test4(get_all_song_names())
#name_test5(get_all_song_names())
name_test6(get_all_song_names())
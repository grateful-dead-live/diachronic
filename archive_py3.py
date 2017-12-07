import os, json, pickle, random
from collections import defaultdict, Counter
import internetarchive as ia
from fuzzywuzzy import fuzz
#from pprint import pprint

AUDIO_DIRS = '../../thomasw/grateful_dead/lma_soundboards/sbd/'
SBD_ITEMS = 'data/sbd_items.json'
SONG_MAP = 'data/song_map.json'
SONG_MAP2 = 'data/song_map2.json'
SONG_LIST_IDS = 'data/song_list_ids.json'
TOP_SONG_MAP = 'data/top_song_map.json'
TOP_SONG_MAP2 = 'data/top_song_map2.json'

def read_json(file):
    with open(file, 'r') as lfile:
        return json.load(lfile)

def write_json(content, file):
    with open(file, 'w') as wfile:
        json.dump(content, wfile)

def save_items():
    subdirs = [d for d in next(os.walk(AUDIO_DIRS))[1]]
    num_subdirs = len(subdirs)
    items = {}
    for i, id in enumerate(subdirs):
        print(str(i)+'/'+str(num_subdirs), id)
        item = ia.get_item(id)
        items[id] = {}
        items[id]['metadata'] = item.metadata
        items[id]['files'] = item.files
    write_json(items, SBD_ITEMS)

def get_tracks(item):
    return filter(lambda i: 'track' in i and '.mp3' in i['name'], item['files'])

def create_song_map():
    json = read_json(SBD_ITEMS)
    tracks = {s:get_tracks(i) for s, i in json.items()}
    metadata = {s:i['metadata'] for s, i in json.items()}
    song_map = {}
    for recording, ts in tracks.items():
        for track in ts:
            if 'title' in track:
                if track['title'] not in song_map:
                    song_map[track['title']] = []
                version = {}
                version['recording'] = recording
                version['track'] = track['name']
                version['year'] = metadata[recording]['year']
                if isinstance(version['year'], list):
                    version['year'] = version['year'][0]
                song_map[track['title']].append(version)
    write_json(song_map, SONG_MAP)

def simplify_song_map():
    song_map = read_json(SONG_MAP)
    song_map2 = defaultdict(list)
    for song_name, versions in song_map.items():
        simple_name = ''.join([c for c in song_name if c.isalpha() or c == ' '])
        simple_name = simple_name.lower()
        song_map2[simple_name].extend(versions)
    write_json(song_map2, SONG_MAP2)


def get_song_versions_by_year(songname):
    versions = read_json(SONG_MAP2)[songname]
    by_year = defaultdict(list)
    for track in versions:
        by_year[track['year']].append({i:track[i] for i in track if i!='year'})
    return by_year

def get_all_song_names():
    return list(read_json(SONG_MAP2).keys())

def get_shows_by_year():
    #TODO
    return

def check_file(version, sbd_items):
    # check if "matrix" is not in metadata and file exists locally
    if "matrix" in sbd_items[version["recording"]]["metadata"]["subject"].lower():
        return False
    else:
        return os.path.isfile(os.path.join(AUDIO_DIRS, version["recording"], version["track"]))

def create_top_song_map():
    top_songs = ["playing in the band", "not fade away", "me and my uncle", "sugar magnolia", "the other one", "i know you rider", "china cat sunflower", "truckin", "jack straw", "good lovin", "mexicali blues", "tennessee jed", "the promised land", "big river", "estimated prophet", "el paso", "eyes of the world", "sugaree"]
    f_ratio = 69
    song_map = read_json(SONG_MAP)
    sbd_items = read_json(SBD_ITEMS)
    top_song_map = defaultdict(list)
    for original_song_name in top_songs:
        #print(original_song_name)
        original_song_name_wordcount = len(original_song_name.split())
        for song_name, versions in song_map.items():
            simple_name = ''.join([c for c in song_name if c.isalpha() or c == ' '])
            simple_name = simple_name.lower().strip().replace("  ", " ")
            simple_name_wordcount = len(simple_name.split())
            if fuzz.ratio(original_song_name, simple_name) > f_ratio and simple_name_wordcount <= original_song_name_wordcount:  
                new_versions = [v for v in versions if check_file(v, sbd_items)]
                top_song_map[original_song_name].extend(new_versions)
        #print(len(top_song_map[original_song_name]))
    #write_json(top_song_map, TOP_SONG_MAP)
    filter_one_recording_per_date(top_song_map, sbd_items)

def filter_one_recording_per_date(top_song_map, sbd_items):
    #top_song_map = read_json(TOP_SONG_MAP)
    #sbd_items = read_json(SBD_ITEMS)
    top_song_map2 = defaultdict(list)
    for song_name, versions in top_song_map.items():
        versiondict = defaultdict(list)
        datelist = []
        for version in versions:
            recording = version["recording"]
            date = sbd_items[recording]["metadata"]["date"]
            versiondict[date].append(version)
            datelist.append(date)
        datecount = dict(Counter(datelist))
        for date, dcount in datecount.items():
            if dcount > 1:
                # if song was played more than once at a concert, only consider those having most of them
                recording_count = flip_dict(dict(Counter([i["recording"] for i in versiondict[date]])))
                choice_list = recording_count[max(recording_count)]
                date_version_recording = random.choice(choice_list)
                for version in versiondict[date]:
                    if version["recording"] == date_version_recording:
                        top_song_map2[song_name].append(version)
            else:
                top_song_map2[song_name].append(versiondict[date][0])
        print(song_name, len(top_song_map2[song_name]))
    write_json(top_song_map2, TOP_SONG_MAP2)

def flip_dict(d):
    reversed_dict = defaultdict(list)
    for key,value in d.items():
        reversed_dict[value].append(key)
    return reversed_dict

create_top_song_map()
#filter_one_recording_per_date()


#save_items()
#create_song_map()
#simplify_song_map()
#print(get_song_versions_by_year(get_all_song_names()[5]))
#print(get_song_versions_by_year('Sugar Magnolia'))
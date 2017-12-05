import os, json
from collections import defaultdict
import internetarchive as ia
from fuzzywuzzy import fuzz

AUDIO_DIRS = '../../thomasw/grateful_dead/lma_soundboards/sbd/'
SBD_ITEMS = 'data/sbd_items.json'
SONG_MAP = 'data/song_map.json'
SONG_MAP2 = 'data/song_map2.json'
SONG_LIST_IDS = 'data/song_list_ids.json'

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

def get_named_songs(song_name):
    f_ratio = 69
    song_names = get_all_song_names()
    named_songs = []
    song_name_words = song_name.replace("  ", " ").split(" ")
    for song in song_names:
        _song = song.strip().replace("  ", " ")
        song_words = _song.split(" ")
        if fuzz.ratio(song_name, song) > f_ratio and len(song_words) <= len(song_name_words):  
            named_songs.append(song)
    return named_songs

def get_list_of_song_ids(song_name):
    song_name_list = get_named_songs(song_name)
    sbd_items = read_json(SBD_ITEMS)
    song_map2 = read_json(SONG_MAP2)
    results_dict = {}
    for s in song_name_list:
        versions = song_map2[s]
        for v in versions:
            if "matrix" not in sbd_items[v["recording"]]["metadata"]["subject"].lower():
                vdate = sbd_items[v["recording"]]["metadata"]["date"]
                if vdate not in results_dict:
                    results_dict[vdate] = [v]
                else:
                    results_dict[vdate].append(v)

    # if duplicate, take only best rated

    new_results = {}
    c = 0
    for k, v in results_dict.items():
        if len(v) > 1:
            max_rating = 0
            new_results[k] = v[0]
            for i in v:
                id = i["recording"]
                item = ia.get_item(id)
                ratings_sum = float(0)
                for review in item.reviews:
                    ratings_sum += float(review["stars"])
                if len(item.reviews) > 0:
                    avg_rating = ratings_sum / len(item.reviews)
                    print(id, avg_rating)
                    if avg_rating > max_rating: 
                        max_rating = avg_rating
                        new_results[k] = i 
                else:
                    avg_rating = 0
                    print(id, "no rating")
            print(new_results[k]["recording"])
            print("")

                   
        else:
             new_results[k] = i

    write_json(new_results, SONG_LIST_IDS)






    
  



        





#save_items()
#create_song_map()
#simplify_song_map()
#print(get_song_versions_by_year(get_all_song_names()[5]))
#print(get_song_versions_by_year('Sugar Magnolia'))
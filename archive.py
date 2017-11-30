import os, json
from collections import defaultdict
import internetarchive as ia

AUDIO_DIRS = '../../thomasw/grateful_dead/lma_soundboards/sbd/'
SBD_ITEMS = 'data/sbd_items.json'
SONG_MAP = 'data/song_map.json'
SONG_MAP2 = 'data/song_map2.json'

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
        print str(i)+'/'+str(num_subdirs), id
        item = ia.get_item(id)
        items[id] = {}
        items[id]['metadata'] = item.metadata
        items[id]['files'] = item.files
    write_json(items, SBD_ITEMS)

def get_tracks(item):
    return filter(lambda i: 'track' in i and '.mp3' in i['name'], item['files'])

def create_song_map():
    json = read_json(SBD_ITEMS)
    tracks = {s:get_tracks(i) for s, i in json.iteritems()}
    metadata = {s:i['metadata'] for s, i in json.iteritems()}
    song_map = {}
    for recording, ts in tracks.iteritems():
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
    for song_name, versions in song_map.iteritems():
        print song_name
        simple_name = ''.join([c for c in song_name if c.isalpha() or c == ' '])
        simple_name = simple_name.lower()
        song_map2[simple_name].append(versions)
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

#save_items()
#create_song_map()
simplify_song_map()
#print get_song_versions_by_year(get_all_song_names()[5])
#print get_song_versions_by_year('Sugar Magnolia')
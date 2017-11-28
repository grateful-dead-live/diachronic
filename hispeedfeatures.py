import numpy as np

def list_features():
    return []

def xsdDurationToFloat(duration):
    return float(duration.split('"')[1].replace('PT', '').replace('S', ''))

def load_values(string):
    dims = string.split('af:dimensions')[1].split('"')[1].split()
    dims = map(int, dims)
    values = string.split('af:value')[1].replace('"', '').split()[:-1]
    values = map(float, values)
    return np.array(values).reshape((-1, dims[0]))

def load_events(string):
    times = map(lambda s: s.split(';')[0], string.split('tl:at')[1:])
    return np.array(sorted(map(xsdDurationToFloat, times)))

def load_feature(file):
    with open(file) as f:
        content = f.read()
    values = 'af:value' in content
    return load_values(content) if values else load_events(content)
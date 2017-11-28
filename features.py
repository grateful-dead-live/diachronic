import numpy as np
from rdflib import Graph, Namespace, RDF

AF = Namespace('http://purl.org/ontology/af/')
TIMELINE = Namespace('http://purl.org/NET/c4dm/timeline.owl#')

def list_features():
    return []

def xsdDurationToPython(duration):
    return float(duration.toPython().replace('PT', '').replace('S', ''))

def load_signal_feature(graph):
    dims = list(graph.objects(None, AF.dimensions))[0].split()
    dims = map(int, dims)
    values = list(graph.objects(None, AF.value))[0].split()
    values = map(float, values)
    return np.array(values).reshape((-1, dims[0]))

def load_event_feature(graph):
    times = [time for time in graph.objects(None, TIMELINE.at)]
    return np.array(sorted(map(xsdDurationToPython, times)))

def load_feature(file):
    g = Graph()
    g.load(file, format='n3')
    is_signal = len(list(g.subjects(AF.value))) > 0
    return load_signal_feature(g) if is_signal else load_event_feature(g)
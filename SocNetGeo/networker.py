import networkx as nx
import json as js
import os
import matplotlib.pyplot as plt
import math
import twatter
import itertools
import tweepy as twp
import time

## Class representing a network of known users in search area
class SNetwork:
    
	## Initializes a new SNetwork
    def __init__(self):
        self.G = nx.DiGraph()
	
	## Initializes a SNetwork with an existing network
	## G: existing network
    def __init__(self, G):
        self.G = G
    
	## Adds a new user to the network
	## usr: new user
    def add_user(self, usr):
        self.G.add_node(usr)
    
    ## Adds a follower & following relationship to the network
    def add_friendship(self, usr1, usr2):
        self.G.add_edge(usr1, usr2)
        self.G.add_edge(usr2, usr1)
    
    ## Adds a usr1 follows usr2 relationship to the network
    def add_friend(self, usr1, usr2):
        self.G.add_edge(usr1, usr2)
    
    ## Adds a usr2 follows usr1 relationship to the network
    def add_follower(self, user1, usr2):
        self.G.add_edge(usr2, usr1)  
    
	## Exports graph to file in three formats: adjacency matrix, multiadjaceny
	## matrix and edge list
	## fileBase: name of file
    def export_graph(self, fileBase):
        nx.write_adjlist(self.G, fileBase + '-adjmat.txt')
        nx.write_multiline_adjlist(self.G, fileBase + '-multiadjmat.txt')
        nx.write_edgelist(self.G, fileBase + '-edglst.txt')
    
	## Draw graph and save as dot archive
    def draw_graph(self):
        # write dot file to use with graphviz
        # run "dot -Tpng g.dot >g.png"
        nx.write_dot(self.G,'g.dot')
        nx.draw_circular(self.G)
        plt.savefig('path.png')

## Matches coordinates given to specific locations, including aliases.
## List of locations obtained from "Carmen: A twitter geolocation system with applications to public health."
## available at https://github.com/mdredze/carmen
def locationBuilder(locsFile, coords):
    locations = []
    with open(locsFile, 'r') as locs:
        for loc in locs.readlines():
            l = js.loads(loc)
            try:
                long1 = math.radians(float(l['longitude']))
                lat1 = math.radians(float(l['latitude']))
            except KeyError:
                continue
            long2 =  math.radians(coords['longitude'])
            lat2 = math.radians(coords['latitude'])
            distance = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(long1 - long2)) * 6371
            if distance <= coords['radius']:
                if l['city'] is not '':
                    locations.append(l['city'])
                if l['state'] is not '':
                    locations.append(l['state'])
                if l['aliases'] is not []:
                    locations += l['aliases']
    return locations

## Builds network from mined Twitter data
def buildBaseNetwork(networkName):
    friendDir = './data/friends/'
    SN = SNetwork()
    users = []
    locations =  locationBuilder('./resources/locations.json', {'latitude': 19.4326, 'longitude': -99.1332, 'radius': 30})
    print locations
    for (dirpath, dirnames, filenames) in os.walk(friendDir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext == '.txt':
                users.append(name)
    for (dirpath, dirnames, filenames) in os.walk(friendDir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext == '.txt':
                SN.add_user(name)
                with open(os.path.join(dirpath, filename)) as f:
                    print os.path.join(dirpath, filename)
                    for line in f.readlines():
                        friend = js.loads(line)
                        location = friend['location']
                        if friend['id'] in users or location in locations:
                            SN.add_friend(name, friend['id'])
    SN.export_graph(networkName)

## Completes network by finding relationships (follower, followed by)
## between known users
def completeNetwork(SN, networkName):
    twat = twatter.Twatter('user')
    for pair in itertools.combinations(SN.G.nodes(),2):
        print pair[0], pair[1]
        if not (SN.G.has_edge(pair[0],pair[1]) and SN.G.has_edge(pair[1],pair[0])):
            try:
                following, followedBy = twat.checkFriendship(pair[0],pair[1])
                print following, followedBy
            except twp.RateLimitError:
                SN.export_graph(networkName)
                print "Sleeping"
                time.sleep(15*60)
                following, followedBy = twat.checkFriendship(pair[0],pair[1])
            if following:
                SN.G.add_edge(pair[1],pair[0])
            if followedBy:
                SN.G.add_edge(pair[0],pair[1])
    SN.export_graph(networkName)


SN = buildBaseNetwork('./data/Mex')
completeNetwork(SN, './data/Mex')
print SN.G.number_of_edges()
print SN.G.number_of_nodes()
SN.draw_graph()

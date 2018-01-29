
# coding: utf-8
# @author: Gabriel Delgado
# Deezer technical exercise

import pandas as pd
import numpy as np
import matplotlib as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster


path = "C:/Users/Gabriel/Desktop/Deezer/hetrec2011-lastfm-2k/"

# Load files
artists = pd.read_csv(path+"artists.dat",sep="\t")
tags = pd.read_csv(path+"tags.dat",sep="\t")
user_artists = pd.read_csv(path+"user_artists.dat",sep="\t")
user_friends = pd.read_csv(path+"user_friends.dat",sep="\t")
user_taggedartists = pd.read_csv(path+"user_taggedartists.dat",sep="\t")
user_taggedartists_ts = pd.read_csv(path+"user_taggedartists-timestamps.dat",sep="\t")


# Define frequency data frame artistID vs tagID
CrossTab_artistsID_tagID = pd.crosstab(user_taggedartists['artistID'], user_taggedartists['tagID'])


# Definition of more populat tags (i.e. those mentioned more than once)
keys_tags = CrossTab_artistsID_tagID.keys()
keys_tags_pop = [] # popular tags
for tags_val in keys_tags:
    if(CrossTab_artistsID_tagID[tags_val].max()>1):
        keys_tags_pop.append(tags_val)

# Selecting the top 3 listened artists by user		
nrow = 0
userID_old = 2
ranking = 0
Top = []
while nrow<len(user_artists.index):
    userID_new = user_artists['userID'][nrow]
    if userID_new == userID_old:
        ranking+=1
    else:
        ranking = 1
        userID_old = userID_new
    Top.append(ranking)    
    nrow+=1

user_artists_top = user_artists
user_artists_top['Top'] = pd.Series(Top, index=user_artists.index)
user_artists_top3 = user_artists_top[user_artists_top['Top']<=3]

# Defining the data frame userID vs tagID according to CrossTab_artistsID_tagID
dfMatrix = np.zeros([len(set(user_artists_top3['userID'])),len(CrossTab_artistsID_tagID.keys())])
indexM = 0
for user in set(user_artists_top3['userID']): 
    ll = user_artists_top3[user_artists_top3['userID']==user]['artistID']
    dfMatrix[indexM,:] = np.asarray(CrossTab_artistsID_tagID.loc[ll].sum(axis=0)>0)
    indexM+=1

df = pd.DataFrame(dfMatrix, index=set(user_artists_top3['userID']), columns=CrossTab_artistsID_tagID.keys())
df.index.name = 'userID'		
		
#################################################
# First distance matrix proposal and clustering analysis
DistanceMatrix = np.zeros([len(keys_tags_pop),len(keys_tags_pop)])

for i in range(0,len(keys_tags_pop)):
    for j in range (0,len(keys_tags_pop)):
        if(j<i):
            tag1 = keys_tags_pop[i]
            tag2 = keys_tags_pop[j]
            Count= np.asarray((CrossTab_artistsID_tagID[tag1]>0) & (CrossTab_artistsID_tagID[tag2]>0))
            sm = Count.sum()
            DistanceMatrix[i,j] = np.exp(-sm)                

DistanceMatrix_sym = (DistanceMatrix.T+DistanceMatrix)

Z = linkage(DistanceMatrix_sym, 'ward')
max_d = 50 

plt.figure()
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Tags ID')
plt.ylabel('Distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
    labels = keys_tags_pop,
    color_threshold = max_d,
)
plt.savefig("Dendrogram_1.png",bbox_inches='tight')
plt.show()

clusters = fcluster(Z, max_d, criterion='distance')

#Interpretation
Profile = {}
for color in list(set(clusters)):
    L = []
    for index in range(len(keys_tags_pop)):
        if clusters[index] == color:
            L.append(keys_tags_pop[index])        
    Profile[color] = L

for name in Profile[1]:
    print(np.asarray(tags[tags['tagID']==name]['tagValue'])[0])
#################################################
# Second distance matrix proposal and clustering analysis

DistanceMatrix = np.zeros([len(keys_tags_pop),len(keys_tags_pop)])

for i in range(0,len(keys_tags_pop)):
    for j in range (0,len(keys_tags_pop)):
        if(j<i):
            tag1 = keys_tags_pop[i]
            tag2 = keys_tags_pop[j]
            Count = np.asarray((df[tag1]>0) & (df[tag2]>0))
            sm = Count.sum()
            DistanceMatrix[i,j] = np.exp(-0.1*sm)    


DistanceMatrix_sym = (DistanceMatrix.T+DistanceMatrix)

Z = linkage(DistanceMatrix_sym, 'ward')
max_d = 50 

plt.figure()
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Tags ID')
plt.ylabel('Distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
    labels = keys_tags_pop,
    color_threshold = max_d,
)
plt.savefig("Dendrogram_2.png",bbox_inches='tight')
plt.show()

clusters = fcluster(Z, max_d, criterion='distance')

#Interpretation
Profile = {}
for color in list(set(clusters)):
    L = []
    for index in range(len(keys_tags_pop)):
        if clusters[index] == color:
            L.append(keys_tags_pop[index])        
    Profile[color] = L

for name in Profile[1]:
    print(np.asarray(tags[tags['tagID']==name]['tagValue'])[0])
#################################################
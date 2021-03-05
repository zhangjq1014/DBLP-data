from lxml import etree
from datetime import datetime
import csv
import codecs
import ujson
import re
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from itertools import combinations

def main():
    
    ccf = open('proceedings.csv', 'r')
    author_conf_dict = {}
    G = nx.Graph()

    ccf.readline()
    while True:
        crf = ccf.readline()
        if len(crf) == 0:
            break
        i = crf.split(',')
        if len(i) != 5:
            print (i)
            input()

        title = i[0].strip()
        author_list = i[1].strip().split('::')
        year = i[2]
        acronym = i[4].strip().replace('\"', '').upper()
        for author in author_list:
            if not author in author_conf_dict:
                author_conf_dict[author] = set()
            author_conf_dict[author].add(acronym)

    author_conf_dict.pop('')
    print ('done')
    conf_dis_dict = {}
    for key, values in author_conf_dict.items():
        com = combinations(list(values),2)
        G.add_edges_from(list(combinations(values, 2)))
        if not len(values) in conf_dis_dict:
            conf_dis_dict[len(values)] = 0
        conf_dis_dict[len(values)] += 1

    conf_dis = sorted(list(conf_dis_dict.items()), key = lambda x: x[0])
    #nx.draw_circular(G)
    nx.draw_kamada_kawai(G, with_labels = True)
    print(G.degree())
   # plt.show()
        
    #plt.plot([x[0] for x in conf_dis], [np.log(x[1]) for x in conf_dis])
    #plt.savefig('number_of_conference.png')

        



if __name__ == '__main__':
    main()

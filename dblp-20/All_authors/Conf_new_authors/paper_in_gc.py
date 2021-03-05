from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
import random
from scipy import interpolate
import numpy as np

ccf = open('conferences_ccf.csv', 'r')
ccf.readline()
conf_field_level = {}
iden_name = {}
while True:
    crf = ccf.readline()
    if len(crf) == 0:
        break
    i = crf.split(',')
    level = i[0].strip().replace('\"', '')
    field = i[1].strip().replace('\"', '')
    acronym = i[3].strip().replace('\"', '').upper()

    url = i[-1].strip().replace('\"', '')
    iden = url.split('/')[5]
    iden_name[iden.upper()] = acronym
    acronym = iden.upper()
    conf_field_level[acronym] = [field, level]
ccf.close()

ccf = open('proceedings.csv', 'r')
author_conf_dict = {}

conf_user_coauthors = {}
conf_year_authors = {}
conf_network = {}
all_network = nx.Graph()
year_coauthor = {}


ccf.readline()
while True:
    crf = ccf.readline()
    if len(crf) == 0:
        break
    i = crf.split(',')
    if len(i) != 6:
        print (i)
        input()

    title = i[0].strip()
    author_list = i[1].strip().split('::')
    year = i[2]
    name = i[4].strip().replace('\"', '').upper()
    conference_name = i[5].strip().replace('\"', '').upper()
    pages = i[3]
    if 'technical program' in title.lower() or 'program chair' in title.lower() or 'technical chair' in title.lower() or 'message from' in title.lower():
        print (title)
        continue
    if pages != '':
        pages = int(pages)
        if pages < 0:
            pages = pages % 20
        if pages < 6:
            continue


    if not conference_name in conf_user_coauthors:
        conf_user_coauthors[conference_name] = {}
        conf_user_coauthors[conference_name]['paper_nums_author_nums'] = [0, 0]

        conf_year_authors[conference_name] = {}
        conf_network[conference_name] = nx.Graph()
    if not year in conf_year_authors[conference_name]:
        conf_year_authors[conference_name][year] = []

    for author in author_list:
        if not author in conf_user_coauthors[conference_name]:
            conf_user_coauthors[conference_name][author] = {}
    conf_year_authors[conference_name][year].append(author_list)

    for author1, author2 in combinations(author_list, 2):
        if author1 not in conf_user_coauthors[conference_name][author2]:
            conf_user_coauthors[conference_name][author2][author1] = 0
            conf_user_coauthors[conference_name][author1][author2] = 0
        conf_network[conference_name].add_edge(author1, author2)
        if year < '2000':
            all_network.add_edge(author1, author2)
        else:
            if not year in year_coauthor:
                year_coauthor[year] = set()
            year_coauthor[year].add((author1, author2))


prog_chair = open('program_chairs.csv', 'r',encoding='utf-8')
year_chairs = {}
prog_chair.readline()
while True:
    line = prog_chair.readline()
    if len(line) == 0:
        break
    line = line.split(';')
    conf = line[0].strip().replace('\"', '').upper()
    year = line[1].strip().replace('\"', '')
    chair = line[2].strip().replace('\"', '')
    if year >= '2000' and year <= '2018' and conf in conf_network:
        if not year in year_chairs:
            year_chairs[year] = []
        year_chairs[year].append([conf, chair])

#nar = new author ratio

fout = open('conf_year_dis.txt', 'w')
conf_distance = {}

conf_data = {}
conf_radius = {}
conf_diameter = {}
conf_ave_length = {}
for conf, year_authors in conf_year_authors.items():
    #if not conf in ['INFOCOM', 'NIPS', 'FOCS', 'CRYPTO', 'ICNP', 'AAAI', 'ICDE', 'STOC', 'ICML', 'ICCV']:
    #    continue

    network = nx.Graph()
    paper_in_gc_rate = []
    diameter_list = []
    ave_length_list = []
    new_all_papers = []
    for year, authors in sorted(year_authors.items(), key = lambda x: x[0]):
        new = 0
        component = [x for x in nx.connected_components(network)] 
        
        if len(component) == 0:
            gc = set()
        else:
            gc = max(component, key = len)
        for author_list in authors:
            author_in_gc = 0  #number of authors already in the network (ever published a paper in the conference)
            for author in author_list:
                if author in network:
                    author_in_gc = 1
            new = new + 1 - author_in_gc
        
        new_all_papers.append([new, len(authors)])
        for author_list in authors:
            for author1, author2 in combinations(author_list, 2):
                network.add_edge(author1, author2)
        #paper_in_gc_rate.append([year, paper_with_author_in_gc / len(authors)])
        #largest_cc = max(nx.connected_components(network), key = len)
        #diameter_list.append([year, nx.diameter(network.subgraph(largest_cc))])
        #conf_data[conf] = paper_with
    #print (conf, ave_length_list)
    y = 0
    #calculate average
    '''
    for n, a in new_all_papers:
        y += n / a  / len(new_all_papers) 
    '''
    conf_data[conf] = new_all_papers

    conf_ave_length[conf] = ave_length_list
style_dict = {'A': ['r', 'o'], 'B': ['b', '^'],'C':['g', 'v']}

#data = sorted(conf_ave_length.items(), key = lambda x: sum (_[1] for _ in x[1]) / len(x[1]))
#aata = sorted(conf_data.items(), key = lambda x: sum (_[1] for _ in x[1]) / len(x[1]))

conf_acc = []
level_data = {'A': [], 'B': [],'C':[]}
fout = open('rank_p_in_gc.txt', 'w')
for conf, data in sorted(conf_data.items(), key = lambda x: x[1]):
    level = conf_field_level[conf][1]
    if len(data) < 15:
        continue
    #if level == 'C':
    #    continue
    conf_acc.append([conf, data])
    print (conf, level, 1 - data[-1][0] / data[-1][1], file = fout)
    if len(data) > len(level_data[level]):
        level_data[level] = level_data[level] + [[0,0] for i in range(len(data) - len(level_data[level]))]
    for i, c in enumerate(data):
        level_data[level][i][0] += c[0] / c[1]
        level_data[level][i][1] += 1
    #if data[0] in ['INFOCOM', 'NIPS', 'FOCS', 'CRYPTO', 'ICNP']:
    #plt.plot([_[1] / sum (x[1] for x in data) for _ in data], label = data[0], linewidth = 4)
    #plt.scatter(a, data, edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none')
        #plt.scatter(i, sum(_[1] for _ in data[1][-5:])/ len(data[1][-5:]), edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none', label = 'CCF_' + level)



'''
for i, value in enumerate(conf_acc):
    level = conf_field_level[value[0]][1]
    plt.scatter(i, value[1], edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none')
    print(value[0], level, value[1],  file = fout)
plt.xlabel('Conferences', fontsize = 10)
plt.ylabel('Authors in GC index', fontsize = 10)
plt.xticks([x for x in range(len(conf_acc))],[i[0] for i in conf_acc], fontsize = 2, rotation = 90)
plt.legend()
'''
ly = 0
for level, data in level_data.items():
    x = [i for i in range(len(data))]
    x_smooth = np.linspace(0, len(x), 10)
    y_smooth = interpolate.make_interp_spline(x,  [x[0] / x[1] for x in data])(x_smooth)
    #plt.plot(x_smooth, y_smooth, color = style_dict[level][0], label = 'CCF_' + level, linewidth = 4)
    plt.plot(x,  [x[0] / x[1] for x in data], color = style_dict[level][0], label = 'CCF_' + level, linewidth = 4)
    ly = max(ly, len(data))
plt.xlabel('Number of Years', fontsize = 8)
plt.ylabel('Average ratio of paper with all new authors', fontsize = 8)
plt.xticks([x for x in range(ly)],[i + 1 for i in range(ly)], fontsize = 7, rotation = 45)
plt.legend()
plt.tight_layout()
plt.savefig('new_author.png', dpi = 300)

from itertools import combinations
import re
import matplotlib.pyplot as plt
import networkx as nx
import random

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
    conference_name = iden.upper()
    conf_field_level[acronym] = [field, level]
ccf.close()

ccf = open('../proceedings.csv', 'r')
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
    acronym = i[4].strip().replace('\"', '').upper()
    conference_name = i[5].strip().replace('\"', '').upper()

    pages = i[3]
    if 'technical program' in title.lower() or 'program chair' in title.lower() or 'technical chair' in title.lower() or 'message from' in title.lower():
        print (title)
        continue
    if pages != '':
        pages = int(pages)
        if pages < 0:
            pages = pages % 20
        #if pages < 6:
        #    continue

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
    conf_year_authors[conference_name][year].append([author_list, title])

    for author1, author2 in combinations(author_list, 2):
        if author1 not in conf_user_coauthors[conference_name][author2]:
            conf_user_coauthors[conference_name][author2][author1] = 0
            conf_user_coauthors[conference_name][author1][author2] = 0
        conf_network[conference_name].add_edge(author1, author2)
        if year < '1990':
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
    if year >= '1991' and year <= '2018' and conf in conf_network:
        if not year in year_chairs:
            year_chairs[year] = []
        year_chairs[year].append([conf, chair])

#nar = new author ratio

fout = open('conf_year_dis.txt', 'w')
fout1 = open('selfpapaer.txt', 'w')
conf_distance = {}
for year, chairs in sorted(year_chairs.items(), key = lambda x : x[0]):
    for conf, chair in chairs:
        if not conf in conf_distance:
            conf_distance[conf] = {}
        if not chair in all_network.nodes():

            name0 = chair.split()[0]
            name1 = chair.split()[-1]
            
           # name = re.compile(name0 + '.*' + name1)
            match_names = []
            for author in all_network.nodes:
                if re.match(name0 + '.+' + name1, author):
                    match_names.append(author)
            if match_names:
                chair = match_names[0]
            else:
                continue

        print (year, conf, chair)
        length = nx.single_source_shortest_path_length(all_network, chair)
        authors = conf_year_authors[conf].get(year, [])
        for authors_list in authors:
            distances = []
            author_list = authors_list[0]
            title = authors_list[1]
            for author in author_list:
                distance = length.get(author, -1)
                distances.append(distance)
                if distance == 0:
                    print (conf, year, author_list, chair, title)
                    print (conf, year, ':'.join(author_list), chair, title, sep = ';', file = fout1)
                conf_distance[conf][distance] = conf_distance[conf].get(distance, 0) + 1
            print (conf, year, ':'.join([str(x) for x in distances]), file = fout)
    for author1, author2 in year_coauthor[year]:
        all_network.add_edge(author1, author2)

for conf, distance in conf_distance.items():
    print (conf)
    print (distance)
    dis = sorted(distance.items(), key = lambda x:x[0])
    print (conf, dis, file = fout)
    plt.plot([x[1] for x in dis])
    
plt.savefig('test.png')
'''
style_dict = {'A': ['r', 'o'], 'B': ['b', '^'],'C':['g', 'v']}
#conf_network['all'] = all_network
for key in conf_network.keys():
    sorted_time_edges = sorted(conf_year_authors[key].items(), key = lambda x: x[0])
    
    network = nx.Graph()
    gaint_component_time = []
    for year, coauthor_list in sorted_time_edges:
        if not coauthor_list:
            continue
        for author1, author2 in coauthor_list:
            network.add_edge(author1, author2)

        largest_cc = max(nx.connected_components(network), key = len)
        
        gaint_component_time.append(len(largest_cc)/ len(network)) 

    if len(gaint_component_time) > 10:
        plt.plot([x for x in range(len(gaint_component_time))], gaint_component_time, style_dict[conf_field_level[key][1]][0], label = key)


plt.legend()
plt.show()
input()

        

'''

name_k_list = sorted(name_k_list, key = lambda x: x[1][0])
for i in range(len(name_k_list)):
    name_k_list[i].append(i + 1)
name_k_list = sorted(name_k_list, key = lambda x: x[1])
#plt.plot([x for x in range(len(name_k_list))], [y[1][0] for y in name_k_list], '.-', label = 'Giant_component')

data_level_dict = {'A':[], 'B':[], 'C':[]}

fig = plt.figure()
ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])

for i in range(len(name_k_list)):
    #plt.scatter(i, name_k_list[i][1][0], c = name_k_list[i][2][0], marker = name_k_list[i][2][1])    
    data_level_dict[name_k_list[i][2]].append([i, name_k_list[i][1][0]])    
level_data = []
for key, value in data_level_dict.items():
    level_data.append([key, sum([x[1] for x in value])/ len(value)])
    print (key, sum([x[1] for x in value])/ len(value))
    ax1.scatter([i[0] for i in value], [i[1] for i in value], edgecolor = style_dict[key][0], marker = style_dict[key][1] , s = 40, color = 'none', label = 'CCF_' + key)
for i in range(len(name_k_list)):
    ax1.scatter(i, name_k_list[i][1][0], c = style_dict[name_k_list[i][2]][0], marker = style_dict[name_k_list[i][2]][1])    

ax1.set_xlabel('Conference Names')
ax1.set_ylabel('Gaint Component(%)')

ax1.set_xticks([x for x in range(len(name_k_list))])
ax1.set_xticklabels([y[0] for y in name_k_list], rotation = 90, fontsize = 1)
ax1.legend()
#ax1.tight_layout()

plt.axes([0.6, 0.2, 0.25, 0.25])
plt.plot([x for x in range(len(level_data))], [y[1] for y in level_data])
plt.xlabel('Conference Level', fontsize = 5)
plt.ylabel('Average GC(%)', fontsize = 5)
plt.xticks([x for x in range(len(level_data))],[i[0] for i in level_data], fontsize = 4)
plt.savefig('gaint_component.png', dpi = 600)
fout = open('rank_giant_component.txt', 'w')
for item in name_k_list:
    print (item[0], item[2], item[1], file = fout)

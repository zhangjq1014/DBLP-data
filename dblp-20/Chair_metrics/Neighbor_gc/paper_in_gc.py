from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
import random
import matplotlib
matplotlib.use('Agg')

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
conf_year_pgc = {}
for conf, year_authors in conf_year_authors.items():
    #if not conf in ['INFOCOM', 'NIPS', 'FOCS', 'CRYPTO', 'ICNP', 'AAAI', 'ICDE', 'STOC', 'ICML', 'ICCV']:
    #    continue

    conf_year_pgc[conf] = conf_year_pgc.get(conf,[])
    network = nx.Graph()
    paper_in_gc_rate = []
    diameter_list = []
    ave_length_list = []
    paper_with_author_in_gc  = {}
    for year, authors in sorted(year_authors.items(), key = lambda x: x[0]):

        paper_in_gc = 0
        component = [x for x in nx.connected_components(network)] 
        
        if len(component) == 0:
            gc = set()
        else:
            gc = max(component, key = len)
        for author_list in authors:
            author_in_gc = 0
            for author in author_list:
                if author in gc:
                    author_in_gc += 1
            paper_in_gc += author_in_gc
            paper_with_author_in_gc[author_in_gc] = paper_with_author_in_gc.get(author_in_gc, 0) + 1
        
        for author_list in authors:
            for author1, author2 in combinations(author_list, 2):
                network.add_edge(author1, author2)
        #paper_in_gc_rate.append([year, paper_with_author_in_gc / len(authors)])
        #largest_cc = max(nx.connected_components(network), key = len)
        #diameter_list.append([year, nx.diameter(network.subgraph(largest_cc))])
        #conf_data[conf] = paper_with
        conf_year_pgc[conf].append([year, paper_in_gc / len(authors)])
    y = 0
    for x, p in paper_with_author_in_gc.items():
        y += x * p / sum(x[1] for x in paper_with_author_in_gc.items()) 
    conf_data[conf] = y
    conf_ave_length[conf] = ave_length_list
style_dict = {'A': ['r', 'o'], 'B': ['b', '^'],'C':['g', 'v']}

#data = sorted(conf_ave_length.items(), key = lambda x: sum (_[1] for _ in x[1]) / len(x[1]))
#aata = sorted(conf_data.items(), key = lambda x: sum (_[1] for _ in x[1]) / len(x[1]))

conf_acc = []
for conf, data in conf_year_pgc.items():
    level = conf_field_level[conf][1]
    #if level == 'C':
    #    continue
    data.sort(key = lambda x: int(x[0]))
    if len(data) < 10:
        continue
    #Last 5 venues
    #data = [x[1] for x in data[-5:]]
    #All venues
    data = [x[1] for x in data]
    conf_acc.append([conf, sum(data) / len(data)])
    #if data[0] in ['INFOCOM', 'NIPS', 'FOCS', 'CRYPTO', 'ICNP']:
    #plt.plot([_[1] / sum (x[1] for x in data) for _ in data], label = data[0], linewidth = 4)
    #plt.scatter(a, data, edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none')
        #plt.scatter(i, sum(_[1] for _ in data[1][-5:])/ len(data[1][-5:]), edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none', label = 'CCF_' + level)


fout = open('rank_p_in_gc_all.txt', 'w')

for i, value in enumerate(conf_acc):
    level = conf_field_level[value[0]][1]
    plt.scatter(i, value[1], edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none')
    print(value[0], level, value[1],  file = fout)
    if len(conf_acc) - i < 6:
        if len(conf_acc) - i  >= 5:
            plt.annotate(value[0] + '(' + str(round(value[1],4)) + ')', (i, value[1]), xytext = (i - 40 -  10 * (len(conf_acc) - i ), value[1] - (len(conf_acc) - i) * 0.1), arrowprops = dict(facecolor = 'black', arrowstyle = 'fancy'))
        elif len(conf_acc) - i == 4:
            plt.annotate(value[0] + '(' + str(round(value[1],4)) + ')', (i, value[1]), xytext = (i - 40 - 10 * (len(conf_acc) - i ), value[1] - (len(conf_acc) - i) * 0.05), arrowprops = dict(facecolor = 'black', arrowstyle = 'simple'))
        else:
            plt.annotate(value[0] + '(' + str(round(value[1],4)) + ')', (i, value[1]), xytext = (i - 40 - 10 * (len(conf_acc) - i ), value[1]), arrowprops = dict(facecolor = 'black', arrowstyle = 'simple'))
plt.xlabel('Conferences', fontsize = 10)
plt.ylabel('Authors in GC index', fontsize = 10)
plt.xticks([x for x in range(len(conf_acc))],[i[0] for i in conf_acc], fontsize = 2, rotation = 90)
plt.legend()
plt.tight_layout()
plt.savefig('score_author_in_gc.png', dpi = 300)

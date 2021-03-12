from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

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

ccf = open('../conf_year_dis.txt', 'r')

conf_level_dis = {'A': {}, 'B': {}}
conf_level_dis_first = {'A': {}, 'B': {}}
conf_level_dis_all = {'A': {}, 'B': {}}
conf_dis = {}
style_dict = {'A': ['r', 'o'], 'B': ['b', '^'],'C':['g', 'v']}
level_points = {'A' : {}, 'B' : {}}
conf_year_dis = {}
while True:
    crf = ccf.readline()
    if len(crf) == 0:
        break
    i = crf.split(' ')

    conf = i[0].strip()
    year = i[1]
    dis_list = i[2].strip().split(':')

    level = conf_field_level[conf][1]
    if level == 'C':
        continue
    conf_year_dis[conf] = conf_year_dis.get(conf, {})
    conf_year_dis[conf][year] = conf_year_dis[conf].get(year, [0.0, 0.0])

    min_dist = []
    for i, val in enumerate(dis_list):
        _val = int(val)
        conf_level_dis_all[level][_val] = conf_level_dis_all[level].get(_val, 0) + 1
        if _val == -1:
            dis_list[i] = _val
            min_dist.append(100)
        else:
            dis_list[i] = _val
            min_dist.append(_val)
    dis = min(min_dist)
    if dis == 100:
        dis = -1
    dis_first = dis_list[0]
    conf_level_dis_first[level][dis_first] = conf_level_dis_first[level].get(dis_first, 0) + 1
    conf_level_dis[level][dis] = conf_level_dis[level].get(dis, 0) + 1
    if not conf in conf_dis:
        conf_dis[conf] = {}
    conf_dis[conf][dis] = conf_dis[conf].get(dis, 0) + 1

    level_points[level][(dis_first, dis)] = level_points[level].get((dis_first, 0), 0) + 1

    if dis == 1:
        conf_year_dis[conf][year][0] += 1
    conf_year_dis[conf][year][1] += 1

    #print (conf_level_dis)
    #input()

#for conf, dis in conf_dis.items():
    #level = conf_field_level[conf][1]
    
conf_acc = []
for key, value in conf_year_dis.items():
    level = conf_field_level[conf][1]

    data = sorted(value.items(), key = lambda x: int(x[0]))
    print (key, data)
    if key == 'ICASSP':
        input()
    if len(data) < 5:
        continue
    data = data[-5:]
    conf_acc.append([key, sum([x[1][0] / x[1][1] for x in data]) / len(data)])

fout = open('rank_pap_5.txt', 'w')

conf_acc = sorted(conf_acc, key = lambda x: x[1])
for i, value in enumerate(conf_acc):
    level = conf_field_level[value[0]][1]
    plt.scatter(i, value[1], edgecolor = style_dict[level][0], marker = style_dict[level][1] , s = 60, color = 'none')
    print(value[0], level, value[1],  file = fout)
    if len(conf_acc) - i < 6:
        print (value[0], value[1])
    if len(conf_acc) - i < 6:
        if len(conf_acc) - i >= 2:
            plt.annotate(value[0] + '(' + str(round(value[1],4)) + ')', (i, value[1]), xytext = (i - 10 * (len(conf_acc) - i), value[1] + 0.03 * (6 - len(conf_acc) + i)), arrowprops = dict(facecolor = 'black', arrowstyle = 'fancy'))
        else:
            plt.annotate(value[0] + '(' + str(round(value[1],4)) + ')', (i, value[1]), xytext = (i - 30, value[1]), arrowprops = dict(facecolor = 'black', arrowstyle = 'fancy'))
plt.xlabel('Conferences', fontsize = 10)
plt.ylabel('Accepted paper from Chairs collaborators', fontsize = 10)
plt.xticks([x for x in range(len(conf_acc))],[i[0] for i in conf_acc], fontsize = 3, rotation = 90)
plt.tight_layout()
plt.legend()
plt.savefig('p_ap.png', dpi = 300)
plt.show()

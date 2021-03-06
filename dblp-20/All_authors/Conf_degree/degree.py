from itertools import combinations
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
print (conf_field_level)
input()

ccf = open('../../proceedings.csv', 'r')
author_conf_dict = {}

conf_user_coauthors = {}
conf_year_authors = {}
conf_network = {}
all_network = nx.Graph()


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
    if 'technical program' in title.lower():
        print (title)
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
        conf_year_authors[conference_name][year] = set([])

    conf_user_coauthors[conference_name]['paper_nums_author_nums'][0] += 1
    conf_user_coauthors[conference_name]['paper_nums_author_nums'][1] += len(author_list)
    for author in author_list:
        if not author in conf_user_coauthors[conference_name]:
            conf_user_coauthors[conference_name][author] = {}
        conf_year_authors[conference_name][year].add(author)

    for author1, author2 in combinations(author_list, 2):
        if author1 not in conf_user_coauthors[conference_name][author2]:
            conf_user_coauthors[conference_name][author2][author1] = 0
            conf_user_coauthors[conference_name][author1][author2] = 0
        conf_network[conference_name].add_edge(author1, author2)
        all_network.add_edge(author1, author2)


#nar = new author ratio
name_k_list = []
#conf_network['all'] = all_network
for key in conf_network.keys():
    network = conf_network[key]
    component_ratio_list = []
    largest_cc = max(nx.connected_components(network), key = len)
    av_degree = sum(val for (node, val) in network.subgraph(largest_cc).degree()) / len(largest_cc)
    for item in nx.connected_components(network):
        component_ratio_list.append(len(item) ) #len(conf_network[key]))
    sorted_component = sorted(component_ratio_list[:10], reverse = True)
    name_k_list.append([key, [av_degree] + [len(conf_network[key])], conf_field_level[key][1]])
    '''
    if len(largest_cc)  ==  sorted_component[0]:
        continue
    print (name_k_list[-1])
    print (len(largest_cc))
    print (len(network))
    print (len(largest_cc) / len(network))
    print (sorted_component)
    input()
    '''



'''
    degree = 0
    for author in conf_user_coauthors[key]:
        degree += len(conf_user_coauthors[key][author])
    paper_num  = conf_user_coauthors[key]['paper_nums_author_nums'][0]
    author_num  = conf_user_coauthors[key]['paper_nums_author_nums'][1]
    conf_user_coauthors[conference_name]['paper_nums_author_nums'][1] += len(author_list)
    name_k_list.append([key, degree/len(conf_user_coauthors[key]), float(author_num) / paper_num, 1.0 * degree/len(conf_user_coauthors[key]) /  (float(author_num) / paper_num)])
    #print (key, len(conf_user_coauthors[key]), degree/len(conf_user_coauthors[key]), float(author_num) / paper_num)

    time_list = list(conf_year_authors[key].keys())
    time_list.sort()
    
    author_old = conf_year_authors[key][time_list[0]]
    new_author_ratio_list = []
    for i in range(1, len(time_list)):
        new_author_number = 0.0
        for author in conf_year_authors[key][time_list[i]]:
            if not author in author_old:
                new_author_number += 1
                author_old.add(author)
        print (time_list[i], new_author_number, len(conf_year_authors[key][time_list[i]]), new_author_number / len(conf_year_authors[key][time_list[i]]))
        new_author_ratio_list.append(new_author_number / len(conf_year_authors[key][time_list[i]]))
        #input()

    if len(new_author_ratio_list) >= 10:
        name_k_list[-1].append(sum(new_author_ratio_list[-10:]) / 10)
    else:
        name_k_list[-1].append(sum(new_author_ratio_list) / len(new_author_ratio_list))
        

    #print (key, len(time_list))
    conf_new_author_ratio_dict[key] = new_author_ratio_list
    #print (time_list)
    #input()

'''

style_dict = {'A': ['r', 'o'], 'B': ['b', '^'],'C':['g', 'v']}
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
ax1.set_ylabel('Average Degree in GC (<k>)')

ax1.set_xticks([x for x in range(len(name_k_list))])
ax1.set_xticklabels([y[0] for y in name_k_list], rotation = 90, fontsize = 1)
ax1.legend()
#ax1.tight_layout()

plt.axes([0.4, 0.45, 0.3, 0.3])
plt.plot([x for x in range(len(level_data))], [y[1] for y in level_data])
plt.xlabel('Conference Level', fontsize = 8)
plt.ylabel('Average degree (<k>)', fontsize = 8)
plt.xticks([x for x in range(len(level_data))],[i[0] for i in level_data], fontsize = 8)
plt.savefig('degree.png', dpi = 600)
fout = open('rank_degree_component.txt', 'w')
for item in name_k_list:
    print (item[0], item[2], item[1], file = fout)

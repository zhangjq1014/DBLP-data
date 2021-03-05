from lxml import etree
from datetime import datetime
import csv
import codecs
import ujson
import re

# all of the element types in dblp
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
# all of the feature types in dblp
all_features = {"address", "author", "booktitle", "cdrom", "chapter", "cite", "crossref", "editor", "ee", "isbn",
                "journal", "month", "note", "number", "pages", "publisher", "school", "series", "title", "url",
                "volume", "year"}


def log_msg(message):
    """Produce a log with current time"""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)


def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd


def clear_element(element):
    """Free up memory for temporary element tree after processing the element"""
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]
 

def count_pages(pages):
    """Borrowed from: https://github.com/billjh/dblp-iter-parser/blob/master/iter_parser.py
    Parse pages string and count number of pages. There might be multiple pages separated by commas.
    VALID FORMATS:
        51         -> Single number
        23-43      -> Range by two numbers
    NON-DIGITS ARE ALLOWED BUT IGNORED:
        AG83-AG120
        90210H     -> Containing alphabets
        8e:1-8e:4
        11:12-21   -> Containing colons
        P1.35      -> Containing dots
        S2/109     -> Containing slashes
        2-3&4      -> Containing ampersands and more...
    INVALID FORMATS:
        I-XXI      -> Roman numerals are not recognized
        0-         -> Incomplete range
        91A-91A-3  -> More than one dash
        f          -> No digits
    ALGORITHM:
        1) Split the string by comma evaluated each part with (2).
        2) Split the part to subparts by dash. If more than two subparts, evaluate to zero. If have two subparts,
           evaluate by (3). If have one subpart, evaluate by (4).
        3) For both subparts, convert to number by (4). If not successful in either subpart, return zero. Subtract first
           to second, if negative, return zero; else return (second - first + 1) as page count.
        4) Search for number consist of digits. Only take the last one (P17.23 -> 23). Return page count as 1 for (2)
           if find; 0 for (2) if not find. Return the number for (3) if find; -1 for (3) if not find.
    """
    cnt = 0
    for part in re.compile(r",").split(pages):
        subparts = re.compile(r"-").split(part)
        if len(subparts) > 2:
            continue
        else:
            try:
                re_digits = re.compile(r"[\d]+")
                subparts = [int(re_digits.findall(sub)[-1]) for sub in subparts]
            except IndexError:
                continue
            cnt += 1 if len(subparts) == 1 else subparts[1] - subparts[0] + 1
    return "" if cnt == 0 else str(cnt)


def extract_feature(elem, features, include_key=False):
    """Extract the value of each feature"""
    if include_key:
        attribs = {'key': [elem.attrib['key']]}
    else:
        attribs = {}
    for feature in features:
        attribs[feature] = []
    for sub in elem:
        if sub.tag not in features:
            continue
        if sub.tag == 'title':
            text = re.sub("<.*?>", "", etree.tostring(sub).decode('utf-8')) if sub.text is None else sub.text
        elif sub.tag == 'pages':
            text = count_pages(sub.text)
        else:
            text = sub.text
        if text is not None and len(text) > 0:
            attribs[sub.tag] = attribs.get(sub.tag) + [text]
    return attribs


def parse_all(dblp_path, save_path, include_key=False):
    log_msg("PROCESS: Start parsing...")
    f = open(save_path, 'w', encoding='utf8')
    for _, elem in context_iter(dblp_path):
        if elem.tag in all_elements:
            attrib_values = extract_feature(elem, all_features, include_key)
            f.write(str(attrib_values) + '\n')
        clear_element(elem)
    f.close()
    log_msg("FINISHED...")  # load the saved results line by line using json


def parse_entity(dblp_path, save_path, type_name, features=None, save_to_csv=False, include_key=False, conf_field_level = {}, chairs_data = {}):
    """Parse specific elements according to the given type name and features"""
    log_msg("PROCESS: Start parsing for {}...".format(str(type_name)))
    assert features is not None, "features must be assigned before parsing the dblp dataset"
    results = []
    attrib_count, full_entity, part_entity = {}, 0, 0
    f = open(save_path, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    writer.writerow(features)  # write title
    for _, elem in context_iter(dblp_path):
        if elem.tag in type_name:
            attrib_values = extract_feature(elem, features, include_key)  # extract required features
            results.append(attrib_values)  # add record to results array

            booktitle = attrib_values['booktitle']
            title = attrib_values['title']
            pages = attrib_values['pages']
            if not attrib_values['crossref']:
                conf = attrib_values['booktitle'][0]
                suffix = '0000'
            else:
                ref = attrib_values['crossref'][0].split('/')
                conf = ref[1]
                suffix = ref[2]
            if conf.upper() in conf_field_level and len(suffix) == 4:
            #if len(attrib_values['booktitle']) != 0 and (attrib_values['booktitle'][0].upper() in conf_field_level):
                #print (booktitle, conf, ref, title, pages)
                for author in attrib_values['author']:
                    if author in chairs_data:
                        booktitle = attrib_values['booktitle'][0].upper()
                        year =  attrib_values['year'][0]
                        if not year in chairs_data[author]:
                            chairs_data[author][year] = []
                        chairs_data[author][year].append(booktitle)
                #row = ['::'.join(v) for v in list(attrib_values.values())]
                attrib_values['crossref'] = [conf.upper()]
                row = ['::'.join(v).replace('\n', '').replace(',', '') for v in list(attrib_values.values())]
                writer.writerow(row)
                #print (attrib_values)  # add record to results array
                #print (attrib_values['booktitle'][0].upper())  # add record to results array
                #input()
            for key, value in attrib_values.items():
                attrib_count[key] = attrib_count.get(key, 0) + len(value)
            cnt = sum([1 if len(x) > 0 else 0 for x in list(attrib_values.values())])
            if cnt == len(features):
                full_entity += 1
            else:
                part_entity += 1
        elif elem.tag not in all_elements:
            continue
        clear_element(elem)
    f.close()
    '''
    if save_to_csv:
        f = open(save_path, 'w', newline='', encoding='utf8')
        writer = csv.writer(f, delimiter=',')
        writer.writerow(features)  # write title
        for record in results:
            # some features contain multiple values (e.g.: author), concatenate with `::`
            row = ['::'.join(v) for v in list(record.values())]
            writer.writerow(row)
        f.close()
    else:  # default save to json file
        with codecs.open(save_path, mode='w', encoding='utf8', errors='ignore') as f:
            ujson.dump(results, f)
    '''
    return full_entity, part_entity, attrib_count


def parse_author(dblp_path, save_path, save_to_csv=False):
    type_name = ['article', 'book', 'incollection', 'inproceedings']
    log_msg("PROCESS: Start parsing for {}...".format(str(type_name)))
    authors = set()
    for _, elem in context_iter(dblp_path):
        if elem.tag in type_name:
            authors.update(a.text for a in elem.findall('author'))
        elif elem.tag not in all_elements:
            continue
        clear_element(elem)
    if save_to_csv:
        f = open(save_path, 'w', newline='', encoding='utf8')
        writer = csv.writer(f, delimiter=',')
        writer.writerows([a] for a in sorted(authors))
        f.close()
    else:
        with open(save_path, 'w', encoding='utf8') as f:
            f.write('\n'.join(sorted(authors)))
    log_msg("FINISHED...")


def parse_article(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ['article']
    features = ['title', 'author', 'year', 'journal', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total articles found: {}, articles contain all features: {}, articles contain part of features: {}'
            .format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_inproceedings(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["inproceedings"]
    features = ['title', 'author', 'year', 'pages', 'booktitle']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total inproceedings found: {}, inproceedings contain all features: {}, inproceedings contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_proceedings(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["proceedings"]
    features = ['title', 'editor', 'year', 'booktitle', 'series', 'publisher']
    # Other features are 'volume','isbn' and 'url'.
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total proceedings found: {}, proceedings contain all features: {}, proceedings contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_book(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["book"]
    features = ['title', 'author', 'publisher', 'isbn', 'year', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total books found: {}, books contain all features: {}, books contain part of features: {}'
            .format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_publications(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ['article', 'book', 'incollection', 'inproceedings']
    features = ['title', 'year', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total publications found: {}, publications contain all features: {}, publications contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def main():
    ccf = open('conferences_ccf.csv', 'r')
    ccfcontent = []

    ccf.readline()
    while True:
        crf = ccf.readline()
        if len(crf) == 0:
            break
        newcontent = crf.split(',')
        ccfcontent.append(newcontent)
    #print(ccfcontent)

    ccf_field_level_dict = {}
    conf_field_level = {}

    for i in ccfcontent:

        level = i[0].strip().replace('\"', '')
        field = i[1].strip().replace('\"', '')
        acronym = i[3].strip().replace('\"', '')
        url = i[-1].strip().replace('\"', '')
        iden = url.split('/')[5]
        acronym = iden.upper()

        if not field in ccf_field_level_dict:
            ccf_field_level_dict[field] = {}

        if not level in ccf_field_level_dict[field]:
            ccf_field_level_dict[field][level] = set()
        
        ccf_field_level_dict[field][level].add(acronym.upper())
        conf_field_level[acronym] = [field, level]
    print (conf_field_level['IMC'])
    input()


    #program_chairs
    prog_chair = open('program_chairs.csv', 'r',encoding='utf-8')
    conf_year_chair_dict = {}
    chairs_data = {}
    chairs_year = []
    prog_chair.readline()
    while True:
        line = prog_chair.readline()
        if len(line) == 0:
            break
        line = line.split(';')
        conf = line[0].strip().replace('\"', '').upper()
        year = line[1].strip().replace('\"', '')
        chair = line[2].strip().replace('\"', '')

        #if not conf.upper() in conf_field_level:
        #    print (conf)
        #    input()
        if year > '2000' and year < '2015':
            chairs_data[chair] = {}
            chairs_year.append([chair, year, conf])
        if not conf in conf_year_chair_dict:
             conf_year_chair_dict[conf] = {}
        if not year in conf_year_chair_dict[conf.upper()]:
             conf_year_chair_dict[conf][year] = set()
        conf_year_chair_dict[conf][year].add(chair)


    print (len(chairs_data))
    input()
    dblp_path = 'dblp-2021-01-02.xml'
    save_path = 'proceedings.csv'
    try:
        context_iter(dblp_path)
        log_msg("LOG: Successfully loaded \"{}\".".format(dblp_path))
    except IOError:
        log_msg("ERROR: Failed to load file \"{}\". Please check your XML and DTD files.".format(dblp_path))
        exit()

    type_name = ["inproceedings"]
    features = ['title', 'author', 'year', 'pages', 'booktitle','crossref']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=True, conf_field_level = conf_field_level, chairs_data = chairs_data)

    print(len(chairs_data))

    fout = open('chair_before_after.txt', 'w')

    for chair, yr, conf in chairs_year:
        data_before = []
        data_after = []
        for year in chairs_data[chair]:
            #if int(year) >= int(yr) - 5 and int(year) < int(yr):
            if int(year) < int(yr):
                data_before += chairs_data[chair][year]
            #elif int(year) > int(yr) and int(year) <= int(yr) + 5:
            elif int(year) > int(yr):
                data_after += chairs_data[chair][year]
        print (chair, yr, conf)
        print (data_before)
        print (data_after)

        if data_before == [] and data_after == []:
            continue

        print (chair, yr, conf, ','.join(data_before), ','.join(data_after), sep = ';', file = fout)

        




if __name__ == '__main__':
    main()

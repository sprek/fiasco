""" This module defines Playset classes and provides functions for
loading from file, and loading/writing to database
"""

import re, sys

# possible categories:
CATEGORIES = ["relationships", "needs", "locations", "objects"]
REL_FLAGS = ['exclusive', 'same']

class Playset:
    """ Playset class
    name                                     : string
    relationships, needs, locations, objects : EntryGroup
    """
    def __init__(self, name, relationships, needs, locations, objects):
        self.name = name
        self.relationships = relationships
        self.needs = needs
        self.locations = locations
        self.objects = objects

class EntryGroup:
    """ EntryGroup contains lists of entries
    title   : string
    entries : list of RelEntry or string
    """
    def __init__(self, title, entries):
        self.title = title
        self.entries = entries

class RelEntry:
    """ RelEntry defines a relationship pair
    rel_a         : string
    rel_a_options : list of strings
    rel_b         : string
    rel_b_options : list of strings
    """
    def __init__(self, rel_a, rel_a_options, rel_b, rel_b_options, flag):
        self.rel_a = rel_a
        self.rel_a_options = rel_a_options
        self.rel_b = rel_b
        self.rel_b_options = rel_b_options
        self.flag = flag

def parse_playset(file):
    """ Parses a playset file
    returns: Playset class
    """
    pf = open(file, 'r')
    cat = ''
    entry_num = ''
    playset = Playset ('', [], [], [], [])
    cur_list = []
    for line in pf:
        line = line.strip()
        m = re.match('^# *(.+)', line)
        m2 = re.match('^@.+?(\w+)',line)
        if m:
            if playset.name == '':
                playset.name = m.group(1)
        elif m2:
            # got a main level category
            cat = m2.group(1).lower()
            if not cat in CATEGORIES:
                print ("invalid category detected: " + cat)
                sys.exit(1)
            cur_list = getattr(playset, cat)
        else:
            # dual entry with a /
            m1 = re.match(' *(\d.+?) +(.+?)/(.+)', line)
            # single entry without a /
            m2 = re.match(' *(\d\..+?) +(.+)', line)
            # group name
            m3 = re.match(' *(\d+) +(.+)', line)
            if cat == 'relationships' and m1:
                cur_list[-1].entries.append(
                    RelEntry(m1.group(2).strip(), [], m1.group(3).strip(), [], ''))
            elif m2:
                entry_num = m2.group(1).strip()
                # check if this is a sub group
                if 'a' in entry_num:
                    cur_list[-1].entries[-1].rel_a_options.append(m2.group(2).strip())
                elif 'b' in entry_num:
                    cur_list[-1].entries[-1].rel_b_options.append(m2.group(2).strip())
                else:
                    cur_list[-1].entries.append(m2.group(2).strip())
                if 'x' in entry_num:
                    cur_list[-1].entries[-1].flag = 'exclusive'
                elif 's' in entry_num:
                    cur_list[-1].entries[-1].flag = 'same'
            elif m3:
                cur_list.append(EntryGroup(m3.group(2).strip(), []))
    pf.close()
    return playset

def get_relationship_indices(rel_name_a, rel_name_b, rel_a_option, rel_b_option, playset):
    """
    input: relationship name, playset
    returns: if found: (int index of relationship category,
                        int index of relationship,
                        int index of rel option a (or -1 for none),
                        int index of rel option b (or -1 for none),
                        string flag)
             if not found: None
    """
    for i, rel in enumerate(playset.relationships):
        for j, entry in enumerate(rel.entries):
            if rel_name_a == entry.rel_a and rel_name_b == entry.rel_b:
                rel_a_index = -1
                rel_b_index = -1
                if rel_a_option:
                    for k, opt in enumerate(entry.rel_a_options):
                        if opt == rel_a_option:
                            rel_a_index = k
                    if rel_a_index == -1:
                        # rel_a_option was set, but not found in the playset
                        return None
                if rel_b_option:
                    for k, opt in enumerate(entry.rel_b_options):
                        if opt == rel_b_option:
                            rel_b_index = k
                    if rel_b_index == -1:
                        # rel_b_option was set, but not found in the playset
                        return None        
                return (i,j,rel_a_index,rel_b_index, entry.flag)
    return None

def get_relationship_id_from_indices(indices, flip_a_b):
    """
    input: indices - tuples where indices[0] is the relationship category index,
                                  indices[1] is the relationship pair index,
                                  indices[2] is the relationship option a index,
                                  indices[3] is the relationship option b index,
                                  indices[4] is the relationship flags
           flip_a_b - True if the a and b relationship indices should be swapped
    returns: a string of the indices joined on '.'
    """
    new_indices = indices
    if flip_a_b:
        new_indices = (indices[0], indices[1], indices[3], indices[2], indices[4])
    return '.'.join(list(map(str, new_indices)))

if __name__ == '__main__':
    main_playset = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
    print("PLAYSET NAME: " + main_playset.name)
    for rel in main_playset.relationships:
        print("RELATIONSHIP TITLE : " + rel.title)
        for entry in rel.entries:
            print("REL A: " + entry.rel_a + " OPTIONS: " + str(entry.rel_a_options))
            print("REL B: " + entry.rel_b + " OPTIONS: " + str(entry.rel_b_options))
    for need in main_playset.needs:
        print("NEED TITLE: " + need.title)
        for entry in need.entries:
            print("NEED: "+ entry)
    for location in main_playset.locations:
        print("LOCATION TITLE: " + location.title)
        for entry in location.entries:
            print("LOCATION: "+ entry)
    for obj in main_playset.objects:
        print("OBJECT TITLE: " + obj.title)
        for entry in obj.entries:
            print("OBJECT: "+ entry)

import re, sys

class Entry:
    def __init__(self, name='', pair='', group='', num=0):
        self.name = name
        self.name_options = []
        self.pair = pair
        self.pair_options = []
        self.group = group
        self.num = num

# possible categories:
CATEGORIES = ["relationships", "needs", "locations", "objects"]

def parse_playset(file):
    pf = open(file, 'r')
    count = 0

    playset_dict = {}
    cat = ''
    entry_num = ''
    cat_count = 0
    last_num = 0
    last_entry = Entry
    last_group = ''
    entry_count = 1
    for line in pf:
        line = line.strip()
        m = re.match('^@.+?(\w+)',line)
        if m:
            # got a main level category
            cat = m.group(1).lower()
            if not cat in CATEGORIES:
                print "invalid category detected: " + cat
                sys.exit(1)
            playset_dict[cat] = []
        else:
            # dual entry with a /
            m1 = re.match(' *(\d.+?) +(.+?)/(.+)', line)
            # single entry without a /
            m2 = re.match(' *(\d\..+?) +(.+)', line)
            # group name
            m3 = re.match(' *(\d+) +(.+)', line)
            if cat == 'relationships' and m1:
                #print m1.group(1) + " : " + m1.group(2) + " : " + m1.group(3)
                entry_num = m1.group(1).strip()
                entry = Entry(m1.group(2).strip(), m1.group(3).strip(), last_group, num=entry_count)
                playset_dict[cat].append(entry)
                last_entry = playset_dict[cat][-1]
                last_num = last_num + 1
                entry_count += 1
            elif m2:
                entry_num = m2.group(1).strip()
                # check if this is a sub group
                if 'a' in entry_num:
                    last_entry.name_options.append(m2.group(2).strip())
                elif 'b' in entry_num:
                    last_entry.pair_options.append(m2.group(2).strip())
                else:
                    tmp_entry = Entry(m2.group(2).strip(),group=last_group,num=entry_count)
                    playset_dict[cat].append(tmp_entry)
                    entry_count += 1
            elif m3:
                last_group = m3.group(2).strip()
                entry_count = 1
                

    return playset_dict

#def get_groups(playset, category):
#    
if __name__ == '__main__':
    pd = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
    
    for cat in pd.keys():
        print "CATEGORY: " + cat
        for entry in pd[cat]:
            print "GROUP: " + entry.group
            print "ENTRY1 " + str(entry.num) + " : " + entry.name
            for opt in entry.name_options:
                print "OPTION A: " + opt
            if len(entry.pair) > 0:
                print "ENTRY2 " + str(entry.num) + " : "+ entry.pair
            for opt in entry.pair_options:
                print "OPTION B: " + opt
        

import os
import re
import pickle
from csv import reader

'''
Generic class for a node in a library system
- label is the classification number or range of classification numbers associated with this
  category
- name is the name of the category 
- depth is the the distance (in number of nodes) between the current node and the 
  root of the tree
- parent is the the direct parent of the current node
'''
class Node:
    def __init__(self, label, name, depth, parent=None):
        self.label = label
        self.name = name
        self.depth = depth
        self.parent = parent
        self.children = {}
        self.items = [] 
        self.item_idx = []
        self.item_count = 0
        self.west = None
        self.prop_m = 0
        self.prop_f = 0

    '''
    Print the tree
    '''
    def __str__(self, depth=0):
        out = "\t"*depth + f"{repr(self.depth)}: {self.label} - {self.name} ({self.item_count})\n"
        for child in self.children.values():
            out += child.__str__(depth+1)
        return out
    
    def __eq__(self, node):
        return isinstance(node, Node) and node.label == self.label and node.name == self.name
    
    '''
    Add a child to its parent node
    '''
    def add_child(self, node):
        self.children[node.label] = node
        
    '''
    Count the direct descendants of a node
    '''
    def count_children(self):
        return len([c for c in self.children.values() if c is not None])
        
    '''
    Count all the descendants of a node (direct or indirect)
    '''
    def count_descendants(self):
        count = self.count_children()
        if count == 0:
            return 0
        return count + sum([kid.count_descendants() for kid in self.children.values() if kid.label is not None])
    
    def count_nodes(self):
        return 1 + self.count_descendants()

    '''
    Add an item to a node
    '''
    def add_item(self, item, i):
        self.items.append(item)
        self.item_count += 1
        self.item_idx.append(i)

    def empty_items(self):
        self.items = []
        self.item_idx = []
        self.item_count = 0
        for child in self.children.values():
            if child is not None:
                child.empty_items()

'''
Node representing a category in the Library of Congress Classification System
'''
class LCCNode(Node):
    def __init__(self, label, name, depth, parent=None):
        super().__init__(label, name, depth, parent)

    def __eq__(self, node):
        return isinstance(node, LCCNode) and node.label == self.label and node.name == self.name
    
'''
LCC node whose label contains a number or range of numbers
'''
class NumNode(LCCNode):
    def __init__(self, label, name, depth, parent=None):
        super().__init__(label, name, depth, parent)
        # the range of numbers that books classified in this category fall within 
        self.minVal, self.maxVal = self.get_min_max()

    def __eq__(self, node):
        return isinstance(node, NumNode) and node.label == self.label and node.name == self.name

    '''
    Determine the range of numbers encompassed by the node's label
    '''
    def get_min_max(self):
        idx = getDigitIdx(self.label)
        num_str = self.label[idx:].replace('(', '')\
            .replace(')', '').replace(self.label[0], '')
        # note: might want to add some additional functionality to handle
        #  cutter info
        if '.' in num_str:
            full_stop = num_str.index('.')
            if num_str[full_stop+1].isalpha():
                num_str = num_str[:full_stop]
        if '-' in num_str:
            min_max = num_str.split('-')
            minVal = float(min_max[0])
            maxVal = float(min_max[1])
        else:
            minVal = float(num_str)
            maxVal = float(num_str)
        return minVal, maxVal
    

'''
Library of Congress Classification tree structure representation
- folder is the path for the folder in which the cvs records used to create
  the lcc tree are stored
''' 
class LCCTree:
    def __init__(self, folder):
        self.root = LCCNode('LCC', 'Library of Congress Classification', 0)
        self.labels = {}
        # used to quickly find the category associated with a classification number  
        self.hash_table = {} 
        self.item_count = 0
        self.node_count = 0
        self.build_tree(folder)

    '''
    Read lcc csv data
    '''
    @staticmethod
    def read_csv(folder):
        data = []
        for subdir, _, files in os.walk(folder):
            for file in files:
                f = subdir + os.sep + file
                cat = file[0]
                name = file[4:-4]
                with open(f, 'r', encoding="utf8") as read_obj:
                    csv_reader = reader(read_obj)
                    data.append((cat, name, list(csv_reader)))
        return data

    '''
    Find the name and label of a LCC category stored in a csv file
    '''
    @staticmethod
    def parse_csv_entry(entry, cat):
        cat_idx = entry.index(cat)
        space = entry.index(" ")
        label = entry[cat_idx:space]
        # this just means it's ordered alphabetically - ok to remove
        if '.A-Z' in label:
            label = label.replace('.A-Z', '')
        name = entry[space+1:].replace('\n', '')
        return label, name

    '''
    Get category depth from lcc csv data
    '''
    @staticmethod
    def get_cat_position(row):
        idx = [i for i in range(len(row)) if row[i] != '']
        if len(idx) > 1:
            print(f"ERROR:{row}")
        elif len(idx) == 0:
            return -1
        return idx[0]
    
    '''
    Extract the numeric portion of a LCC number
    '''
    @staticmethod
    def getDivision(subStr):
        dec_count = 0
        for idx, char in enumerate(subStr):
            if char == '.':
                dec_count += 1
            # The second decimal usually refers to a cutter number
            # Cutter numbers are ignored
            if dec_count > 1:
                return subStr[:idx]
            if not char.isdigit() and char != '.':
                return subStr[:idx]
        return subStr
    
    '''
    Convert CSV files of the LCC category sturcutre to tree data structures
    '''
    def csv_to_tree(self, csv_data):
        no_label = 0
        cat = csv_data[0] 
        name = csv_data[1]
        csv = csv_data[2]
        root = LCCNode(cat, name, 1, self.root)
        parent = root
        for row in csv:
            idx = self.get_cat_position(row)
            depth = idx + 2
            if idx != -1:
                # * is used represent categories that are represented in the structure of the LCC outline
                # but do not have a LCC number or range of LCC numbers associated with them
                if '*' in row[idx]:
                    no_label += 1
                    label = '*' * no_label
                    name = row[idx][2:]
                else:
                    label, name = self.parse_csv_entry(row[idx], cat)
                if label.isalpha() or '*' in label or (label[0] == 'K' and not bool(re.search('\d', label))):
                    node = LCCNode(label, name, depth)
                else:
                    node = NumNode(label, name, depth)
                 # Link  node to it's parent           
                while depth-1 != parent.depth:
                    parent = parent.parent
                node.parent = parent
                parent.add_child(node)
                parent = node
        return root

    '''
    Build the LCC tree structure from csv files contianing the category structure
    of the system.
    '''       
    def build_tree(self, folder):
        data = self.read_csv(folder)
        for csv in data:
            subtree = self.csv_to_tree(csv)
            label = subtree.label
            self.root.children[label] = subtree
            self.labels[subtree.label] = [kid.label[1:] for kid in subtree.children.values()
                                          if kid.label is not None and len(kid.label) > 1 
                                          and kid.label.isalpha()]
            if label != 'A':
                self.labels[subtree.label] += [None]
        self.node_count = self.root.count_descendants()

        self.build_hash() #used to access subcategories more efficiently
        self.labels['K'] = [label[1:] for label in self.hash_table['K'].keys() 
                    if label.isalpha() and  len(label) > 1 and label != 'node'] + [None]

    '''
    Build hash table entries for further divisions (numeric subcategories) of the LCC
    These categories are hashed by a tuple of the minimum and maximum value of their
    numeric range. 
    '''
    def num_hash(self, node, hash_table):
        for child in node.children.values():
            if child.label is not None:
                hash_table[(child.minVal, child.maxVal)] = child
                self.num_hash(child, hash_table)

    '''
    Build hash table entries for main- and sub-classes of the LCC for every main
    class except for K
    '''
    def alpha_hash(self, tree):
        # E anf F don't have subclasses
        if tree.label == 'E' or tree.label == 'F':
            sub_hash = {}
            self.num_hash(tree, sub_hash)
            sub_hash['node'] = tree
            self.hash_table[tree.label] = sub_hash
        else:
            self.hash_table[tree.label] = {'node': tree}
            for child in tree.children.values():
                if child.label is not None:
                    sub_hash = {}
                    self.num_hash(child, sub_hash)
                    sub_hash['node'] = child
                    self.hash_table[tree.label][child.label] = sub_hash

    '''
    Get subclass prefixes in class K
    '''
    def get_prefixes(self, node, prefixes):
        # do not want to include these exempt character sequences in the hash-table
        exempt = ['KDKDK', 'KJKKZ', 'KLKWX', 'KUAKUH', 'KKBKKC', 'KNTKNU']
        prefix = re.sub(r'[^a-zA-Z]', '', node.label)
        if prefix not in prefixes and prefix not in exempt:
            prefixes.append(prefix)
        for child in node.children.values():
            if child.label is not None:
                self.get_prefixes(child, prefixes)

    '''
    Function to build a hash table for class K
    '''
    def build_k_hash(self, node, prefixes, sub_hash):
        case2 = ['KD-KDK', 'KJ-KKZ', 'KL-KWX']
        case3 = ['KKB-KKC', 'KNT-KNU']
        case4 = 'KUA-KUH'

        for child in node.children.values():
            if child.label in prefixes:
                sub_hash[child.label]['node'] = child
            elif '*' in child.label or child.label in case2:
                pass
            elif child.label in case3:
                valid = child.label.split('-')
                sub_hash[valid[0]] = {'node': child}
                sub_hash[valid[1]] = {'node': child}
            elif child.label == case4:
                for char in 'ABCDEFGH':
                    sub_hash['KU'+char] = {'node': child}
            else:
                sub_hash[re.sub(r'[^a-zA-Z]', '', child.label)][(child.minVal, child.maxVal)] = child
            self.build_k_hash(child, prefixes, sub_hash)

    '''
    K has a different format from the rest of the LCC and thus its hash table 
    must be built in a specialized way. I.e. some subclasses are represnted by 
    two letters or ranges of letters as opposed to just one.
    '''
    def k_hash(self, k_tree):
        self.hash_table[k_tree.label] = {'node': k_tree}
        prefixes = []
        for child in k_tree.children.values():
            if child.label is not None:
                self.get_prefixes(child, prefixes)
        sub_hash = {pre: {} for pre in prefixes}
        self.build_k_hash(k_tree, prefixes, sub_hash)
        self.hash_table[k_tree.label] = {**self.hash_table[k_tree.label], **sub_hash}

    '''
    Build a hash table for the LCC which is used to more efficiently access
    its categories
    '''
    def build_hash(self):
        for tree in self.root.children.values():
            # Class K must be treated as a special case
            if tree.label == 'K':
                self.k_hash(tree)
            else:
                self.alpha_hash(tree)

    '''
    Get the components of a LCC number. They are:
    - The main class: First letter 
    - The subclass: Second (and sometimes third) letter 
    - Further division: numeric portion of the LCC number

    Not all LCC numbers have a subclass (i.e. all books classified in E and F)
    and not all LCC numbers have a division (i.e. AN for newspapers)
    '''
    def getComponents(self, lcc):
        mainCls = lcc[0]
        digIdx = getDigitIdx(lcc)
        if digIdx == -1: # there is no division beyond the subclass
            subCls = lcc[1:]
            division = None
        else:
            subCls = lcc[1:digIdx]
            division = self.getDivision(lcc[digIdx:])
            if division[-1] == '.':
                division = division[:-1]
            division = float(division)
        if subCls == '': # there is no subclass
            subCls = None
        return (mainCls, subCls, division)

    '''
    Check if a number is a valid instance of an LCC number
    '''
    def validate_lcc(self, lcc_num):
        if len(lcc_num) < 2:
            return False
        firstDigit = getDigitIdx(lcc_num)
        if (lcc_num[0] in self.labels.keys() and (firstDigit in [1, 2, 3] or 
                                                        (len(lcc_num) <= 3 and firstDigit == -1))):
            return True
    '''
    Add books from a list of books to an instance of a LCC Tree 
    Assume that item formats have already been checked as valid LCC 
    '''
    def add_books(self, bookList):
        i = -1
        for book in bookList:
            # get lcc category labels 
            mainCls, subCls, div = self.getComponents(book['lcc'])
            if subCls not in self.labels[mainCls]:
                continue
            elif subCls is None:
                subCls = mainCls
            else:
                subCls = mainCls + subCls
            # find subclass 
            if mainCls == 'E' or mainCls == 'F':
                nodes = self.hash_table[mainCls]
                node = None
            elif mainCls == 'K': 
                nodes = self.hash_table[mainCls][subCls]
                if 'node' in nodes.keys():
                    node = nodes['node']
                else:
                    node = None
            else:
                nodes = self.hash_table[mainCls][subCls]
                node = nodes['node']
            if div is not None:
                # find deepest category associated with a book
                valRange = 9999
                for label in nodes.keys():
                    if label != 'node':
                        diff = label[1] - label[0]
                        # the smaller the numerical range, the greater the depth
                        if div >= label[0] and div <= label[1] and diff <= valRange:
                            node = nodes[label]
                            valRange = diff
            # add book to its categories
            if node is not None: 
                self.item_count += 1
                book['lcc_cat'] = node 
                i += 1
            while node is not None:
                node.add_item(book, i)
                node = node.parent
            # keep track of book count 


    '''
    Remove all books from a tree
    '''
    def remove_books(self):
        root = self.root
        self.item_count = 0
        root.empty_items()

    '''
    Find the deepest node (category) that is shared by two nodes in the LCC
    '''
    def common_ancestor(self, node1, node2):
        if node1.label[0] != node2.label[0]:
            return self.root 
        else:
            d1 = node1.depth
            d2 = node2.depth 
            while d1 != d2:
                if d1 > d2:
                    node1 = node1.parent
                    d1 = node1.depth
                else:
                    node2 = node2.parent 
                    d2 = node2.depth
            while node1 != node2:
                node1 = node1.parent
                node2 = node2.parent 
            return node1


'''
Node representing a category in the Dewey Decimal Classification System
'''   
class DeweyNode(Node):
    def __init__(self, label, name, depth, parent=None):
        super().__init__(label, name, depth, parent)
        self.parse = self.label.replace('.', '')

    def __eq__(self, node):
        return isinstance(node, DeweyNode) and node.label == self.label and node.name == self.name
    
    '''
    Add a child node to the DDC
    '''
    def add_child(self, node):
        idx = node.depth-1
        ddc = node.label.replace('.', '')
        self.children[ddc[idx]] = node        

'''
Dewey Decimal System Data Structure
- folder is the path for the folder in which the txt and csv files used to create
  the DDC tree are stored
'''
class DDCTree:
    def __init__(self, folder):
        self.root = DeweyNode('DDC', 'Dewey Decimal System', 0)
        self.item_count = 0
        self.node_count = 0
        self.build_tree(folder)
    
    '''
    Convert text file of DDC categories into a DDC data structure
    for the first 3 levels of categories in the DDC
    '''
    def txt_to_tree(self, fp):
        with open(fp, 'r') as f:
            data = f.readlines()
        for row in data[1:]:
            row_data = row.replace('\n', '').split('\t')
            depth = int(row_data[2])
            label = row_data[0][:depth]
            name = row_data[1]
            node = DeweyNode(label, name, depth)
            mainClasses = self.root.children
            if depth == 1:
                mainClasses[row_data[0][0]] = node
                node.parent = self.root
            elif depth == 2:
                parent = mainClasses[row_data[0][0]]
                parent.add_child(node)
                node.parent = parent
            else: # level == 3
                gp = mainClasses[row_data[0][0]]
                parent = gp.children[row_data[0][1]]
                parent.add_child(node)
                node.parent = parent
            self.node_count += 1
        
    '''
    Get category in DDC
    '''
    def get_node(self, number):
        digits = number.replace('.', '')
        node = self.root.children[digits[0]]
        for dig in digits[1:]:
            node = node.children[dig]
        return node

    '''
    Convert csv file of DDC categories at depths of 4 or greater 
    (after the decimal place)
    ''' 
    def load_fg_cats(self, fp):
        with open (fp, 'rb') as f:
            fg_cats =  pickle.load(f)
        fg_cats.sort(key=lambda x : float(x[0]))
        fg_cats = [tup for tup in fg_cats if len(tup[0]) > 3]
        for ddc, name in fg_cats:
            parent = self.get_node(ddc[:-1])
            node = DeweyNode(ddc, name, parent.depth+1, parent)
            parent.add_child(node)
            self.node_count += 1
    
    '''
    Build a representation of the DDC
    '''
    def build_tree(self, folder):
        self.txt_to_tree(folder + '/ddc22-summaries-eng.txt')
        self.load_fg_cats(folder + '/ddc_fg_orig.pk')

    '''
    Add books from a list of books to an instance of a DDC Tree 
    Assume that item formats have already been checked as valid DDC 
    '''
    def add_books(self, bookList):
        for (i, book) in enumerate(bookList):
            ddc = book['ddc']
            digits = ddc.replace('.', '')
            node = self.root
            j = 0
            node.add_item(book, i)
            while node.children != {} and j < len(digits) and digits[j] in node.children.keys():
                child = node.children[digits[j]]
                child.add_item(book, i)
                node = child
                j += 1
            self.item_count += 1
            book['ddc_cat'] = node

    '''
    Find the deepest node (category) that is shared by two nodes in the LCC
    '''
    def common_ancestor(self, node1, node2):
        node = self.root 
        for (dig1, dig2) in zip(node1.parse, node2.parse):
            if dig1 != dig2:
                break 
            node = node.children[dig1]                  
        return node 
    
    '''
    Remove all books from a tree
    '''
    def remove_books(self):
        self.item_count = 0
        root = self.root
        root.empty_items()

'''
General functions to help with Library Classification Systems

Check if a number is a valid instance of a DDC number
'''

def validate_ddc(ddc_num):
    if ddc_num.count('.') > 1:
        cutter_idx = ddc_num.find('.', ddc_num.find('.'))
        ddc_num = ddc_num[:cutter_idx]
    if ddc_num.replace('.', '').isnumeric():
        return True
    else:
        return False
'''
Find the index of the first digit in a LCC number
'''
def getDigitIdx(lcc_num):
    for idx, char in enumerate(lcc_num):
        if char.isdigit():
            return idx
    return -1
        
'''
Remove extra characters from DDC and LCC numbers in a list of books
'''
def extract_class_num(bookList):
    processed_data = []
    badDDCChars = '#*()+,[]/!- S'
    badLCCChars = '*()+,[]/!- '
    for book in bookList:
        # working under assumption that we use the first classification number
        if book['ddc'] is not None:
            ddc = book['ddc'][0]
            for char in badDDCChars:
                ddc = ddc.replace(char, '').upper()
            book['ddc'] = ddc
        if book['lcc'] is not None:
            lcc = book['lcc'][0]
            for char in badLCCChars:
                lcc = lcc.replace(char, '').upper()
            book['lcc'] = lcc
        processed_data.append(book)
    return processed_data

'''
Regularize dates from MARC records
'''
def format_date(dateStr):
    if type(dateStr) == int:
        return dateStr
    xxxx  = r'\d\d\d\d'
    dateStr = dateStr.lower()
    if 'n.d.' in dateStr: #no date
        date = None 
    elif re.search(r'c\d\d\d\d|c \d\d\d\d', dateStr):
        # ASSUMPTION: use the earliest date in a range of dates 
        date = min([int(d[1:]) for d in re.findall(r'c\d\d\d\d|c \d\d\d\d', dateStr)])
    elif re.search(r'c\.\d\d\d\d', dateStr):
        date = min([int(d[2:]) for d in re.findall(r'c\.\d\d\d\d', dateStr)])
    elif re.search(r'c\d\d\dl', dateStr):
        date = min([int(d[1:].replace('l', '1')) for d in re.findall(r'c\d\d\dl', dateStr)])
    elif re.search(r'\dc\d\d\d', dateStr):
        date = min([int(d.replace('c', '')) for d in re.findall(r'\dc\d\d\d', dateStr)])
    elif re.search(r'c9\d\d|c8\d\d', dateStr):
        date = min([int(d.replace('c', '1')) for d in re.findall(r'c9\d\d|c8\d\d', dateStr)])
    elif re.search(xxxx, dateStr) and 'c' not in dateStr and not re.search(r'^\d\d\d |^ \d\d\d |^\d\d\d\[', dateStr):
        date = min([int(d) for d in re.findall(xxxx, dateStr)])
    else:
        date = None
    return date

'''
Regularize titles from MARC records
'''
def format_title(title):
    if ' /' in title:
        spaceSlash = title.index(' /')
        title = title[:spaceSlash]
    title = title.strip()
    return title.lower()

'''
Regularize names from MARC records
'''
def format_name(name):
    #strip leading and trailing whitespace
    name = name.strip()
    # strip trailing punctuation
    name = name.rstrip('.,_-()')
    # remove remaning periods
    name = name.replace('.', '')
    # remove square brackets
    name = name.replace('[', '').replace(']', '')
    #remove dates
    name = re.sub(',?( d|,d)? ?\d{4} ?-? ?\d{,4}', '', name)
    #remove trailing numbers
    name = re.sub('\d*$| \d*$', '', name)
    #deal with brackets 
    name = re.sub(' ?\([^)]*\)?', '', name)   
    #final strip
    name = name.strip()
    return name.lower()
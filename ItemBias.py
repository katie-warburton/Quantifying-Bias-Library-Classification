import numpy as np
import scipy
import random

'''
Functions to aid in the analyses of item gender bias in the LCC and DDC. 
It is assumed that the nodes and trees being examined are LibraryTree objects. 
'''

'''
Calculate the percentage of books by men and books by women 
at a given node and its children.
'''
def get_prop_fm(node):
    if node.item_count > 0:
        authGens = [book['auth_gen'] for book in node.items]
        node.prop_m = authGens.count('male') / node.item_count
        node.prop_f = authGens.count('female') / node.item_count
    for child in node.children.values():
        if child is not None:
            get_prop_fm(child)

'''
Determine the percentage of books by men and women at each
category in a classification system.
'''
def tag_tree_fm(tree):
    get_prop_fm(tree.root)

'''
Tag a book with its authors gender.
'''
def tag_books_fm(books, genLookup):
    for book in books:
        book['auth_gen'] = genLookup[book['oclc']]

'''
CIRCULATION

Get circulation statistics for books in a library classification
system that are by an author of gender 'gen' (gender is coded as 'male', 
'female', 'unknown', or 'ambiguous' based on tagging conventions from
VIAF author records and Ekstrand & Kluver (2021).)
'''
def get_circ_stats(tree, gen):
    annual_circ = 0
    in_circ = 0
    annual_in_circ = 0
    total = 0
    for item in tree.root.items:
        if item['auth_gen'] == gen:
            annual_circ += item['total_circ']
            if item['total_circ'] > 0:
                annual_in_circ += 1
            if item['circ_status'] > 0:
                in_circ += 1
            total += 1
    return total, in_circ, annual_in_circ, annual_circ

'''
LEVEL BIAS

Permutation test to determine the significance of the difference
between the average depth of books by women and books by men 
in a library classification system.
'''
def level_perm_test1(levels, split, expDiff, perms):
    p_val = 0
    for i in range(perms):
        np.random.shuffle(levels)
        fLevels = levels[:split]
        mLevels = levels[split:]
        actualDiff = abs(np.mean(fLevels) - np.mean(mLevels))
        if actualDiff >= expDiff:
            p_val += 1
    return p_val / perms

'''
Count the probability that a randomly selected book written by a women
is categorized deeper in the category system than a book by a man
'''
def prob_non_west_deeper(fLevels, mLevels, perms):
    deeperF, deeperM = 0, 0
    for _ in range(perms):
        fDepth = random.choice(fLevels)
        mDepth = random.choice(mLevels)
        if fDepth > mDepth:
            deeperF += 1
        if mDepth > fDepth:
            deeperM += 1 
    return deeperF / (deeperF+deeperM)

'''
Permutation test to compute the significance of the probability
that a book by a women is categorized deeper in a library
classification system than a book by a man.
'''
def level_perm_test2(levels, split, expVal, perms):
    p_val = 0
    expDiff = abs(expVal - 0.50)
    for _ in range(perms):
        np.random.shuffle(levels)
        fLevels = levels[:split]
        mLevels = levels[split:]
        deeperF = prob_non_west_deeper(fLevels, mLevels, 10000)
        actualDiff = abs(deeperF - 0.50)
        if actualDiff >= expDiff:
            p_val += 1
    return p_val / perms


'''
DISTRIBUTIONAL BIAS

Compute the distribution of books by women and books by men
across the subcategories of a node.
'''
def get_fm_dist(root):
    dist_f, dist_m = [], []
    sum_f, sum_m = 0, 0
    for child in root.children.values():
        if child is not None:
            num_f = int(child.item_count * child.prop_f)
            num_m = int(child.item_count * child.prop_m)
            dist_f.append(num_f)
            dist_m.append(num_m)
            sum_f +=  num_f
            sum_m += num_m
    for i in range(len(dist_f)):
        if sum_f != 0:
            dist_f[i] = dist_f[i] / sum_f
        if sum_m != 0:
            dist_m[i] =  dist_m[i] / sum_m
    return dist_f, dist_m, sum_f, sum_m

'''
Collect all nodes with at least minItems books and at least
minKids children. 
'''
def nodes_with_constraints(tree, minItems, minKids):
    nodes = []
    check_node(tree.root, minItems, minKids, nodes)
    # not counting the root in this analyses
    return nodes[1:]

'''
Helper function for nodes_with_constraints
'''
def check_node(node, minItems, minKids, nodeList):
    num_children = node.count_children()
    if node.item_count >= minItems and num_children >= minKids: 
        nodeList.append(node)
    for kid in node.children.values():
        if kid is not None:
            check_node(kid, minItems, minKids, nodeList)

'''
Code to determine the number of times the distribution of books by women
across the subcategories of a node is flatter than the distribution of books by men, 
the number of times the distribution of men is flatter, and the number of times they 
are equally as flat. Assumes that all nodes in the list of nodes have at least 
2 children.
'''
def calc_dist_bias(validNodes):
    flatter = [0, 0]
    for node in validNodes:
        dist_f, dist_m, _, _ = get_fm_dist(node)
        #ensure there is some number of male and female authors at each node
        if sum(dist_f)> 0 and sum(dist_m) > 0: 
            ent_f = scipy.stats.entropy(dist_f, base=2)
            ent_m = scipy.stats.entropy(dist_m, base=2)
            if ent_f < ent_m:
                flatter[0] += 1
            elif ent_f > ent_m:
                flatter[1] += 1
            else:
                flatter[0] += 0.5
                flatter[1] += 0.5                 
    return flatter

'''
Collect the differences in distributions of books by men versus books
by women for all nodes in a list of nodes. 
'''
def calc_diff_in_dist(validNodes):
    data = []
    for node in validNodes:
        dist_f, dist_m, _, _ = get_fm_dist(node)
        if sum(dist_f) == 0:
            ent_f = 0
        else:
            ent_f = scipy.stats.entropy(dist_f, base=2)
        if sum(dist_m) == 0:
            ent_m = 0
        else:
            ent_m = scipy.stats.entropy(dist_m, base=2)
        
        diff = ent_m - ent_f
        data.append((diff, node))
    return data


'''
Collect all nodes with less than maxItems
'''
def get_min_items(tree, maxItems):
    validNodes = []
    nodes_with_items(tree.root, validNodes, maxItems)
    return len(validNodes)

'''
Helper function for get_min_items
'''
def nodes_with_items(node, nodes, max_items):
    if node.item_count < max_items:
        nodes.append(node)
    for kid in node.children.values():
        if kid is not None:
            nodes_with_items(kid, nodes, max_items)

'''
Collect all nodes with less than maxKids
'''
def get_min_kids(tree, maxKids):
    validNodes = []
    nodes_with_kids(tree.root, validNodes, maxKids)
    return len(validNodes)

'''
Helper function for get_min_kids
'''
def nodes_with_kids(node, validNodes, max_kids):
    num_kids = node.count_children()
    if num_kids < max_kids:
        validNodes.append(node)
    for kid in node.children.values():
        if kid is not None:
            nodes_with_kids(kid, validNodes, max_kids)

'''
Collect all nodes with books by men but not women. 
'''
def nodes_without_women(tree):
    validNodes = []
    no_women(tree.root, validNodes)
    return len(validNodes)

'''
Helper function for nodes_without_women
'''
def no_women(node, validNodes):
    if node.item_count > 0 and node.prop_f == 0 and node.prop_m != 0:
        validNodes.append(node)
    for kid in node.children.values():
        if kid is not None:
            no_women(kid, validNodes)

'''
Collect all nodes with books by women but not men.
'''
def nodes_without_men(tree):
    validNodes = []
    no_men(tree.root, validNodes)
    return len(validNodes) 

'''
Helper function for nodes_without_men.
'''
def no_men(node, validNodes):
    if node.item_count > 0 and node.prop_m == 0 and node.prop_f != 0:
        validNodes.append(node)
    for kid in node.children.values():
        if kid is not None:
            no_men(kid, validNodes)





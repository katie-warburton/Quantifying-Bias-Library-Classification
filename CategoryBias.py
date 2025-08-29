
import random
import statistics as stats
import numpy as np
from scipy.spatial.distance import jensenshannon

'''
Functions to aid in the analyses of western category bias in the LCC and DDC. 
It is assumed that the nodes and trees being examined are LibraryTree objects. 
'''

'''
Compute the total number of categories (descendants and all) in 
a list of starting nodes.
'''
def get_total_nodes(categories):
    count = 0
    for cat in categories:
        count += cat.count_nodes()
    return count

'''
COUNT BIAS

Functions to compute the mean, median and mode percentage of items per node.
'''
def avg_items_per_node(nodes):
    # Sum up the items in the starting nodes to get the total number of items
    total_items = sum([node['num_items'] for node in nodes if node['parent'] is None 
                    or node['parent'].west is None])

    items_per_node = [node['num_items']/total_items for node in nodes]
    return stats.mean(items_per_node)

def median_items_per_node(nodes):
    total_items = sum([node['num_items'] for node in nodes if node['parent'] is None 
                    or node['parent'].west is None])

    items_per_node = [node['num_items']/total_items for node in nodes]
    return stats.median(items_per_node)

def mode_items_per_node(nodes):
    total_items = sum([node['num_items'] for node in nodes if node['parent'] is None 
                    or node['parent'].west is None])

    items_per_node = [node['num_items']/total_items for node in nodes]
    return stats.mode(items_per_node)

'''
Permutation test to determine how likely the discrepancy between western
and non-western categories is the result of chance.
'''
def category_perm_test(w_count, nw_count, permutations):
    i, p_val = 0, 0
    total = w_count + nw_count
    diff = abs(w_count - nw_count)
    while i < permutations:
        random_w, random_nw, j = 0, 0, 0
        while j < total:
            # assign nodes a western or non-western label with 
            # uniform probability 
            label = random.randint(0, 1)
            if label == 0:
                random_nw += 1
            else:
                random_w += 1
            j += 1
        if abs(random_w - random_nw) >= diff:
            p_val += 1
        i += 1
    return p_val / permutations


'''
LEVEL BIAS

Compute the average depth of a list of western and non-western categories
''' 
def level_bias1(west, nonwest):
    w_levels = get_level_dist(west)
    nw_levels = get_level_dist(nonwest)
    avg_w = stats.mean(w_levels)
    avg_nw = stats.mean(nw_levels)
    return avg_w, avg_nw

'''
Collect the starting depths from a list of categories
'''
def get_level_dist(nodes):
    starting_nodes = [node for node in nodes if node['parent'] is None 
                      or node['parent'].west is None]
    levels = []
    for node in starting_nodes:
        levels.append(node['depth'])
    return levels

'''
Compute the Jensen-Shannon divergence between a distribution of western
cateogries over classification system depths and non-western categories.  
'''
def get_jsd(w_levels, nw_levels):
    level_set = list(set(w_levels+nw_levels))
    w_dist = [w_levels.count(lev)/len(w_levels) for lev in level_set]
    nw_dist = [nw_levels.count(lev)/len(nw_levels) for lev in level_set]
    return jensenshannon(w_dist, nw_dist)**2
    
'''
Permutation test to determine how likely it is that the attested JSD 
between the disttributions of western and non-western category depths 
is the result of chance.
'''
def level_perm_test1(levels, nw_start, exp_jsd, perms):
    p_val = 0
    for _ in range(perms):
        np.random.shuffle(levels)
        w_levels = levels[:nw_start]
        nw_levels = levels[nw_start:]
        jsd = get_jsd(w_levels, nw_levels)
        if jsd >= exp_jsd:
            p_val += 1
    return p_val/ perms


'''
Function to compute statistics relevant to category level bias. Determines
the probability that a non-western node is deeper in a category system than 
a western one and the significance of this probability. 
'''
def level_bias2(west, nonwest, permTest=False, perms=0):
    starting_w = [node['depth'] for node in west if node['parent'] is None 
                        or node['parent'].west is None]
    starting_nw = [node['depth'] for node in nonwest if node['parent'] is None 
                        or node['parent'].west is None]
    prob_nw = prob_non_west_deeper(starting_w, starting_nw, 10000)    
    if permTest:
        p_val = level_perm_test2(starting_w + starting_nw, len(starting_w), prob_nw, perms)
        return prob_nw, p_val
    else:
        return prob_nw, None

'''
Permutation test to determine if the probability of a non-western
category node being deeper in the classification system than a 
western category system is significant. 
'''
def level_perm_test2(levels, nw_start, exp_prob, perms):
    exp_diff = abs(exp_prob - 0.50)
    p_val = 0
    for _ in range(perms):
        np.random.shuffle(levels)
        w_levels = levels[:nw_start]
        nw_levels = levels[nw_start:]
        # can do more than 100 -- less is better for demonstration purposes
        nw_deeper = prob_non_west_deeper(w_levels, nw_levels, 10000)
        if abs(nw_deeper - 0.50) >= exp_diff:
            p_val += 1
    return p_val / perms

'''
Count the number of times that for a pair of randomly selected western
and non-western categories, the two categorues are at the same depth, 
the western category is deeper, or the non-western category is deeper.
'''
def compare_depths(w_dat, nw_dat, n):
    same, nw_deeper, w_deeper, i = 0, 0, 0, 0
    while i < n:
        w_lev = random.choice(w_dat)
        nw_lev = random.choice(nw_dat)
        if nw_lev == w_lev:
            same += 1
        elif nw_lev > w_lev:
            nw_deeper += 1
        else:
            w_deeper += 1
        i += 1
    return nw_deeper, w_deeper, same

'''
Compute the probability that a randomly selected non-western category
is deeper in a classification system then a randomly selected western
category. 
'''
def prob_non_west_deeper(w_dat, nw_dat, n):
    nw_deeper, w_deeper, _ = compare_depths(w_dat, nw_dat, n)
    return nw_deeper / (nw_deeper+w_deeper)

'''
DESCENDANT BIAS

Functions to compute the mean, median, and mode percentage of items per
starting node. 
'''
def mean_items_per_start(nodes):
    start_items = [node['num_items'] for node in nodes if node['parent']
                       is None or node['parent'].west is None]
    total_items = sum(start_items)
    items_per_start = [count/total_items for count in start_items]
    return stats.mean(items_per_start)

def median_items_per_start(nodes):
    start_items = [node['num_items'] for node in nodes if node['parent']
                       is None or node['parent'].west is None]
    total_items = sum(start_items)
    items_per_start = [count/total_items for count in start_items]
    return stats.median(items_per_start)

def mode_items_per_start(nodes):
    start_items = [node['num_items'] for node in nodes if node['parent']
                       is None or node['parent'].west is None]
    total_items = sum(start_items)
    items_per_start = [count/total_items for count in start_items]
    return stats.mode(items_per_start)

'''
Compute the mean number of descendants per starting node. 
'''
def avg_descendants(nodes):
    start_nodes = [node['num_desc'] for node in nodes if node['parent']
                       is None or node['parent'].west is None]
    return stats.mean(start_nodes), len(start_nodes)

'''
Permutation test to determine the significance of the difference between
the mean number of descendants per western node and the mean number of
descendants per non-western node.
'''
def desc_perm_test(w_nodes, nw_nodes, perms):
    w_kids = [node['num_desc'] for node in w_nodes if node['parent']
                       is None or node['parent'].west is None]
    nw_kids = [node['num_desc'] for node in nw_nodes if node['parent']
                       is None or node['parent'].west is None]
    observed_diff = abs(stats.mean(w_kids) - stats.mean(nw_kids))
    kid_counts = w_kids + nw_kids
    num_w = len(w_kids)
    p_val, i = 0, 0
    while i < perms:
        np.random.shuffle(kid_counts)
        w_kids_i = kid_counts[:num_w]
        nw_kids_i = kid_counts[num_w:]
        diff_i = abs(stats.mean(w_kids_i) - stats.mean(nw_kids_i))
        if diff_i >= observed_diff:
            p_val += 1
        i += 1
    return p_val / perms

'''
CIRCULATION

For a given set of nodes, compute the percentage of books in circulation,
the percentgae of circulaitng books taken out, and the rate of circulation 
for the books taken out. 
'''
def get_anual_circ(nodeList):
    total = 0
    num_items = 0
    num_in_circ = 0
    circ_year = 0
    for node in nodeList:
        if node['parent'] is None or node['parent'].west is None:
            for item in node['items']:
                # total number of times books have been circulated
                total += item['total_circ']
                num_items += 1
                # Number of books in circulation
                if item['circ_status'] > 0:
                    num_in_circ += 1
                # Number of books that circulated in a year
                if item['total_circ'] > 0:
                    circ_year += 1
    percent_circ = num_in_circ/num_items # percentage of books in circulation
    taken_out = circ_year/num_in_circ # percentage of circulating books taken out
    circ_rate = total/circ_year # rate of circulation for circulating books
    return num_items, percent_circ, taken_out, circ_rate
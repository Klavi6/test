import math
import random
from sklearn.neighbors import KDTree as kdt
import numpy as np

rng = np.random.default_rng()

def distance(a, b, c, d):
    #return 0.959961 * max((abs(c - a), abs(d - b))) + 0.397461 * min((abs(c - a), abs(d - b)))
    a = c-a
    b = d-b
    return math.sqrt(a**2 + b**2)

# Initial connections using k-d tree
def kdtree(clients, base_stations):

    c_coor = [(c.x,c.y) for c in clients]
    bs_coor = [p.coverage.center for p in base_stations]

    tree = KDTree(bs_coor, leaf_size=2)
    res = tree.query(c_coor)

    for c, d, p in zip(clients, res[0], res[1]):
        if d[0] <= base_stations[p[0]].coverage.radius:
            c.base_station = base_stations[p[0]]

class KDTree:
    last_run_time = 0
    limit = None

    # Initial connections using k-d tree
    @staticmethod
    def run(clients, base_stations, run_at, assign=True):
        #with open("output_text.txt","a+") as f:
        #    f.write("\n"f'KDTREE CALL [{run_at}] - limit: {KDTree.limit}')
        if run_at == KDTree.last_run_time:
            return
        KDTree.last_run_time = run_at
        
        c_coor = [(c.x,c.y) for c in clients]
        bs_coor = [p.coverage.center for p in base_stations]

        tree = kdt(bs_coor, leaf_size=2)
        res = tree.query(c_coor,k=min(KDTree.limit,len(base_stations)))

        #with open("output_text.txt","a+") as f:
        #    f.write("\n"f'{res[0]}')
        for c, d, p in zip(clients, res[0], res[1]):
            if assign and d[0] <= base_stations[p[0]].coverage.radius:
                c.base_station = base_stations[p[0]]    
            c.closest_base_stations = [(a, base_stations[b]) for a,b in zip(d,p)]


def format_bps(size, pos=None, return_float=False):
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
    power, n = 1000, 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T', 5: 'P', 6:'E', 7: 'Z', 8:'Y'}
    while size >= power:
        size /= power
        n += 1
    if return_float:
        return f'{size:.3f} {power_labels[n]}bps'
    return f'{size:.0f} {power_labels[n]}bps'

def get_dist(d):
    return {
        'randrange': random.randrange, # start, stop, step
        'randint': random.randint, # a, b
        'random': random.random,
        'uniform': random.uniform, # a, b
        'triangular': random.triangular, # low, high, mode
        'beta': random.betavariate, # alpha, beta
        'expo': random.expovariate, # lambda
        'gamma': random.gammavariate, # alpha, beta
        'gauss': random.gauss, # mu, sigma
        'lognorm': random.lognormvariate, # mu, sigma
        'normal': random.normalvariate, # mu, sigma
        'vonmises': random.vonmisesvariate, # mu, kappa
        'pareto': random.paretovariate, # alpha
        'weibull': random.weibullvariate, # alpha, beta
        "np_uniform": rng.uniform
    }.get(d)

def get_random_mobility_pattern(vals, mobility_patterns):
    i = 0
    #r = random.random()
    r = rng.random()

    while vals[i] < r:
        i += 1

    return mobility_patterns[i]

def get_random_slice_index(slice_weights, slice_quantity):
    i = 0
    #r = random.random()
    r = rng.random()

    while slice_weights[i] < r:
        i += 1
    #j = random.randrange(slice_quantity[i])
    j = rng.integers(slice_quantity[i])
    for k in range(i):
        j += slice_quantity[k]
    return j
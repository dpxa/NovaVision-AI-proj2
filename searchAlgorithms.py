import threading
import random
from TSPHelper import TSPHelper
from math import ceil
import numpy as np
    
def search(helper: TSPHelper, stop_event: threading.Event, alg_num: int):
    if (alg_num == 0):
        print("\tUsing random_search")
        return random_search(helper, stop_event)
    elif (alg_num == 1) :
        print("\tUsing NN_epsilon_search")
        return NN_epsilon_search(helper, stop_event)
    else:
        print("\tUsing NN_2opt_decay_search")
        return NN_2opt_decay_search(helper, stop_event)
    
def flip_best_path():
    global best_path

    idx = best_path.index(0)
    best_path = best_path[idx:] + best_path[:idx]
    best_path.append(best_path[0])
    
def random_search(helper: TSPHelper, stop_event: threading.Event):
    global best_path
    global min_dist
    
    best_path = []
    min_dist = float('inf')
    
    while not stop_event.is_set():
        currentPath = list(range(0, helper.num_points))
        random.shuffle(currentPath)
        currentPath.append(currentPath[0])
        
        dist = 0
        for i in range(len(currentPath) - 1):
            dist += helper.lookup_table[currentPath[i]][currentPath[i + 1]]
        currentPath.pop()
        
        if (dist < min_dist):
            min_dist = dist
            best_path = currentPath
            print(f"\t\t{min_dist}")
            
    flip_best_path()
    
    return best_path, ceil(min_dist)

def NN_2opt_decay_search (helper: TSPHelper, stop_event: threading.Event):
    global best_path
    global min_dist
    
    best_path = []
    min_dist = float('inf')
    
    if not stop_event.is_set():
        nearest_neighbor(helper, 0.0, True)

    while not stop_event.is_set():
        nearest_neighbor(helper, 0.12, True)
        
    flip_best_path()

    return best_path, ceil(min_dist)

def NN_epsilon_search(helper: TSPHelper, stop_event: threading.Event):
    global best_path
    global min_dist

    best_path = []
    min_dist = float('inf')

    if not stop_event.is_set():
        nearest_neighbor(helper, 0.0)

    while not stop_event.is_set():
        nearest_neighbor(helper, 0.05)
        
    flip_best_path()

    return best_path, ceil(min_dist)


def nearest_neighbor(helper, epsilon, twopt = False):
    global best_path
    global min_dist

    points = set(range(0, helper.num_points))
    initialPoint = random.choice(list(points))
    currentPath = [initialPoint]
    points.remove(initialPoint)

    dist = 0

    while points:
        bestMatchVal = float('inf')
        bestMatchPoint = None
        if epsilon > random.random():
            bestMatchPoint = random.choice(list(points))
            bestMatchVal = helper.lookup_table[currentPath[-1]][bestMatchPoint]
        else:
            for point in points:
                d = helper.lookup_table[currentPath[-1]][point]
                if d < bestMatchVal:
                    bestMatchVal = d
                    bestMatchPoint = point
        
        dist += bestMatchVal
        
        if twopt:
            epsilon *= 0.9
        elif dist >= min_dist:
            return
        
        currentPath.append(bestMatchPoint)
        points.remove(bestMatchPoint)

    total_dist = dist + helper.lookup_table[currentPath[-1]][currentPath[0]]
    
    if twopt:
        currentPath.append(currentPath[0])
        currentPath, total_dist = Two_opt(helper, currentPath, total_dist)
        currentPath.pop()

    if total_dist < min_dist:
        min_dist = total_dist
        best_path = currentPath
        print(f"\t\t{min_dist}")
        return
    
def Two_opt(helper, path, dist):
    improve = True
    lookup = np.array(helper.lookup_table)

    while improve:
        improve = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                edge_AB = lookup[path[i - 1]][path[i]]
                edge_CD = lookup[path[j]][path[j + 1]]
                
                edge_AC = lookup[path[i - 1]][path[j]]
                edge_BD = lookup[path[i]][path[j + 1]]
                
                if (edge_AC + edge_BD) < (edge_AB + edge_CD):
                    path[i:j + 1] = reversed(path[i:j + 1])
                    dist += (edge_AC + edge_BD) - (edge_AB + edge_CD)
                    improve = True
                    break
            if improve:
                break

    return path, dist

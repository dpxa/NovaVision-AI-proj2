import random
from TSPHelper import TSPHelper
from math import ceil, sqrt
import numpy as np
import tempfile, os
    
def flip_best_path():
    global best_path

    idx = best_path.index(0)
    best_path = best_path[idx:] + best_path[:idx]
    best_path.append(best_path[0])

def NN_2opt_decay_search(helper: TSPHelper):
    global best_path
    global min_dist

    best_path = []
    min_dist = float('inf')

    nearest_neighbor(helper, 0.0, True)

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
            bestMatchVal = helper.lookup_table[currentPath[-1], bestMatchPoint]
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

    total_dist = dist + helper.lookup_table[currentPath[-1], currentPath[0]]
    
    if twopt:
        currentPath.append(currentPath[0])
        currentPath, total_dist = Two_opt(helper, currentPath, total_dist)
        currentPath.pop()

    if total_dist < min_dist:
        min_dist = total_dist
        best_path = currentPath
        return

def Two_opt(helper, path, dist):
    improve = True
    iterations = 0
    max_iterations = 100
    
    while improve and iterations < max_iterations:
        improve = False
        iterations += 1
        
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                edge_AB = helper.lookup_table[path[i - 1], path[i]]
                edge_CD = helper.lookup_table[path[j], path[j + 1]]

                edge_AC = helper.lookup_table[path[i - 1], path[j]]
                edge_BD = helper.lookup_table[path[i], path[j + 1]]
                
                if (edge_AC + edge_BD) < (edge_AB + edge_CD):
                    # slicing instead of iterator
                    path[i:j + 1] = path[i:j + 1][::-1]
                    dist += (edge_AC + edge_BD) - (edge_AB + edge_CD)
                    improve = True
                    break
            if improve:
                break

    return path, dist


# Create temp file to TSPHelper can be instantiated
def initializeWithTemp(helper, centroid, clusterCoors):
    file = tempfile.NamedTemporaryFile(mode="w+",delete=False)

    file.write(f"{centroid[0]} {centroid[1]}\n")
    for c in clusterCoors:
        xCoor = helper.data[c, 0]
        yCoor = helper.data[c, 1]
        file.write(f"{xCoor} {yCoor}\n")
    file.close()
    
    coordFileVal = TSPHelper(file.name)
    os.remove(file.name)

    return coordFileVal

#updating the k means now
def callKMeans(helper):
    # Stores each k value and drone info
    results = {}

    for k in range(1, 5):
        # sum of squared distances
        bestSek = float('inf')
        bestClusters = []
        bestCentroids = []
        
        # Repeat KMeans 10 times for each k value
        for _ in range(10):
            clusters, centroids, sek = KMeans(helper, k)
            if sek < bestSek:
                bestSek = sek
                bestClusters = clusters
                bestCentroids = centroids
            
        # to store cluster results
        finalClusterVal = []
        # looping through cluster
        for i, cluster in enumerate(bestClusters):
            if len(cluster) == 0:
                continue

            tempFileFunc = initializeWithTemp(helper, bestCentroids[i], cluster)
            path, dist = NN_2opt_decay_search(tempFileFunc)
            
            adj_path = [cluster[idx - 1] for idx in path[1:-1]]

            # storing the drone info
            finalClusterVal.append({
                "drone": i + 1,
                "centroid": bestCentroids[i],
                "path": adj_path,
                "distance": dist
              })

        results[k] = finalClusterVal
    return results

def KMeans(helper,K=4):
    points = list(range(helper.num_points))

    centroids = []
    for _ in range(K):
        centroids.append([random.uniform(helper.min_x, helper.max_x), random.uniform(helper.min_y, helper.max_y)])

    clusters = []
    max_iterations = 50

    for _ in range(max_iterations):
        # need k empty cluster lists
        clusters = [[] for _ in range(K)]
        for i in range(len(points)):
            point = points[i]
            closestIndex = 0
            minDist = float('inf')
            for j in range(K):
                d = sqrt((helper.data[point, 0] - centroids[j][0]) ** 2 + (helper.data[point, 1] - centroids[j][1]) ** 2)
                if d < minDist:
                    minDist = d
                    closestIndex = j
            clusters[closestIndex].append(point)

        newCentroids = []

        for cluster in clusters:
            if len(cluster) != 0:
                xMean = np.mean(helper.data[cluster, 0])
                yMean = np.mean(helper.data[cluster, 1])

                newCentroids.append([xMean, yMean])
            else:
                # randomly reinitialize centroid
                newCentroids.append([random.uniform(helper.min_x, helper.max_x), random.uniform(helper.min_y, helper.max_y)])
                
        converged = True
        for j in range(len(newCentroids)):
            if abs(newCentroids[j][0] - centroids[j][0]) > 0.01 or abs(newCentroids[j][1] - centroids[j][1]) > 0.01:
                converged = False
                break
                
        if converged:
            break
        else:
            centroids = newCentroids

    # calculating objective function (sum of squared distances)
    total_sek = 0
    for i in range(K):
        cluster_sek = 0
            
        if not clusters[i]:
            continue
        for point in clusters[i]:
            cluster_sek += sqrt((helper.data[point, 0] - centroids[i][0]) ** 2 + (helper.data[point, 1] - centroids[i][1]) ** 2) ** 2

        total_sek += cluster_sek
                                                                  
    return clusters, centroids, total_sek

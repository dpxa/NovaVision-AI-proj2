import threading
import random
from TSPHelper import TSPHelper
from math import ceil
import numpy as np
import tempfile, os
def search(helper: TSPHelper, stop_event: threading.Event, alg_num: int):
    if (alg_num == 0):
        print("\tUsing random_search")
        return random_search(helper, stop_event)
    elif (alg_num == 1) :
        print("\tUsing NN_epsilon_search")
        return NN_epsilon_search(helper, stop_event)
    elif (alg_num == 2):
        print("\tUsing KMeans algorithm")
        return callKMeans(helper)
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

def NN_2opt_decay_search (helper: TSPHelper):
    global best_path
    global min_dist

    best_path = []
    min_dist = float('inf')


    nearest_neighbor(helper, 0.0, False) #fast nearest neighbour

    #if cluster small
    n = helper.num_points
    if n <= 400:
        #do teh 2opt
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


# helper function which has mini files for each drone coordiantes

def helperFunction1(helper, clusterCoors):
    file = tempfile.NamedTemporaryFile(mode="w+",delete=False)
    for c in clusterCoors:
        xCoor, yCoor = helper.data[c]
        file.write(f"{xCoor} {yCoor}\n") # (x y) coordinates in temporary file
    file.close()
    #storing the temporary file data
    coordFileVal = TSPHelper(file.name)
    #deleting the temporary file

    os.remove(file.name)
    return coordFileVal

#updating the k means now
def callKMeans(helper):
    results = {} #storing each k value and each drone info in dictionary

    for k in range(1, 5):
        print(f"\n K means algorithm with K = {k}")
        # run 10 time for each k value and get the best result
        bestSek = float('inf')
        bestClusters = []
        bestCentroids = []
        for i in range(10):
            clusters, centroids, sek= KMeans(helper, k) #calling the k means algorithm
            if sek < bestSek:
                bestSek = sek
                bestClusters = clusters
                bestCentroids = centroids
            
        print(f"\n Best SEK for K={k} is {round(bestSek,2)}")   
            
        #to store cluster results
        finalClusterVal = []
        #looping through cluster
        for j, cluster in enumerate(bestClusters):
            #check for cluster empty or not (if empty skip)
            if len(cluster) == 0:
                continue #skip this cluster

            # intial centroaid point
            centroid_value = bestCentroids[j]
            
            # create a list of the landing pad coordinates
            cluster_coords = [centroid_value]
            for p in cluster:
                if p != centroid_value:
                    cluster_coords.append(p)

            print(f"Drone {j+1}: {len(cluster)}") #how many points the drone should visit

            
            #the temporary file function
            tempFileFunc = helperFunction1(helper, cluster_coords)
            #calling the best search algorithm for each drone and its cluster
            #getting the best path and distance for that path
            path, dist = NN_2opt_decay_search(tempFileFunc)
            
            # adjusting the path to match original indices
            adjusted_path = [cluster_coords[i] for i in path[:-1]] #excluding the last point which is return to start

            #getting the final results of each drone for each k mean alg
            finalClusterVal.append({"drone": j+1,"centroid":centroids[j], "path": adjusted_path, "distance": dist}) #things to have drone no., centroid, path, dist

        #appending it to the final results dictionary
        results[k] = finalClusterVal
        results[k].append({"Sek_Score": bestSek}) #adding the sek value for each k
    return results

def KMeans(helper,K=4):
    points = list(range(helper.num_points))
    centroids = random.sample(points,K)
    converge = False
    final_clusters = []
    while converge == False:
        #need k empty lists n
        clusters = [[] for i in range(K)]
        for i in range(len(points)):
            point = points[i]
            closestIndex = 0
            minDist = float('inf') #changing to infinity to update it later
            for j in range(K):
                d = helper.lookup_table[point][centroids[j]]
                if d < minDist:
                    minDist = d
                    closestIndex = j
            clusters[closestIndex].append(point)

        newCentroids = [] #calculating the new centroids now

        for cluster in clusters:
            if len(cluster) != 0:
                #calculating the mean for x coordinates and y coordinates for centroids
                x_y_coordinates = np.array([helper.data[i] for i in cluster])
                #x coodinates mean
                xMean = np.mean(x_y_coordinates[:, 0])

                #y coor mean
                yMean = np.mean(x_y_coordinates[:, 1])

                #the point closest to the mean coor as the new centroid
                #distance formula sqrt(x2 -x1)^2 +( y2 -y1)^2)
                closeCoor = min(cluster, key=lambda x: ((helper.data[x][0] - xMean)** 2 + (helper.data[x][1] - yMean)** 2))

                newCentroids.append(closeCoor) #new centroid coordinates
            else: #if empty
                newCentroids.append(random.choice(points)) #random centroids
                
        if newCentroids == centroids:
            converge = True
            final_clusters = clusters
        else:
            centroids = newCentroids
            
    # calculating Objective function (sum of squared distances)
    total_sek = 0
    for i in range(K):
        cluster_sek = 0
            
        # check if the cluster is not empty
        if not final_clusters[i]:
            continue
        for point in final_clusters[i]:
            distance_to_centroid = helper.lookup_table[point][centroids[i]]
            cluster_sek += distance_to_centroid ** 2
        total_sek += cluster_sek
                                                                  

    #returning clusters and centroids
    return final_clusters, centroids, total_sek


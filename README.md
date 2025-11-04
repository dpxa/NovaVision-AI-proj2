# NovaVision AI Repo for Project 1
## Overview
## Tool
* Python
* Terminal base

## Plan and Process
### method 
1. Read coordinates in from file
2. Create 2D lookup matrix of euclidian distances
3. Calculate the total distance for the path. 

### randomSearch
1. create empty current_path, best_path, min_distance
2. Loop until "Enter key" hit. 
3. In the loop, use random.shuffle and calculate the current_dist from path_distance from helper function. then check if the current_dist is the smallest so far. 
4. return min_dist and best_path

## Reference 
* Random shuffle: https://www.geeksforgeeks.org/python/random-shuffle-function-in-python/
* Enter press to stop : https://docs.python.org/3/library/threading.html and https://www.instructables.com/Starting-and-Stopping-Python-Threads-With-Events-i/ 
* KNN Algorithm: https://www.geeksforgeeks.org/machine-learning/k-nearest-neighbours/
* Nearest Neighbour Algorithm: https://en.wikipedia.org/wiki/Nearest_neighbour_algorithm
* Slide 34 from AnyTime Algorithms Psuedocode by Dr.Keogh
* 2-opt : https://en.wikipedia.org/wiki/2-opt
* KMeans Psuedocode:https://en.wikipedia.org/wiki/K-means_clustering
* generating random values in a list: https://stackoverflow.com/questions/16655089/python-random-numbers-into-a-list

from TSPHelper import TSPHelper
import searchAlgorithms
import threading
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def _worker(helper, res, ex):
    try:
        res[0] = searchAlgorithms.callKMeans(helper)
    except Exception as e:
        ex[0] = e

# Time KMeans out after X seconds
def callKMeans_timeout(helper, seconds=300):
    # arrays becuase result needs to be passed by reference
    res = [None]
    ex = [None]
    
    thread = threading.Thread(target=_worker, args=(helper, res, ex))
    thread.daemon = True
    thread.start()
    thread.join(seconds)
    
    if thread.is_alive:
        print("KMeans is still running")
        thread.join()
    
    # so we can see if there was an exception
    if ex[0]:
        raise ex[0]

    return res[0]
    

def image_gen(fileName, helper, clusters, directory):
    listColour = ["blue", "green", "red", "purple"]

    plt.figure(figsize=(15, 15))

    for i, cluster in enumerate(clusters):
        x_y_coordinates = [cluster["centroid"]]
        for idx in cluster["path"][1:-1]:
            x_y_coordinates.append(helper.data[idx])
        x_y_coordinates.append(cluster["centroid"])
        
        x_y_coordinates = np.array(x_y_coordinates)

        # choose color
        color = listColour[i % len(listColour)]

        plt.plot(x_y_coordinates[:, 0], x_y_coordinates[:, 1], color=color,
                     linewidth=2, label=f"Drone {i+1}")

        # Make centroid standout
        xValCen, yValCen = cluster["centroid"]

        plt.plot(xValCen, yValCen, 'ko', markersize=14, label="Landing Pad (Home)", markerfacecolor="orange",
                 markeredgewidth=1.5)

    plt.title(f"Drone Routes")
    plt.legend(fontsize=16)

    plt.axis('equal')
    plt.margins(0.05)
    
    # saving the solution
    fileName = os.path.splitext(os.path.basename(fileName))[0]
    outputFileName = f"{fileName}_OVERALL_SOLUTION.jpeg"
    
    outputPath = os.path.join(directory, outputFileName)
    plt.savefig(outputPath, dpi=192)
    plt.close()

    print(f"Route image saved as {outputFileName}")

def main():
    filein = input("Enter the name of the file: ")

    if filein == "":
        filein = "input.txt"
    elif filein == "1":
        filein = "test_cases/Almond9832.txt"
    elif filein == "2":
        filein = "test_cases/pecan1212.txt"
    elif filein == "3":
        filein = "test_cases/threeCircle129.txt"
    elif filein == "4":
        filein = "test_cases/Walnut2621.txt"

    try:
        open(filein, 'r')
    except FileNotFoundError:
        exit("File not found")
        return

    helper = TSPHelper(filein)
    nodes = helper.num_points

    currentTime = datetime.now()
    print(f"There are {nodes} nodes: Solutions will be available by {(currentTime+timedelta(minutes=5)).strftime('%I:%M %p')}")
    
    finalResults = callKMeans_timeout(helper)
    
    print("Time taken", datetime.now() - currentTime)

    # output the total distance
    for key, valueCluster in finalResults.items():
        finalSumDistance = 0

        for a in valueCluster:
            if "distance" in a:
                finalSumDistance += a["distance"]

        print(f"\n{key}) If you use {key} drone(s), the total route will be {round(finalSumDistance,1)} meters")

        # looping through the results
        numList = ["i","ii","iii","iv"]
        for j, cluster in enumerate(valueCluster):
            xVal, yVal = cluster["centroid"]
            locationTotal = len(cluster["path"])
            dist = cluster["distance"]
 
            print(f" {numList[j]}. Landing Pad should be at [{int(xVal)}, {int(yVal)}], serving {locationTotal} locations, route is {round(dist,1)} meters.")

    # getting input k
    kNum = int(input("\nPlease select your choice 1 to 4: "))

    if kNum not in finalResults:
        print("Invalid number of drones. There are only 1, 2, 3, or 4 drones avaliable.")

    clusters = finalResults[kNum]
    # storing txt file in this folder
    folderName = "solution"

    os.makedirs(folderName, exist_ok=True)
    #making the file name and the file path
    fileName = os.path.splitext(os.path.basename(filein))[0]
    
    # list for all files that need to be stored
    filesDone = []

    for c in clusters:
        totalDist = round(c["distance"],1)
        droneNum = c["drone"]

        outputFileName = f"{fileName}_{droneNum}_solution_{totalDist}.txt"
        outputPath = os.path.join(folderName, outputFileName)

        filesDone.append(outputFileName)
        
        path = c["path"]
        with open(outputPath, "w") as file:
            for i in path:
                value = i + 1
                file.write(f"{value}\n")

    print(f"Writing {', '.join(filesDone)} to disk")

    image_gen(fileName, helper, clusters, folderName)

if __name__ == "__main__":
    main()

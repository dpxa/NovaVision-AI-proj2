from TSPHelper import TSPHelper
import searchAlgorithms
# import threading
import os
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# stop = threading.Event()

# def wait_for_enter():
#     input()
#     stop.set()

#function for generating image
def image_gen(fileName, helper,clusters, directory):
    # best_path not include start and finish home in code
    listColour = ["blue", "green","red","purple"] #list of colors for each cluster

    # graph path logic:
    plt.figure(figsize=(15, 15))  # setting the size of the graph

    for n, cluster in enumerate(clusters):
        if "path" not in cluster:
            continue  # skip SEK_Score entry
        #get teh corrdinates of the cluster points

        x_y_coordinates = np.array([helper.data[i] for i in cluster["path"]])


        color = listColour[n%len(listColour)] #choosing the color

        # plottong the graph

        plt.plot(x_y_coordinates[:, 0], x_y_coordinates[:, 1], color=color,
                     linewidth=2, label=f"Drone {n+1}")  # other coordiantes in blue

        #centroid to standout
        # the home coordinate plotting again to look different
        coordinatesCentroid = cluster["centroid"]
        xValCen, yValCen = helper.data[coordinatesCentroid]

        #homepad a color not in color list
        plt.plot(xValCen, yValCen, 'ko', markersize=8, label="Landing Pad (Home)", markerfacecolor="orange")  # home in red






    plt.title(f"Drone Routes")
    plt.legend(fontsize=16)


    plt.axis('equal')
    plt.margins(0.05)
    #saving the file as image

    fileName = os.path.splitext(os.path.basename(fileName))[0]
    outputFileName = f"{fileName}_OVERALL_SOLUTION.jpeg"
    # path solution/name of file
    outputPath = os.path.join(directory, outputFileName)
    plt.savefig(outputPath, dpi=192)
    plt.close()

    print(f"Route image saved as {outputFileName}")

def main():
    print("Compute DronePath")
    filein = input("Enter the name of the file: ")

    if filein == "":
        filein = "input.txt"

    try:
        open(filein, 'r')
    except FileNotFoundError:
        exit("File not found")
        return
    helper = TSPHelper(filein)

    nodes = helper.num_points
    currentTime = datetime.now()
    print(f"There are {nodes}: Solutions will be available by {(currentTime+timedelta(minutes=5)).strftime('%I:%M %p')}")
    finalResults = searchAlgorithms.callKMeans(helper) #K means algorithm

    for key, valueCluster in finalResults.items():
        #looping through the values and finding the total distance
        finalSumDistance = 0
        for a in valueCluster:
            if "distance" in a:
                finalSumDistance += a["distance"]
        #printing the values
        print(f"\n{key}) If you use {key} drone(s), the total route will be {round(finalSumDistance,1)} meters")

        #looping through the results
        for j, cluster in enumerate(valueCluster):
            if "centroid" not in cluster:
                continue #skip if no centroid
            else:
                centroidVal = cluster["centroid"]
                #lookup
                xVal, yVal = helper.data[centroidVal]

                locationTotal = len(cluster["path"])
                # the distance covered by the drone

                dist = cluster["distance"]
                #printing the land pad stuff
                print(f" {chr(105+j)}. Landing Pad should be at [{int(xVal)},{int(yVal)}], serving {locationTotal} locations, route is {round(dist,1)} meters")

    #getting input k
    kNum = int(input("\n Please select your choice 1 to 4: "))

    if kNum not in finalResults:
        print("Wrong K value")

    clusters = finalResults[kNum]
    #storing the txt fill in the folder solution
    folderName = "solution"

    os.makedirs(folderName, exist_ok=True)
    #making the file name and the file path
    fileName = os.path.splitext(os.path.basename(filein))[0]
    filesDone = [] #list for all files that are stored

    for c in clusters:
        if "distance" not in c:
            continue  # skip SEK_Score entry
        totalDist = round(c["distance"],1)

        path = c["path"]
        droneNum = c["drone"]
        outputFileName = f"{fileName}_{droneNum}_solution_{totalDist}.txt"
        #path solution/name of file
        outputPath = os.path.join(folderName, outputFileName)

        #appending to files done list
        filesDone.append(outputFileName)

        #removing first and last 1 in my path
        reducePath = path[1:-1] if path[0] == path[-1] else path

        with open(outputPath, "w") as file:
            #looping through the coordinates in the path
            for i in reducePath:
                #value containes the coordinate number
                value = i+1
                #writing to file
                file.write(f"{value}\n")

    print(f"Writing {', '.join(filesDone)} to disk")

    image_gen(fileName, helper, clusters, folderName)

if __name__ == "__main__":
    main()
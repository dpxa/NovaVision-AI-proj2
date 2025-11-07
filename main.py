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
def image_gen(fileName, directory,bestPath, pathDistance, helper):
    # best_path not include start and finish home in code
    
    coordinates = [[0.0] * 2 for _ in range(helper.num_points + 1)]
    for i, idx in enumerate(bestPath):
        coordinates[i] = helper.data[idx]

    coordinates = np.array(coordinates)

    x = coordinates[:,0]
    #seperating the coordinates to plot the graph
    y = coordinates[:,1]



    #graph path logic:
    plt.figure(figsize=(10, 10)) #setting the size of the graph

    #plottong the graph

    plt.plot(x, y, 'b-o', linewidth=2, markersize=4) #other coordiantes in blue
    #the home coordinate plotting again to look different
    plt.plot(x[0], y[0], 'ro', markersize=8, label = "Landing Pad (Home)") #home in red

    plt.title(f"Drone Route - Total Distance:{pathDistance} m")
    plt.legend()
    plt.axis('equal')
    plt.margins(0.05)
    #saving the file as image

    fileName = os.path.splitext(os.path.basename(fileName))[0]
    outputFileName = f"{fileName}_solution_{pathDistance}.jpeg"
    # path solution/name of file
    outputPath = os.path.join(directory, outputFileName)
    plt.savefig(outputPath, dpi=192)
    plt.close()

    print(f"Route image saved as {outputFileName}")

def main():
    print("ComputeDronePath")
    filein = input("Enter the name of the file: ")

    if filein == "":
        filein = "input.txt"

    # # set flag to stop the thread when "Enter key" is hit
    # wait_thread = threading.Thread(target = wait_for_enter)
    #  # Daemon thread will exit when the main program exits
    # wait_thread.daemon = True
    # wait_thread.start()

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
            finalSumDistance += a["distance"]
        #printing the values
        print(f"\n{key}) If you use {key} drone(s), the total route will be {round(finalSumDistance,1)} meters")

        #looping through the results
        for j, cluster in enumerate(valueCluster):
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


#OLD code stuff

    # print("\tShortest route discovered so far")
    #
    # alg_num = 2
    # if len(sys.argv) > 1 and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 2:
    #     alg_num = int(sys.argv[1])
    # bestPath, pathDistance = searchAlgorithms.search(helper)
    #
    # directory = "solution" #folder to store txt solutins
    # os.makedirs(directory, exist_ok=True)
    #
    # #making the file name and the file path
    # fileName = os.path.splitext(os.path.basename(filein))[0]
    # outputFileName = f"{fileName}_solution_{pathDistance}.txt"
    # #path solution/name of file
    # outputPath = os.path.join(directory, outputFileName)
    #
    # #6000 meter check
    # if pathDistance > 6000:
    #     print(f"Warning best distance {pathDistance} exceeds 6000 meters")
    #
    # #output file already exists
    # if os.path.exists(outputPath):
    #     print("Solution already present Overwriting it")
    #
    # with open(outputPath, "w") as f:
    #     #writing the output path to the txt file
    #     for p in bestPath:
    #         index = p + 1
    #         f.write(f"{index}\n")
    #
    # print(f"Route written to disk as {outputFileName}")
    #
    # image_gen(filein, directory, bestPath, pathDistance, helper)

if __name__ == "__main__":
    main()
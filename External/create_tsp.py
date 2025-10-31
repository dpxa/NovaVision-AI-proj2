import os

coordinates = []
filename = 'st70.tsp'
with open(filename, 'r') as f:
    for line in f:
        line = line.strip()
        if (line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9'))):
            coordinates.append(map(float, line.split()))
        
content = ""

for (i, x, y) in coordinates:
    content += f"{x} {y}\n"
    
with open('ready_' + filename, 'w') as f:
    f.write(content)

# i want 3 lines on a graph reoesenting the 3 algorithms

# it will be X vs Y (# of nodes vs (best score / optiomal score) %)

import matplotlib.pyplot as plt

x = [70, 127, 262]
y = []
scores = [[678, 119740, 2478], [726, 126075, 2976], [2684, 508552, 23257]]
solutions = [675, 118282, 2378]

for score in scores:
    for i in range(len(score)):
        score[i] = round((score[i] / solutions[i]) * 100, 2)
        
print(scores)

plt.figure(figsize=(10, 10))

plt.plot(x, scores[0], marker='o', linestyle='-', label="Algorithm 2 (NN-2opt-decay)")
plt.plot(x, scores[1], marker='o', linestyle='-', label="Algorithm 1 (NN-epsilon)")
plt.plot(x, scores[2], marker='o', linestyle='-', label="Random Search")

plt.xlabel('Number of Nodes')
plt.ylabel('Score / Optimal Score')
plt.title('TSP Algorithms Comparison')

plt.axhline(100, color='r', linestyle='-', linewidth='1', label='100% Baseline')

plt.legend()

plt.savefig('All_Algs.png')
plt.cla()

plt.plot(x, scores[0], marker='o', linestyle='-', label="Algorithm 2 (NN-2opt-decay)")
plt.plot(x, scores[1], marker='o', linestyle='-', label="Algorithm 1 (NN-epsilon)")

plt.xlabel('Number of Nodes')
plt.ylabel('Score / Optimal Score')
plt.title('TSP Algorithms Comparison (no RS)')

plt.axhline(100, color='r', linestyle='-', linewidth='1', label='100% Baseline')

plt.legend()

plt.savefig('No_Random.png')

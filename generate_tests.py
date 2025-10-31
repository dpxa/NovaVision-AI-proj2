import itertools
import subprocess
from pathlib import Path

def main():
    algs = [0, 1, 2]
    timers = [0.1, 1.0, 10.0, 100.0]
    filenames = ['External/ready_st70.tsp', 'External/ready_bier127.tsp', 'External/ready_gil262.tsp']
    count = 1
    
    perms = list(itertools.product(algs, timers, filenames))
    
    for t in perms:
        command = ['python', 'main.py', str(t[0]), str(t[1]), t[2]]
        print(f'Command {count} / {len(perms)} : {' '.join(command)}')
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout.strip())
        count += 1
    
    '''
    filenames2 = ['Sample/32Almonds.txt', 'Sample/64Walnut.txt', 'Sample/128Circle201.txt', 'Sample/128Hazelnut.txt', 'Sample/256Cashew.txt']
    count = 1
    
    for filename in filenames2:
        command = ['python', 'main.py', str(2), str(100), filename]
        print(f'Command {count} / {len(filenames2)} : {' '.join(command)}')
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout.strip())
        count += 1
    '''

if __name__ == "__main__":
    main()
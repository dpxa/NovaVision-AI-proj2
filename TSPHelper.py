import numpy as np

class TSPHelper:
    def __init__(self, filein: str):
        self.filein = filein
        # np array - (n, 2)
        self.data = self.data_to_list()
        self.num_points = len(self.data)
        # 2D numpy array - (n, n)
        self.lookup_table = self.populate_lookup_table()

    def data_to_list(self):
        data = []

        with open(self.filein, "r") as f:     
            first_char = f.read(1)
            if not first_char:
                print("Input file is empty")
                exit(1)
            f.seek(0)
            
            try:
                for line in f:
                    # strip whitespace and split line into individual coordinates
                    row = line.strip().split()
                    x = float(row[0])
                    y = float(row[1])
                    data.append((x, y))
            except ValueError:
                print("Input file contains data that is not a number")
                exit(1)
            
            self.unscaled_min_x = min(row[0] for row in data)
            self.unscaled_min_y = min(row[1] for row in data)

            # scale the coordinates to positive values only.
            scaled_data = []
            for p in data:
                scaled_data.append((p[0] - self.unscaled_min_x, p[1] - self.unscaled_min_y))
                
            # input file can either go back to home at the end or omit home
            # keep tuple comparison while still a Python list
            if len(scaled_data) > 1 and (scaled_data[-1] == scaled_data[0]):
                scaled_data.pop()
            
            self.min_x = 0
            self.min_y = 0
            self.max_x = max(row[0] for row in scaled_data)
            self.max_y = max(row[1] for row in scaled_data)
        # return as numpy array shape (n, 2)
        return np.array(scaled_data, dtype=float)

    def populate_lookup_table(self):
        # create numpy 2D array initialized to 0.0
        lookup_table = np.zeros((self.num_points, self.num_points), dtype=float)

        for i in range(self.num_points):
            # skip over scenario where j == i (already 0.0)
            for j in range(i + 1, self.num_points):
                x1, y1 = self.data[i]
                x2, y2 = self.data[j]
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                # populate the lookup table symmetrically so we don't need to check order of coords later
                lookup_table[i, j] = dist
                lookup_table[j, i] = dist

        return lookup_table

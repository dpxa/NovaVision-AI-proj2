class TSPHelper:
    def __init__(self, filein: str):
        self.filein = filein
        self.data = self.data_to_list()
        self.num_points = len(self.data)
        self.lookup_table_index_map = None
        self.lookup_table = self.populate_lookup_table()

    def data_to_list(self):
        data = []

        with open(self.filein, "r") as f:
            for line in f:
                # strip whitespace and split line into individual coordinates
                row = line.strip().split()
                data.append((float(row[0]), float(row[1])))
            
            if (data[-1] == data[0]):
                data.pop()
            # input file can either go back to home at the end or omit home

        return data

    def populate_lookup_table(self):
        # create 2d matrix and initialize all values to 0.0
        lookup_table = [[0.0] * self.num_points for _ in range(self.num_points)]
        
        # necessary so we can lookup tuples directly in the table
        self.lookup_table_index_map = {}
        for i, p in enumerate(self.data):
            self.lookup_table_index_map[p] = i

        for i in range(self.num_points):
            # skip over scenario where j == i (already 0.0)
            for j in range(i + 1, self.num_points):
                x1, y1 = self.data[i]
                x2, y2 = self.data[j]
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                # populate the lookup table symmetrically so we don't need to check order of coords later
                lookup_table[i][j] = dist
                lookup_table[j][i] = dist

        return lookup_table

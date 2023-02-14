from collections import defaultdict

class Network():
    def __init__(self):
        self.links = defaultdict(list)
        self.latencies = {}
        self.bandwidths = {}

    def add_link(self, from_node, to_node, latency, bandwidth):
        # Note: assumes edges are bi-directional
        self.links[from_node].append(to_node)
        self.links[to_node].append(from_node)
        self.latencies[(from_node, to_node)] = float(latency.replace("ms", ""))
        self.latencies[(to_node, from_node)] = float(latency.replace("ms", ""))
        self.bandwidths[(from_node, to_node)] = bandwidth
        self.bandwidths[(to_node, from_node)] = bandwidth

    def load_links(self, links):
        for link in links:
            self.add_link(*link)

    def load_links_from_dict(self, links):
        for link in links:
            self.add_link(*link.values())

    def find_path(self, start, stop, mode="shortest"):
        default = 0
        weight = self.latencies
        current_weight = lambda a, b : a + b
        selected_path = lambda a, b: a > b
        best = lambda a: min(a, key=lambda k: a[k][1])
        if mode == "thickest":
            default = float('inf')
            weight = self.bandwidths
            current_weight = lambda a, b : min(a, b)
            selected_path = lambda a, b: a < b
            best = lambda a: max(a, key=(lambda k: a[k][1]))
        elif mode != "shortest":
            return "There is not a mode like that"

        weight_paths = {start: (None, default)}
        current_node = start
        visited = set()


        while current_node != stop:
            visited.add(current_node)
            destinations = self.links[current_node]
            weight_to_current = weight_paths[current_node][1]

            for next in destinations:
                xweight = current_weight(weight[(current_node, next)], weight_to_current)
                if next not in weight_paths:
                    weight_paths[next] = (current_node, xweight)
                else:
                    current_best_weight = weight_paths[next][1]
                    if selected_path(current_best_weight, xweight):
                        weight_paths[next] = (current_node, xweight)

            next_destinations = {node: weight_paths[node] for node in weight_paths if node not in visited}
            if not next_destinations:
                return "Route Not Possible"
            # next node is the destination with the lowest weight
            current_node = best(next_destinations)

        # Work back through destinations in thickest path
        path = []
        while current_node != None:
            path.append(current_node)
            next = weight_paths[current_node][0]
            current_node = next
        # Reverse path
        path = path[::-1]
        return path, weight_paths[stop][1]


if __name__ == '__main__':
    links = [
        ('X', 'A', 1, 400),
        ('X', 'B', 1, 10),
        ('Y', 'A', 7, 400),
        ('Y', 'B', 5, 4)
    ]

    test_network = Network()
    test_network.load_links(links)


    print(test_network.find_path('A', 'B'), "\n", test_network.find_path('A', 'B', "thickest"))

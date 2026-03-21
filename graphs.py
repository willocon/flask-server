# Node:
# title: string (Location name)
# coordinates: tuple (x, z)

# nodes can be POIs or teleport destinations (e.g. fairy ring, spells)
# could maybe add a continent field to decide whether an edge is walkable.

class Node:
    def __init__(self, title, coordinates, is_fairy_ring):
        self.title = title
        self.coordinates = coordinates
        self.is_fairy_ring = is_fairy_ring
        self.neighbours = []

    def add_neighbour(self, edge):
        self.neighbours.append(edge)

    def __repr__(self):
        return f"Node({self.title}, {self.coordinates}, is_fairy_ring={self.is_fairy_ring})"
    

# Edge:
# from_node: Node
# to_node: Node
# est_time: float (estimated time to travel, uses pythagorean distance or 0 for teleport)
# GP_cost: int (cost in GP to travel)
# magic_lvl: int (required magic level to use the edge, 0 for non-teleport edges)
# is_teleport: bool (whether the edge is a teleport)

class Edge:
    def __init__(self, from_node, to_node, coordinates_from, coordinates_to, GP_cost, magic_lvl, is_teleport, is_transport):
        self.from_node = from_node
        self.to_node = to_node
        if is_teleport:
            self.est_time = 0
        elif from_node.is_fairy_ring and to_node.is_fairy_ring:
            self.est_time = 5  # arbitrary time for fairy ring travel, since its not really walkable but also not instant 
        elif is_transport:
            self.est_time = 10  # arbitrary time for transport edges like boats, since they aren't instant
        else:
            self.est_time = (((coordinates_to[0] - coordinates_from[0]) ** 2 + (coordinates_to[1] - coordinates_from[1]) ** 2) ** 0.5)/2  # divide by 2 to convert distance to approximate time, assuming that the player walks 2 tiles per second (realistically they can run 2 tiles per 0.6 seconds but we factor in they might walk portions)
        self.GP_cost = GP_cost
        self.magic_lvl = magic_lvl
        self.is_teleport = is_teleport
        self.is_transport = is_transport
        self.is_fairy_ring = from_node.is_fairy_ring and to_node.is_fairy_ring
    def __repr__(self):
        return f"Edge(from {self.from_node} to {self.to_node}, est_time {self.est_time}, GP_cost {self.GP_cost}, magic_lvl {self.magic_lvl}, is_teleport {self.is_teleport}, is_transport {self.is_transport}, is_fairy_ring {self.is_fairy_ring})"

# Graph:
# nodes: dict (key: title, value: Node)
# edges: list of Edge

# when adding a starting node, connect it to all nodes with a teleport edge within the magic level and gp constraints. Then connect to the nearest node to use as a walking edge. This then connects it to the rest of the graph.
# the destination node can be added to the nearest node using a walking edge.

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.pending_edges = []

    def add_node(self, title, coordinates, is_fairy_ring):
        if title not in self.nodes:
            self.nodes[title] = Node(title, coordinates, is_fairy_ring)

# in the csv, might do the from_title as "start" for teleports. 
# if the edge is a teleport, make it one directional from the start node to the destination node. The walkable edges are two way, and the fairy ring edges are two way.
    def add_edge(self, from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport):
        if from_title in self.nodes and to_title in self.nodes:
            from_node = self.nodes[from_title]
            to_node = self.nodes[to_title]
            edge = Edge(from_node, to_node, from_node.coordinates, to_node.coordinates, GP_cost, magic_lvl, is_teleport, is_transport)
            from_node.add_neighbour(edge)
            self.edges.append(edge)
            if not is_teleport:
                # Add reverse edge for walkable edges
                reverse_edge = Edge(to_node, from_node, to_node.coordinates, from_node.coordinates, GP_cost, magic_lvl, is_teleport, is_transport)
                to_node.add_neighbour(reverse_edge)
                self.edges.append(reverse_edge)

    def __repr__(self):
        return f"Graph(nodes: {list(self.nodes.keys())}, edges: {len(self.edges)})"


class Constraints:
    def __init__(self, max_magic_level, GP_budget, fairy_rings):
        self.max_magic_level = max_magic_level
        self.GP_budget = GP_budget
        self.fairy_rings = fairy_rings

    def __repr__(self):
        return f"Constraints(max_magic_level: {self.max_magic_level}, GP_budget: {self.GP_budget}, fairy_rings: {self.fairy_rings})"
    
    def subtract_GP(self, amount):
        if self.GP_budget >= amount:
            self.GP_budget -= amount
            return True
        return False

# only need to put the teleport edges in the csv, the walkable edges are generated.
# the edges for teleports should be one way from the start node to the destination node. The walkable edges are two way, and the fairy ring edges are two way.
# if i connect one fairy ring node to all of the others, then theyre now fully connected.
def from_file(file_path):
    graph = Graph()
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 4:  # Node
                title, x, z, fairy_ring = parts
                is_fairy_ring = fairy_ring.lower() == 'true'
                coordinates = (int(x), int(z))
                graph.add_node(title, coordinates, is_fairy_ring)
            elif len(parts) == 6:  # Edge
                from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport = parts[0], parts[1], int(parts[2]), int(parts[3]), parts[4].lower() == 'true', parts[5].lower() == 'true'
                if from_title in graph.nodes and to_title in graph.nodes:
                    graph.add_edge(from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport)
                    if not is_teleport:
                        graph.add_edge(to_title, from_title, GP_cost, magic_lvl, is_teleport, is_transport)  # add reverse edge for non-teleport edges (e.g. boats)
                else:
                    graph.pending_edges.append((from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport))
    return graph

def resolve_pending_edges(graph):
    still_pending = []
    for from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport in graph.pending_edges:
        if from_title in graph.nodes and to_title in graph.nodes:
            graph.add_edge(from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport)
        else:
            still_pending.append((from_title, to_title, GP_cost, magic_lvl, is_teleport, is_transport))
    graph.pending_edges = still_pending

# connect nodes within a certain distance with walking edges
def connect_walkable_nodes(graph, max_distance):
    for node1 in graph.nodes.values():
        for node2 in graph.nodes.values():
            if node1 != node2 and node2.is_fairy_ring == False:  # only connect non-fairy ring nodes with walkable edges
                if not(node1.neighbours and any(edge.is_transport for edge in node1.neighbours)): # dont try to connect transport edges with walking edges, since they arent really walkable
                    distance = ((node2.coordinates[0] - node1.coordinates[0]) ** 2 + (node2.coordinates[1] - node1.coordinates[1]) ** 2) ** 0.5
                    if distance <= max_distance:
                        graph.add_edge(node1.title, node2.title, GP_cost=0, magic_lvl=0, is_teleport=False, is_transport=False)

# add start and destination nodes, connecting them to the nearest nodes in the graph
def add_start_and_destination(graph, start_title, start_coordinates, dest_title, dest_coordinates):
    graph.add_node(start_title, start_coordinates, is_fairy_ring=False)
    graph.add_node(dest_title, dest_coordinates, is_fairy_ring=False)

    resolve_pending_edges(graph)

    # Connect start and destination to nearest nodes in the graph (excluding themselves)
    nearest_start_node = min((node for node in graph.nodes.values() if node.title != start_title), key=lambda node: ((node.coordinates[0] - start_coordinates[0]) ** 2 + (node.coordinates[1] - start_coordinates[1]) ** 2) ** 0.5)
    nearest_dest_node = min((node for node in graph.nodes.values() if node.title != dest_title), key=lambda node: ((node.coordinates[0] - dest_coordinates[0]) ** 2 + (node.coordinates[1] - dest_coordinates[1]) ** 2) ** 0.5)

    graph.add_edge(start_title, nearest_start_node.title, GP_cost=0, magic_lvl=0, is_teleport=False, is_transport=False)
    graph.add_edge(dest_title, nearest_dest_node.title, GP_cost=0, magic_lvl=0, is_teleport=False, is_transport=False)

# connect all fairy ring nodes to each other with teleport edges
def connect_fairy_ring_nodes(graph):
    fairy_ring_nodes = [node for node in graph.nodes.values() if node.is_fairy_ring]
    for i in range(1,len(fairy_ring_nodes)):
        graph.add_edge(fairy_ring_nodes[0].title, fairy_ring_nodes[i].title, GP_cost=0, magic_lvl=0, is_teleport=False, is_transport=False)

# perform djikstra's algorithm to find the shortest path from start to destination, considering the constraints
# before returning, print the nodes in the path and the edges taken, and the total GP cost and magic level used.
def dijkstra(graph, start_title, dest_title, constraints):
    import heapq
    queue = [(0, start_title, constraints.GP_budget)]  # (current_time, current_node_title, remaining_GP)
    dist = {start_title: (0, constraints.GP_budget)}  # Track both time and remaining GP for each node
    prev = {}
    while queue:
        current_time, current_title, remaining_GP = heapq.heappop(queue)
        # Check if we've already found a better path to this node
        if current_title in dist and current_time > dist[current_title][0]:
            continue
        if current_title == dest_title:
            path = []
            node_title = dest_title
            while node_title in prev or node_title == start_title:
                path.append(node_title)
                if node_title == start_title:
                    break
                node_title = prev[node_title]
            path.reverse()
            return current_time, len(path), path # return est time and number of nodes
        current_node = graph.nodes[current_title]   
        for edge in current_node.neighbours:
            next_title = edge.to_node.title
            
            # Check GP cost for ALL edges (not just teleports)
            if edge.GP_cost > remaining_GP:
                continue
            
            # Check magic level for teleports
            if edge.is_teleport and edge.magic_lvl > constraints.max_magic_level:
                continue
            
            # Check fairy ring constraint
            if edge.is_fairy_ring and not constraints.fairy_rings:
                continue

            new_time = current_time + edge.est_time
            new_remaining_GP = remaining_GP - edge.GP_cost
            
            # Only update if we found a better path (shorter time) to next_title
            if next_title not in dist or new_time < dist[next_title][0]:
                dist[next_title] = (new_time, new_remaining_GP)
                prev[next_title] = current_title
                heapq.heappush(queue, (new_time, next_title, new_remaining_GP))
    return float('inf'), 0  # return infinity and 0 steps if no path is found

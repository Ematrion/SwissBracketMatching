import networkx as nx
import itertools

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

cmap = ListedColormap([
    "#d62728",  # red
    "#2ca02c",  # green
    "#1f77b4",  # blue
    "#ffcc00",  # strong yellow
])
clab = [f"Round {i+1}" for i in range(len(cmap.colors))] # type:ignore
handles = [ mpatches.Patch(color=cmap.colors[i], label=clab[i]) for i in range(len(cmap.colors))] # type:ignore

from ema.gtypes import Edge


class CompleteBiPartite:
    def __init__(self, n):
        self.n = n
        self.nodes = list(range(1, n+1))
        self.left = self.nodes[:n//2]
        self.right = self.nodes[n//2:]
        self.edges = list(itertools.product(self.left, self.right))
        
        
        self.coloring: dict[Edge, int] = {} # a dict (u,v) -> color
        
        #self.graph = nx.Graph()
        self.graph = nx.Graph(self.edges)
    
    
    def positions(self):
        pos = {}

        # left side ordered (keep as-is)
        for i, node in enumerate(self.left):
            pos[node] = (0, -i)

        # right side reversed visually
        n_right = len(self.right)
        for i, node in enumerate(self.right):
            # flip the vertical position
            pos[node] = (1, -(n_right - 1 - i))

        return pos

    
    def plot(self, coloring=True):
        if self.coloring and coloring:
            colors = [self.coloring[tuple(edge)] for edge in self.graph.edges()] # type: ignore
            nx.draw(self.graph, pos=self.positions(), with_labels=True,
                    edge_color=colors, edge_cmap=cmap, edge_vmin=0, edge_vmax=len(cmap.colors) - 1) # type: ignore
            #plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), handles=handles)
        else:
            nx.draw(self.graph, pos=self.positions(), with_labels=True)
    
    def set_edges_color(self, covering):
        colors = list(range(len(covering.keys())))
        coloring = {}
        for color, (day, edges) in zip(colors, covering.items()):
            for edge in edges:
                # NOTE: it is an undirected graph, but no idea wich version is stored in selg.graph.edges()
                coloring[(edge[0], edge[1])] = color
                coloring[(edge[1], edge[0])] = color
        
        self.coloring = coloring

    def remove_pairing(self, u, v):
        if (u,v) not in self.edges:
            raise ValueError(f'{(u,v)} not a pairing in graph {self.graph}')
        
        self.remove_node(u)
        self.remove_node(v)
    
    def remove_node(self, v):
        if v in self.left:
            self.left.remove(v)
        elif v in self.right:
            self.right.remove(v)
        else:
            raise ValueError(f'vertex {v} not in graph {self.graph}')
        
        self.nodes.remove(v)
        self.graph.remove_node(v)
                             
        # convert to list because dict changes in loop
        for key in list(self.coloring.keys()):
            if v in key:
                del self.coloring[key]

    def remove_color(self, color: int):
        # get all edges colored by 'color'
        same_color_edges = [edge for edge, c in self.coloring.items() if c == color]
        
        # remove those edges
        self.graph.remove_edges_from(same_color_edges)

    def reduce(self, u, v, remove_color: bool=True):
        # remove (u,v)
        self.remove_pairing(u, v)
        
        if remove_color:
            # get color of (u,v) or (v,u)
            try:
                uv_color = self.coloring[(u,v)]
            except KeyError:
                uv_color= self.coloring[(v,u)]
            self.remove_color(uv_color)
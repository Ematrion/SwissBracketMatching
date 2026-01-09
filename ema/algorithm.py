import itertools

#from utils import relabelling, RotatingOpponents
from ema.gtypes import Matching, Covering

def new_vertex():
    # return the high and the low seed
    return 'high', 'low'

def one_more_edge(matching: Matching, v1, v2) -> Matching:
    return matching + [(v1, v2)]
    
def mixture(op1: Matching, op2: Matching, v1, v2) -> Matching:
    assert len(op1) == len(op2)
    common_edge = set(op1).intersection(set(op2))
    
    # some bullet proof testing,
    assert len(common_edge) == 1
    common_edge = list(common_edge)[0]
    (a1, a2) = common_edge
    
    new_coloring = list(set(op2)-{common_edge}) + [(a1, v2), (v1, a2)]
    assert len(new_coloring) == len(op1) + 1
    
    return new_coloring

# ----- #

def label_mapping(total: int, labels: list | None = None, shift: int=0):
    iterator = iter(labels) if labels else range(2, total)
    new_labels = {i-1: i for i in iterator}
    new_labels['high'] = min(new_labels.values())-1
    new_labels['low'] = max(new_labels.values())+1
    return {key: value + shift for key, value in new_labels.items()}

def relabelling(edges, *args, **kwars):
    lm = label_mapping(total=len(edges)*2, *args, **kwars)
    new_edges = []
    for (v1, v2) in edges:
        new_edges.append( (lm[v1], lm[v2]) )
    return new_edges

def get_left(matching: Matching):
    return [u for (u, _) in matching]

def get_right(matching: Matching):
    return [v for (_, v) in matching]


class RotatingOpponents:
    def __init__(self, game_day: Matching):
        # constant state
        self.left = get_left(game_day)
        self.right = get_right(game_day)
        
        # variable state
        self.right_indices = None
        self.i = None
        self.n = None
    
    def __iter__(self):
        self.i = 0
        self.n = len(self.left)
        self.right_indices = list(range(len(self.right)))
        return self
    
    def __next__(self):
        if self.i < self.n: # type: ignore
            current = self.right_indices
            self.i += 1 # type: ignore
            self.right_indices = [self.right_indices[-1]] + self.right_indices[0:-1] # type: ignore
            return self.make_round(current)
        else:
            raise StopIteration
    
    def make_round(self, indices):
        return [(u, self.right[i]) for u, i in zip(self.left, indices)]


def cross_options(op1: Covering, op2: Covering):
    v1, vn = new_vertex()
    options = []
    for name1, op1_1 in op1.items():
        coloring = {f'{name1}{name1}': one_more_edge(op1_1, v1, vn)}
        
        for name2, op2_2 in op2.items():
            coloring[f'{name1}{name2}'] = mixture(op1_1, op2_2, v1, vn)
        
        options.append(coloring)
    
    for option in options:
        for name, edges in option.items():
            option[name] = relabelling(edges)
            
    return options

def roll_match(matching: Matching):
    new_cover = {}
    for i, new_matching in enumerate(RotatingOpponents(matching)):
        new_cover[f'{i}'] = new_matching
    return new_cover

def roll_options(coverings: list[Covering]) -> list[Covering]:
    u, v = new_vertex()
    options = []
    for cover in coverings:
        for name, matching in cover.items():
            extended = one_more_edge(matching, u, v)
            options.append({f'{name}_R_{day}': new_match for day, new_match in roll_match(extended).items()})
    
    for option in options:
        for name, edges in option.items():
            option[name] = relabelling(edges)
            
    return options
    

# --- Generalisation --- #
def hyper_nodes(coverings):
    nodes = [name for covering in coverings for name in covering.keys()]
    return nodes

def hyper_edges(coverings):
    mappings = {name: edges for covering in coverings for name, edges in covering.items()}
    color_classes = [list(covering.keys()) for covering in coverings]
    edges = []
    for covering1, covering2 in itertools.combinations(color_classes, 2):
        print('cov1', covering1, 'cov2',covering2)
        for matching1, matching2 in itertools.product(covering1, covering2):
            g1, g2 = mappings[matching1], mappings[matching2] 
            print('m1', matching1, g1, 'm2', matching2, g2, 'inter', set(g1).intersection(set(g2)))
            edges.append((matching1, matching2))
    return edges
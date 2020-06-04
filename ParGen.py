from math import sqrt
import numpy as np
import ete3_functions
from imp import reload
reload(ete3_functions)
from ete3_functions import make_ete3_lifted, save_ete3

LIMIT = .14
GAMMA = .9
LAMBDA = .1

def initialize_u(leaves, u_vec):
    if u_vec is not None:
        for leaf, u_val in zip(leaves, np.ravel(u_vec)):
            leaf.u = u_val
    # if u_vec is not None:
    #     names = [leaf.name for leaf in leaves]
    #     temp = dict(zip(names,np.ravel(u_vec)))
    #     for leaf in leaves:
    #         leaf.u = temp.get(leaf.name,0)

def normalize_u(leaves):
    summ = sum(map(lambda leaf:leaf.u**2, leaves))
    for leaf in leaves:
        leaf.u /= sqrt(summ)

def truncate_u(leaves, threshold):
    if threshold is not None:
        for leaf in leaves:
            if leaf.u < threshold:
                leaf.u = 0

def set_internal_u(node):
    if node.is_leaf:
        return node.u ** 2
    summ = .0
    for child in node:
        summ += set_internal_u(child)
        node.u = sqrt(summ)
    return summ

def prune_tree(node):
    if node.u == 0:
        node.children = []
    for child in node:
        prune_tree(child)

def reduce_edges(node):
    if len(node) == 1:
        temp = node.children[0].children
        node.children = temp
    for child in node:
        reduce_edges(child)

def set_params(node):
    if node.is_internal:
        node.G = [leaf for leaf in node.leaf_cluster if leaf.u==0]
        for gap in node.G: gap.v = gap.parent.u
        node.V = sum(map(lambda gap: gap.v, node.G))
    for child in node:
        set_params(child)

def enumerate_tree_layers(node, current_layer=0):
    node.e = current_layer
    for child in node:
        enumerate_tree_layers(child, current_layer=current_layer+1)

def make_init_step(node, gamma_v):
    if node.is_internal:
        for child in node:
            make_init_step(child, gamma_v)
    else:
        if node.u > 0:
            node.H = [node]; node.L = []; node.p = gamma_v * node.u
        else:
            node.H = []; node.L = []; node.p = 0

def make_recursive_step(node, lambda_v):
    if node.is_internal:
        for child in node:
            make_recursive_step(child, lambda_v)
        p_nogain = sum(child.p for child in node)
        p_gain = node.u + lambda_v * node.V

        if p_gain < p_nogain:
            node.H = [node];
            node.L = node.G;
            node.p = p_gain
        else:
            node.H = [];
            node.L = [];
            node.p = p_nogain
            for child in node: node.H += child.H; node.L += child.L

def make_result_table(node):
    table = []

    if node.is_internal:
        for child in node:
            table.extend(make_result_table(child))

    table.append([node.index.rstrip(".") or "", node.name, str(round(node.u, 3)),
                  str(round(node.p, 3)), str(round(node.V, 3)),
                  "; ".join([" ".join([s.index, s.name]) for s in (node.H or [])]),
                  "; ".join([" ".join([s.index, s.name]) for s in (node.G or [])]),
                  "; ".join([" ".join([s.index, s.name]) for s in (node.L or [])])])

    return table

def save_result_table(result_table, filename="table.csv"):

    result_table = sorted(result_table, key=lambda x: (len(x), x))
    result_table = [["index", "name", "u", "p", "V", "H", "G", "L"]] + result_table
    with open(filename, 'w') as file_opened:
        for table_row in result_table:
            file_opened.write('\t'.join(table_row) + '\n')
    print(f"Table saved in the file: {filename}")

def parGen(root, u_vec, gamma_v=GAMMA, lambda_v=LAMBDA, limit=LIMIT):

    leaves = root.leaf_cluster
    initialize_u(leaves, u_vec)
    print('SUM:', sum(map(lambda leaf: leaf.u**2, leaves)))
    normalize_u(leaves)
    print(f"Number of leaves: {len(leaves)}")
    print("All positive weights:")
    for leaf in sorted(leaves, key=lambda leaf: leaf.u, reverse=True):
        if round(leaf.u,1):
            print(f"{leaf.name:<60} {round(leaf.u,2)}")

    print('Truncating with u-membership threshold', limit)
    truncate_u(leaves, limit)
    normalize_u(leaves)
    print("Setting weights for internal nodes")
    set_internal_u(root)
    print(f"Membership in root: {root.u:.5f}")
    print("Pruning tree...")
    prune_tree(root)
    print('Number of leaves after truncating and pruning',len(root.leaf_cluster))
    print("Setting gaps...and other parameters")
    reduce_edges(root)
    set_params(root)
    enumerate_tree_layers(root)

    print("ParGenFS main steps...")
    make_init_step(root, gamma_v)
    make_recursive_step(root, lambda_v)

    print("Saving...")
    result_table = make_result_table(root)
    save_result_table(result_table)

    ete3_desc = make_ete3_lifted(root)
    save_ete3(ete3_desc)
    # print("ete representation:")
    # print(ete3_desc)
    print("Done.")


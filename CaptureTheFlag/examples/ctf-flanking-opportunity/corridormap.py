#==============================================================================
# This file is part of The AI Sandbox
# Copyright (c) 2013, AiGameDev.com KG.
#==============================================================================

"""
NOTE!

This file is work in progress and not documented.  This process was covered in
a previous masterclass that you can find here:

https://new.livestream.com/accounts/1422055/events/1699806


We'll be finalizing this code and posting it as a standalone module within
The AI Sandbox soon.   In the meantime, we recommend using it as a black-box
as shown in the example commanders.
"""

import math
import numpy
import mahotas
from PIL import Image
from PIL import ImageOps
import networkx as nx

DEFAULT_MAP_SCALE = 10
LONG_EDGE_SPLIT_TOLERANCE_PX = 4.0
WELD_TOLERANCE_PX = 2.0

def build_graph(block_heights, width, height):
    map_image = image_from_block_heights(block_heights, width, height)
    skel_map = compute_skeleton(map_image)
    area_graph_adj = build_image_space_area_graph(skel_map)
    split_long_edges(skel_map, area_graph_adj, LONG_EDGE_SPLIT_TOLERANCE_PX * DEFAULT_MAP_SCALE)
    weld_vertices(area_graph_adj, WELD_TOLERANCE_PX * DEFAULT_MAP_SCALE)
    area_graph_adj = convert_to_world_coords(area_graph_adj)

    graph = nx.Graph(directed=False)

    for u, coords in enumerate(area_graph_adj.keys()):
        graph.add_node(u, position=coords)

    for u, u_coords in enumerate(area_graph_adj.keys()):
        for v_coords in area_graph_adj[u_coords]:
            v = area_graph_adj.keys().index(v_coords)
            graph.add_edge(u, v, weight=math.sqrt((u_coords[0] - v_coords[0])**2 + (u_coords[1] - v_coords[1])**2))

    return graph

def fromimage(im):
    im = im.convert('F')
    return numpy.array(im)

def image_from_block_heights(block_heights, width, height, scale=DEFAULT_MAP_SCALE):
    '''Create image-array for processing from block heights list'''
    img = Image.new('I', (width, height), 1)

    for x in range(width):
        for y in range(height):
            if block_heights[x][y] > 0:
                img.putpixel((x, y), 0)

    img = ImageOps.expand(img, border=1, fill=0)
    img = img.resize((scale * img.size[0], scale * img.size[1]), Image.NEAREST)
    arr = fromimage(img)
    arr = arr.astype(numpy.bool)
    return arr

def compute_skeleton(input_map):
    '''Returns a skeleton image of the free space'''
    return mahotas.thin(input_map)

def build_image_space_area_graph(skel_map):
    '''Builds image space graph (represented with adjacency list) by connecting skeleton junctions'''
    initial = numpy.where(skel_map==1)

    if initial[0].size == 0 or initial[1].size == 0:
        return None

    stack = [((initial[0][0], initial[1][0]), None)]
    visited = set([])
    adj_list = {None:[]}

    walk_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while len(stack) > 0:
        top = stack.pop()

        node, junction = top

        visited.add(node)

        children = []

        for walk_dir in walk_dirs:
            child = (node[0] + walk_dir[0], node[1] + walk_dir[1])

            if skel_map[child[0], child[1]] != 1:
                continue

            if child in visited:
                if child in adj_list:
                    if not child in adj_list[junction]:
                        adj_list[junction].append(child)

                continue

            children.append(child)

        if len(children) > 1:
            adj_list[node] = []
            adj_list[junction].append(node)
            junction = node

        for child in children:
            stack.append((child, junction))

    del adj_list[None]

    for u in adj_list.iterkeys():
        adj_list[u] = [e for e in adj_list[u] if u != e]

        for v in adj_list[u]:
            if u not in adj_list[v]:
                adj_list[v].append(u)

    return adj_list

def find_pixel_path(skel_map, adj_list, u, v):
    '''Finds the skeleton pixels connecting two neighbouring junctions using Breadth First Search'''
    def reverse_path(begin, end, parents):
        result = [end]
        while result[0] != begin:
            result.insert(0, parents[result[0]])
        return result

    walk_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    queue = [u]
    visited = set([])
    parents = {}

    while len(queue) > 0:
        node = queue.pop(0)

        if node == v:
            return reverse_path(u, v, parents)

        if node != u and node in adj_list:
            continue

        visited.add(node)

        for walk_dir in walk_dirs:
            child = (node[0] + walk_dir[0], node[1] + walk_dir[1])

            if skel_map[child[0], child[1]] != 1:
                continue

            if child in visited:
                continue

            parents[child] = node
            queue.append(child)

    return None

def split_long_edges(skel_map, adj_list, tolerance):
    '''Create additional vertices on the edges longer than tolerance'''
    edge_list = set([(u, v) for u in adj_list for v in adj_list[u]])
    visited = set([])

    for (u, v) in edge_list:
        if (v, u) in visited:
            continue

        visited.add((u, v))

        if (v[0]-u[0])**2 + (v[1]-u[1])**2 > tolerance * tolerance:
            path = find_pixel_path(skel_map, adj_list, u, v)

            if path == None:
                continue

            s = u

            for w in path[1:-1]:
                if (w[0]-s[0])**2 + (w[1]-s[1])**2 > tolerance * tolerance:
                    adj_list[s].remove(v)
                    adj_list[v].remove(s)
                    adj_list[s].append(w)
                    adj_list[v].append(w)
                    adj_list[w] = [s, v]
                    s = w

def weld_vertices(adj_list, tolerance):
    '''Remove vertices closer than tolerance'''
    cell_size = 10.0 * tolerance
    num_buckets = 128
    buckets = [[] for i in range(num_buckets)]

    def cell_hash(x, y):
        return (0x8da6b343 * x + 0xd8163841 * y) % num_buckets

    def get_weld_vertex(v, bucket):
        for u in buckets[bucket]:
            if (u[0]-v[0])**2 + (u[1]-v[1])**2 < tolerance * tolerance:
                return u

        return None

    def add_to_bucket(v):
        x = int(v[0]/cell_size)
        y = int(v[1]/cell_size)
        buckets[cell_hash(x, y)].append(v)

    def weld_vertex(v):
        top = int((v[1] - tolerance)/cell_size)
        left = int((v[0] - tolerance)/cell_size)
        right = int((v[0] + tolerance)/cell_size)
        bottom = int((v[1] + tolerance)/cell_size)

        visited = set([])

        for i in range(left, right+1):
            for j in range(top, bottom+1):
                bucket = cell_hash(i, j)
                if bucket in visited:
                    continue
                visited.add(bucket)

                w = get_weld_vertex(v, bucket)

                if w:
                    return w

        add_to_bucket(v)
        return v

    def weld(adj_list, v, w):
        w_neis = [e for e in adj_list[w] if e != v]
        v_neis = [e for e in adj_list[v] if e != w]

        adj_list[w] = list(set(w_neis + v_neis))

        for v_nei in v_neis:
            adj_list[v_nei] = [e for e in adj_list[v_nei] if e != v and e != w] + [w]

        del adj_list[v]

    vertices = adj_list.keys()

    for v in vertices:
        w = weld_vertex(v)
        if w != v:
            weld(adj_list, v, w)

def compute_vertex_areas(input_map, adj_list):
    '''Computes the image map containing pixel-vertex relation'''
    surface = numpy.ones(input_map.shape, dtype=numpy.uint32)
    markers = numpy.zeros(input_map.shape, dtype=numpy.uint32)

    vertex_list = []

    for index, (x, y) in enumerate(adj_list.iterkeys()):
        markers[x, y] = index + 1
        vertex_list.append((x, y))

    return mahotas.cwatershed(surface, markers), vertex_list

def downscale_vertex_areas(vertex_areas_map, scale=DEFAULT_MAP_SCALE):
    m = vertex_areas_map.astype(numpy.uint32)
    i = Image.fromstring('I', (m.shape[1], m.shape[0]), m.tostring())
    i = i.resize((m.shape[1]/scale, m.shape[0]/scale), Image.NEAREST)
    r = numpy.array(i)
    return r

def image_map_to_world_space(coords, scale=DEFAULT_MAP_SCALE, border_width=1):
    x = (coords[1] - border_width * scale)/float(scale)
    y = (coords[0] - border_width * scale)/float(scale)
    return (x, y)

def convert_to_world_coords(adj_list, scale=DEFAULT_MAP_SCALE, border_width=1):
    '''Image space adj list -> world space adj list'''
    result = {}

    for u_coords, neis in adj_list.iteritems():
        u = image_map_to_world_space(u_coords, scale, border_width)
        result[u] = []

        for v_coords in neis:
            result[u].append(image_map_to_world_space(v_coords, scale, border_width))

    return result

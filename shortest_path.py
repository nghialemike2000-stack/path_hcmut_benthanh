from __future__ import annotations

import math
import csv
import json
from pathlib import Path
from itertools import islice

import folium
import networkx as nx
import osmnx as ox


# =========================================================
# GATES / ENTRANCES
# =========================================================

BACH_KHOA_GATES = {

    "gate_1": (
        10.772085537574405, 106.65770218648836
    ),

    "gate_2": (
        10.772689726821197, 106.66066833396891
    ),

    "gate_3": (
        10.773539119525351, 106.6613593305036
    ),
}

BEN_THANH_GATES = {

    "north": (
        10.773162054715135, 106.69763552764178
    ),

    "east": (
        10.77279460684222, 106.69850445081336
    ),

    "south": (
        10.772030759155927, 106.69834289980986
    ),

    "west": (
        10.772210782443693, 106.69757864713894
    ),
}

GATE_DISPLAY_NAMES = {

    "gate_1": "HCMUT Gate 1",
    "gate_2": "HCMUT Gate 2",
    "gate_3": "HCMUT Gate 3",

    "north": "Ben Thanh North Gate",
    "east": "Ben Thanh East Gate",
    "south": "Ben Thanh South Gate",
    "west": "Ben Thanh West Gate",
}

# =========================================================
# TEMPORARY LOCATIONS FOR BBOX
# =========================================================

loc_bach_khoa = list(BACH_KHOA_GATES.values())[0]
loc_ben_thanh = list(BEN_THANH_GATES.values())[0]



# =========================================================
# CONFIG
# =========================================================

K_PATHS = 30
TARGET_VERTICES = 100
MIN_LENGTH_THRESHOLD = 0  # filter out very short edges (e.g. connectors to gates)
NETWORK_TYPE = "drive"

# bounding box padding
LAT_PADDING = 0.006
LON_PADDING = 0.006

OUTPUT_HTML = "hcmut_ben_thanh_k_paths.html"

CSV_OUTPUT_FOLDER = Path("list_vertex")

CSV_OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# CREATE BBOX
# =========================================================

north = max(loc_ben_thanh[0], loc_bach_khoa[0]) + LAT_PADDING
south = min(loc_ben_thanh[0], loc_bach_khoa[0]) - LAT_PADDING
east = max(loc_ben_thanh[1], loc_bach_khoa[1]) + LON_PADDING
west = min(loc_ben_thanh[1], loc_bach_khoa[1]) - LON_PADDING

bbox = (west, south, east, north)

# =========================================================
# DOWNLOAD GRAPH
# =========================================================

print("Downloading map data...")

custom_filter = """
["highway"~"motorway|trunk|primary|secondary|tertiary"]
"""

# =========================================================
# DOWNLOAD AND CONSOLIDATE GRAPH
# =========================================================
print("Downloading and consolidating map data...")

# Download original graph
G_raw = ox.graph_from_bbox(
    bbox,
    custom_filter=custom_filter,
    simplify=True,
)

# Project to UTM (meters) for accurate distance consolidation
G_proj = ox.project_graph(G_raw)

# Consolidate intersections within 25 meters to merge close nodes
# This handles complex junctions and dual carriage ways
G_cons = ox.consolidate_intersections(G_proj, rebuild_graph=True, tolerance=25, dead_ends=False)

# Project back to WGS84 (lat/long) for folium and GPS calculations
G = ox.project_graph(G_cons, to_crs="EPSG:4326")

print(f"Consolidated graph loaded:")
print(f"Nodes: {len(G.nodes)}")
print(f"Edges: {len(G.edges)}")

# =========================================================
# CONVERT TO SIMPLE DIGRAPH
# =========================================================

D = ox.convert.to_digraph(G, weight="length")

# =========================================================
# FIND BEST GATE COMBINATION
# =========================================================

best_distance = float("inf")

best_start_gate = None
best_end_gate = None

best_origin_node = None
best_destination_node = None

for start_name, start_point in BACH_KHOA_GATES.items():

    for end_name, end_point in BEN_THANH_GATES.items():

        try:

            temp_origin = ox.nearest_nodes(
                G,
                X=start_point[1],
                Y=start_point[0]
            )

            temp_destination = ox.nearest_nodes(
                G,
                X=end_point[1],
                Y=end_point[0]
            )

            temp_distance = nx.shortest_path_length(
                D,
                temp_origin,
                temp_destination,
                weight="length"
            )

            print(
                f"{start_name} -> {end_name} "
                f"= {temp_distance/1000:.2f} km"
            )

            if temp_distance < best_distance:

                best_distance = temp_distance

                best_start_gate = start_name
                best_end_gate = end_name

                best_origin_node = temp_origin
                best_destination_node = temp_destination

        except Exception:

            print(
                f"Skip {start_name} -> {end_name}"
            )

# =========================================================
# FINAL BEST ROUTE
# =========================================================

print("\n================================")
print("BEST GATE COMBINATION")
print("================================")

print(f"HCMUT : {best_start_gate}")
print(f"Ben Thanh : {best_end_gate}")
print(f"Distance : {best_distance/1000:.2f} km")

START_GATE = best_start_gate
END_GATE = best_end_gate

loc_bach_khoa = BACH_KHOA_GATES[START_GATE]
loc_ben_thanh = BEN_THANH_GATES[END_GATE]

# =========================================================
# FIND BEST ROAD NODES
# =========================================================

origin = ox.nearest_nodes(
    G,
    X=loc_bach_khoa[1],
    Y=loc_bach_khoa[0]
)

destination = ox.nearest_nodes(
    G,
    X=loc_ben_thanh[1],
    Y=loc_ben_thanh[0]
)

print(f"\nOrigin node: {origin}")
print(f"Destination node: {destination}")

# =========================================================
# CREATE CUSTOM GATE NODES
# =========================================================

origin_gate_node = "HCMUT_GATE"
destination_gate_node = "BEN_THANH_GATE"

G.add_node(
    origin_gate_node,
    y=loc_bach_khoa[0],
    x=loc_bach_khoa[1]
)

G.add_node(
    destination_gate_node,
    y=loc_ben_thanh[0],
    x=loc_ben_thanh[1]
)

# =========================================================
# CONNECT GATE TO ROAD NETWORK USING REAL DISTANCE
# =========================================================

from geopy.distance import geodesic

# ---------------------------------------------------------
# HCMUT REAL CONNECTOR DISTANCE
# ---------------------------------------------------------

origin_node_coord = (
    G.nodes[origin]["y"],
    G.nodes[origin]["x"]
)

origin_connector_length = geodesic(
    loc_bach_khoa,
    origin_node_coord
).meters

print(
    f"HCMUT gate connector = "
    f"{origin_connector_length:.2f} meters"
)

G.add_edge(
    origin_gate_node,
    origin,
    length=origin_connector_length
)

G.add_edge(
    origin,
    origin_gate_node,
    length=origin_connector_length
)

# ---------------------------------------------------------
# BEN THANH REAL CONNECTOR DISTANCE
# ---------------------------------------------------------

destination_node_coord = (
    G.nodes[destination]["y"],
    G.nodes[destination]["x"]
)

destination_connector_length = geodesic(
    loc_ben_thanh,
    destination_node_coord
).meters

print(
    f"Ben Thanh connector = "
    f"{destination_connector_length:.2f} meters"
)

G.add_edge(
    destination,
    destination_gate_node,
    length=destination_connector_length
)

G.add_edge(
    destination_gate_node,
    destination,
    length=destination_connector_length
)

# =========================================================
# REBUILD DIGRAPH AFTER ADDING CUSTOM NODES
# =========================================================

D = ox.convert.to_digraph(G, weight="length")

# =========================================================
# USE GATE NODES AS REAL START + END
# =========================================================

origin = origin_gate_node
destination = destination_gate_node

# =========================================================
# FIND K SHORTEST PATHS
# =========================================================

print(f"\nFinding {K_PATHS} shortest paths...")

paths_iter = nx.shortest_simple_paths(
    D,
    origin,
    destination,
    weight="length"
)

paths = list(islice(paths_iter, K_PATHS))

print(f"Found {len(paths)} paths")

# =========================================================
# CALCULATE PATH LENGTH
# =========================================================

def route_length(graph: nx.DiGraph, route: list[int]) -> float:
    total = 0.0

    for u, v in zip(route[:-1], route[1:]):
        total += graph.edges[u, v]["length"]

    return total


lengths = []

for idx, path in enumerate(paths):
    length = route_length(D, path)
    lengths.append(length)

    print(f"\nPath {idx+1}")
    print(f"Distance: {length / 1000:.2f} km")
    print(f"Vertices: {len(path)}")

# =========================================================
# GET INTERSECTIONS / IMPORTANT NODES
# =========================================================

selected_nodes = set()

for path in paths:
    for node in path:
        selected_nodes.add(node)

# if still not enough vertices,
# add nearby intersections

# =========================================================
# ADD MORE INTERSECTIONS WITH DISTANCE GAP
# =========================================================

MIN_NODE_GAP = 80  # Minimum distance in meters between any two selected nodes

if len(selected_nodes) < TARGET_VERTICES:

    print(f"\nAdding more intersections with {MIN_NODE_GAP}m gap...")

    center_lat = (
        loc_ben_thanh[0] + loc_bach_khoa[0]
    ) / 2

    center_lon = (
        loc_ben_thanh[1] + loc_bach_khoa[1]
    ) / 2

    def corridor_distance(node_id: int):

        lat = G.nodes[node_id]["y"]
        lon = G.nodes[node_id]["x"]

        return geodesic(
            (lat, lon),
            (center_lat, center_lon)
        ).meters

    candidates = []

    for node, data in G.nodes(data=True):

        if node in selected_nodes:
            continue

        street_count = int(data.get("street_count", 0))

        if street_count >= 3:
            candidates.append(node)

    candidates.sort(key=corridor_distance)

    for node in candidates:

        if len(selected_nodes) >= TARGET_VERTICES:
            break

        node_lat = G.nodes[node]["y"]
        node_lon = G.nodes[node]["x"]

        is_too_close = False

        for s_node in selected_nodes:

            s_lat = G.nodes[s_node]["y"]
            s_lon = G.nodes[s_node]["x"]

            dist = geodesic(
                (node_lat, node_lon),
                (s_lat, s_lon)
            ).meters

            if dist < MIN_NODE_GAP:
                is_too_close = True
                break

        if not is_too_close:
            selected_nodes.add(node)

print(f"\nSelected vertices: {len(selected_nodes)}")

# =========================================================
# CREATE SUBGRAPH
# =========================================================

subgraph = G.subgraph(selected_nodes).copy()

print(f"Subgraph nodes: {len(subgraph.nodes)}")
print(f"Subgraph edges: {len(subgraph.edges)}")

# =========================================================
# CREATE NODE INDEX
# =========================================================

selected_nodes_list = list(selected_nodes)

node_to_index = {}

for idx, node in enumerate(selected_nodes_list):

    node_to_index[node] = idx

# =========================================================
# CREATE GOOGLE MAP STYLE VIEW
# =========================================================

center_lat = (
    loc_ben_thanh[0] + loc_bach_khoa[0]
) / 2

center_lon = (
    loc_ben_thanh[1] + loc_bach_khoa[1]
) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=15,
    tiles="OpenStreetMap"
)

map_name = m.get_name()
# =========================================================
# MARK MAIN LOCATIONS
# =========================================================

folium.Marker(
    location=loc_ben_thanh,
    popup=f"Ben Thanh {GATE_DISPLAY_NAMES[END_GATE]}",
    icon=folium.Icon(color="red")
).add_to(m)

folium.Marker(
    location=loc_bach_khoa,
    popup=f"HCMUT {GATE_DISPLAY_NAMES[START_GATE]}",
    icon=folium.Icon(color="blue")
).add_to(m)

# =========================================================
# DRAW ALL SELECTED VERTICES
# =========================================================

for node in selected_nodes:

    lat = G.nodes[node]["y"]
    lon = G.nodes[node]["x"]

    street_count = G.nodes[node].get("street_count", 0)

    info_html = f"""
    <b>Vertex:</b> {node_to_index[node]}<br>
    <b>Latitude:</b> {lat:.8f}<br>
    <b>Longitude:</b> {lon:.8f}<br>
    <b>Street Count:</b> {street_count}
    """

    vertex_marker = folium.CircleMarker(
        location=[lat, lon],
        radius=7,
        color="white",
        weight=2,
        fill=True,
        fill_color="green",
        fill_opacity=0.9,
        tooltip=folium.Tooltip(info_html, sticky=True)
    )
    folium.Popup(info_html).add_to(vertex_marker)
    
    vertex_marker.add_to(m)

    marker_name = f"vertex_marker_{node_to_index[node]}"
    vertex_marker._name = marker_name

    

# =========================================================
# DRAW K SHORTEST PATHS WITH LAYER CONTROL
# =========================================================

from folium import FeatureGroup

# ---------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------

colors = [
    "#ff0000",  # red
    "#0066ff",  # blue
    "#8a2be2",  # purple
    "#ff8800",  # orange
    "#00aa00",  # green
    "#ff1493",  # pink
    "#00cccc",  # cyan
    "#222222",  # black
    "#999900",
    "#663300",
]

base_weight = 8

# ---------------------------------------------------------
# SHOW ALL PATHS LAYER
# ---------------------------------------------------------

all_paths_group = FeatureGroup(
    name="Show All Paths",
    show=True
)

# ---------------------------------------------------------
# CREATE EACH PATH LAYER
# ---------------------------------------------------------

for idx, path in enumerate(paths):

    color = colors[idx % len(colors)]

    line_weight = max(3, base_weight - idx)

    # -----------------------------------------------------
    # INDIVIDUAL PATH LAYER
    # -----------------------------------------------------

    path_group = FeatureGroup(
        name=f"Path {idx+1} ({lengths[idx]/1000:.2f} km)",
        show=False
    )

    # -----------------------------------------------------
    # BUILD REAL ROAD GEOMETRY
    # -----------------------------------------------------

    route_segments = []

    for u, v in zip(path[:-1], path[1:]):

        edge_data = D.get_edge_data(u, v)

        if edge_data is None:
            continue

        geometry = edge_data.get("geometry", None)

        # REAL ROAD GEOMETRY
        if geometry is not None:

            coords = [
                (lat, lon)
                for lon, lat in geometry.coords
            ]

        else:

            # fallback
            coords = [
                (
                    G.nodes[u]["y"],
                    G.nodes[u]["x"]
                ),
                (
                    G.nodes[v]["y"],
                    G.nodes[v]["x"]
                ),
            ]

        route_segments.extend(coords)

    # -----------------------------------------------------
    # DRAW ON INDIVIDUAL LAYER
    # -----------------------------------------------------

    folium.PolyLine(
        route_segments,
        color=color,
        weight=line_weight,
        opacity=0.9,
        popup=(
            f"""
            <b>Path {idx+1}</b><br>
            Distance: {lengths[idx]/1000:.2f} km
            """
        )
    ).add_to(path_group)

    # -----------------------------------------------------
    # DRAW ON SHOW ALL LAYER
    # -----------------------------------------------------

    folium.PolyLine(
        route_segments,
        color=color,
        weight=line_weight,
        opacity=0.9,
        popup=(
            f"""
            <b>Path {idx+1}</b><br>
            Distance: {lengths[idx]/1000:.2f} km
            """
        )
    ).add_to(all_paths_group)

    # -----------------------------------------------------
    # DRAW NODES OF THIS PATH
    # -----------------------------------------------------

    for node in path:

        lat = G.nodes[node]["y"]
        lon = G.nodes[node]["x"]

        folium.CircleMarker(
            location=[lat, lon],

            # larger node size
            radius=8,

            # white border
            weight=2,
            color="white",

            # node fill
            fill=True,
            fill_color="red",
            fill_opacity=1.0,

            popup=f"""
            <b>Vertex:</b> {node_to_index[node]}<br>
            <b>Node ID:</b> {node}<br>
            <b>Path:</b> {idx+1}<br>
            <b>Latitude:</b> {lat:.8f}<br>
            <b>Longitude:</b> {lon:.8f}
            """
        ).add_to(path_group)

    # -----------------------------------------------------
    # ADD START + END MARKERS
    # -----------------------------------------------------

    first_node = path[0]
    last_node = path[-1]
    first_lat = G.nodes[first_node]["y"]
    first_lon = G.nodes[first_node]["x"]
    last_lat = G.nodes[last_node]["y"]
    last_lon = G.nodes[last_node]["x"]

    folium.Marker(
        location=[
            first_lat,
            first_lon
        ],
        popup=f"""
        <b>Start Path {idx+1}</b><br>
        HCMUT: {GATE_DISPLAY_NAMES[START_GATE]}<br>
        <b>Vertex:</b> {node_to_index[first_node]}<br>
        <b>Latitude:</b> {first_lat:.8f}<br>
        <b>Longitude:</b> {first_lon:.8f}
        """,
        icon=folium.Icon(color="green")
    ).add_to(path_group)

    folium.Marker(
        location=[
            last_lat,
            last_lon
        ],
        popup=f"""
        <b>End Path {idx+1}</b><br>
        Ben Thanh: {GATE_DISPLAY_NAMES[END_GATE]}<br>
        <b>Vertex:</b> {node_to_index[last_node]}<br>
        <b>Latitude:</b> {last_lat:.8f}<br>
        <b>Longitude:</b> {last_lon:.8f}
        """,
        icon=folium.Icon(color="darkred")
    ).add_to(path_group)

    # -----------------------------------------------------
    # ADD LAYER TO MAP
    # -----------------------------------------------------

    path_group.add_to(m)

# ---------------------------------------------------------
# ADD SHOW ALL PATHS LAYER
# ---------------------------------------------------------

all_paths_group.add_to(m)

# ---------------------------------------------------------
# LAYER CONTROL
# ---------------------------------------------------------

folium.LayerControl(
    position="bottomleft",
    collapsed=False
).add_to(m)

# =========================================================
# CUSTOM SCROLLABLE LAYER CONTROL
# =========================================================

custom_css = """
<style>

.leaflet-control-layers-list {
    max-height: 250px;
    overflow-y: auto;
    overflow-x: auto;
    width: 300px;
}

</style>
"""

m.get_root().header.add_child(
    folium.Element(custom_css)
)

# =========================================================
# DRAW EDGES + REAL GEOMETRY + REAL DISTANCE
# =========================================================

drawn_edges = set()

for u, v, data in subgraph.edges(data=True):

    if (u, v) in drawn_edges:
        continue

    drawn_edges.add((u, v))

    length = float(data.get("length", 0))

    # skip artificial connector edges

    # if length <= connector_length:
    #     continue

    if length < MIN_LENGTH_THRESHOLD:
        continue

    geometry = data.get("geometry", None)

    # -----------------------------------------------------
    # USE REAL ROAD GEOMETRY
    # -----------------------------------------------------

    if geometry is not None:

        coords = [
            (lat, lon)
            for lon, lat in geometry.coords
        ]

    else:

        coords = [
            (
                G.nodes[u]["y"],
                G.nodes[u]["x"]
            ),
            (
                G.nodes[v]["y"],
                G.nodes[v]["x"]
            ),
        ]

    # -----------------------------------------------------
    # DRAW ROAD EDGE
    # -----------------------------------------------------

    folium.PolyLine(
        coords,
        color="gray",
        weight=2,
        opacity=0.5,
    ).add_to(m)

    # -----------------------------------------------------
    # PUT DISTANCE LABEL AT MIDDLE OF CURVE
    # -----------------------------------------------------

    middle_index = len(coords) // 2

    mid_lat, mid_lon = coords[middle_index]

    folium.Marker(
        [mid_lat, mid_lon],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size:10px;
                color:black;
                background:white;
                padding:2px;
                border-radius:3px;
                white-space: nowrap;
            ">
                {length:.0f}m
            </div>
            """
        )
    ).add_to(m)

# =========================================================
# EXPORT CSV FOR EACH PATH
# =========================================================

for idx, path in enumerate(paths):

    # -----------------------------------------------------
    # VERTEX CSV
    # -----------------------------------------------------

    vertex_csv = (
        CSV_OUTPUT_FOLDER /
        f"path_{idx+1}_vertices.csv"
    )

    with open(
        vertex_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "vertex_order",
            "node_id",
            "latitude",
            "longitude"
        ])

        for order, node in enumerate(path):

            lat = G.nodes[node]["y"]
            lon = G.nodes[node]["x"]

            writer.writerow([
                order,
                node,
                lat,
                lon
            ])

    # -----------------------------------------------------
    # EDGE CSV
    # -----------------------------------------------------

    edge_csv = (
        CSV_OUTPUT_FOLDER /
        f"path_{idx+1}_edges.csv"
    )

    with open(
        edge_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "from_node",
            "to_node",
            "from_lat",
            "from_lon",
            "to_lat",
            "to_lon",
            "edge_length_m"
        ])

        for u, v in zip(path[:-1], path[1:]):

            edge_data = D.get_edge_data(u, v)

            if edge_data is None:
                continue

            length = edge_data.get("length", 0)

            writer.writerow([

                u,
                v,

                G.nodes[u]["y"],
                G.nodes[u]["x"],

                G.nodes[v]["y"],
                G.nodes[v]["x"],

                length
            ])

print("\nCSV exported successfully")

# =========================================================
# CREATE GRAPH INFO PANEL
# =========================================================

vertex_info_html = f"""
<div id="graph-panel" style="
position: fixed;
top: 10px;
right: 10px;
width: 430px;
height: 700px;
z-index:9999;
background:white;
border:2px solid black;
padding:10px;
font-size:12px;
font-family:monospace;
">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
">

<h2 style="margin:0;">
GRAPH INFORMATION
</h2>

<div>

<button onclick="expandPanel()" style="
width:30px;
height:30px;
font-size:18px;
cursor:pointer;
">
+
</button>

<button onclick="collapsePanel()" style="
width:30px;
height:30px;
font-size:18px;
cursor:pointer;
">
-
</button>

</div>

</div>

<div id="graph-content">

<br>

<b>Total Vertices:</b> {len(selected_nodes_list)}<br>
<b>Total Edges:</b> {len(subgraph.edges)}<br>

<hr>

<h3>VERTICES</h3>

<div style="
height:250px;
overflow:auto;
border:1px solid gray;
padding:5px;
">

<pre>
STT | LATITUDE | LONGITUDE
"""

for idx, node in enumerate(selected_nodes_list):

    lat = G.nodes[node]["y"]
    lon = G.nodes[node]["x"]

    vertex_info_html += (
        f'<span '
        f'style="cursor:pointer;color:blue;" '
        f'onclick="focusVertex({idx})">'
        f'{idx:03d}'
        f'</span> | '
        f'{lat:.8f} | '
        f'{lon:.8f}\n'
    )

vertex_coords = {
    idx: [
        G.nodes[node]["y"],
        G.nodes[node]["x"],
    ]
    for idx, node in enumerate(selected_nodes_list)
}

vertex_info_html += """
</pre>

</div>

<hr>

<h3>EDGES</h3>

<div style="
height:250px;
overflow:auto;
border:1px solid gray;
padding:5px;
">

<pre>
FROM | TO | DISTANCE(m)
"""

for u, v, data in subgraph.edges(data=True):

    if (
        u not in node_to_index
        or
        v not in node_to_index
    ):
        continue

    u_idx = node_to_index[u]
    v_idx = node_to_index[v]

    length = float(data.get("length", 0))

    edge_coords = []

    geometry = data.get("geometry", None)

    if geometry is not None:

        for lon, lat in geometry.coords:
            edge_coords.append([lat, lon])

    else:

        edge_coords = [
            [G.nodes[u]["y"], G.nodes[u]["x"]],
            [G.nodes[v]["y"], G.nodes[v]["x"]]
        ]

    vertex_info_html += (
        f'<span '
        f'style="cursor:pointer;color:red;" '
        f'onclick=\'focusEdge({edge_coords})\'>'
        f'{u_idx:03d} | {v_idx:03d}'
        f'</span> | '
        f'{length:.2f}\n'
    )

vertex_info_html += """
</pre>

</div>

<hr>

<h3>DOWNLOAD FILES</h3>

<a href="graph.txt" download>
<button style="width:100%;padding:8px;">
Download graph.txt
</button>
</a>

<br><br>

<a href="list_vertex/path_1_vertices.csv" download>
<button style="width:100%;padding:8px;">
Download vertices CSV
</button>
</a>

<br><br>

<a href="list_vertex/path_1_edges.csv" download>
<button style="width:100%;padding:8px;">
Download edges CSV
</button>
</a>

</div>

<script>

const vertexCoords = __VERTEX_COORDS__;

function getVertexMarker(vertexId) {

    let coords = vertexCoords[vertexId];

    if (!coords) {
        return null;
    }

    let foundMarker = null;

    __MAP_NAME__.eachLayer(function(layer) {

        if (
            foundMarker !== null ||
            typeof layer.getLatLng !== "function" ||
            typeof layer.openPopup !== "function"
        ) {
            return;
        }

        let latLng = layer.getLatLng();

        if (
            Math.abs(latLng.lat - coords[0]) < 0.00000001 &&
            Math.abs(latLng.lng - coords[1]) < 0.00000001
        ) {
            foundMarker = layer;
        }
    });

    return foundMarker;
}

function focusVertex(vertexId) {

    let coords = vertexCoords[vertexId];

    if (!coords) {
        return;
    }

    __MAP_NAME__.setView(
        coords,
        18
    );

    let marker = getVertexMarker(vertexId);

    if (marker) {
        marker.openPopup();
    }
}

let currentEdge = null;

function focusEdge(coords) {

    if (currentEdge !== null) {
        __MAP_NAME__.removeLayer(currentEdge);
    }

    currentEdge = L.polyline(
        coords,
        {
            color: 'red',
            weight: 6,
            opacity: 0.8,
            lineJoin: 'round'
        }
    ).addTo(__MAP_NAME__);

    __MAP_NAME__.fitBounds(
        currentEdge.getBounds(),
        {padding: [50, 50]}
    );
}

function collapsePanel() {

    document.getElementById("graph-content").style.display = "none";

    document.getElementById("graph-panel").style.width = "250px";

    document.getElementById("graph-panel").style.height = "60px";

}

function expandPanel() {

    document.getElementById("graph-content").style.display = "block";

    document.getElementById("graph-panel").style.width = "430px";

    document.getElementById("graph-panel").style.height = "700px";

}

window.focusVertex = focusVertex;
window.focusEdge = focusEdge;
window.collapsePanel = collapsePanel;
window.expandPanel = expandPanel;

</script>

</div>
""".replace(
    "__MAP_NAME__",
    map_name
).replace(
    "__VERTEX_COORDS__",
    json.dumps(vertex_coords)
)

m.get_root().html.add_child(
    folium.Element(vertex_info_html)
)

# =========================================================
# SAVE HTML
# =========================================================

m.save(OUTPUT_HTML)

print("\n=================================================")
print("DONE")
print("=================================================")

print(f"HTML map saved as:")
print(OUTPUT_HTML)

print("\nOpen the HTML file in browser.")
print("You can zoom, click nodes, and inspect edges.")

# =========================================================
# EXPORT GRAPH.TXT
# =========================================================

graph_txt = "graph.txt"


# ---------------------------------------------------------
# WRITE GRAPH
# ---------------------------------------------------------

with open(graph_txt, "w", encoding="utf-8") as f:

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    f.write(f"VERTICES {len(selected_nodes_list)}\n\n")

    # -----------------------------------------------------
    # WRITE ALL VERTICES
    # -----------------------------------------------------

    for idx, node in enumerate(selected_nodes_list):

        lat = G.nodes[node]["y"]
        lon = G.nodes[node]["x"]

        f.write(
            f"{idx} {lat:.8f} {lon:.8f}\n"
        )

    # -----------------------------------------------------
    # EDGES
    # -----------------------------------------------------

    f.write("\nEDGES\n\n")

    written_edges = set()

    for u, v, data in subgraph.edges(data=True):

        # avoid duplicate edges
        edge_key = tuple(sorted((str(u), str(v))))

        if edge_key in written_edges:
            continue

        written_edges.add(edge_key)

        # only export edges between selected nodes
        if (
            u not in node_to_index
            or
            v not in node_to_index
        ):
            continue

        u_idx = node_to_index[u]
        v_idx = node_to_index[v]

        length = float(
            data.get("length", 0)
        )

        f.write(
            f"{u_idx} "
            f"{v_idx} "
            f"{length:.2f}\n"
        )

print("\ngraph.txt exported successfully")

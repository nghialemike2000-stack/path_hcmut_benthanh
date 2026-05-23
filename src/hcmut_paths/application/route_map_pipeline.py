from __future__ import annotations

from hcmut_paths.algorithms.gate_selector import find_best_gate_pair
from hcmut_paths.algorithms.k_shortest_paths import (
    find_k_shortest_paths,
    route_lengths,
    display_path,
)
from hcmut_paths.config.gates import (
    BACH_KHOA_GATES,
    BEN_THANH_GATES,
    GATE_DISPLAY_NAMES,
    initial_bbox_coordinates,
)
from hcmut_paths.config.settings import AppSettings
from hcmut_paths.domain.models import Coordinate, PipelineResult
from hcmut_paths.exporters.graph_txt_exporter import export_graph_txt
from hcmut_paths.exporters.html_exporter import export_html_map
from hcmut_paths.exporters.path_csv_exporter import export_path_csv_files
from hcmut_paths.graph.directed_graph_builder import to_weighted_digraph
from hcmut_paths.graph.gate_connector import connect_gate_nodes, nearest_node
from hcmut_paths.graph.node_indexer import build_node_index
from hcmut_paths.graph.osm_loader import build_bbox, load_consolidated_graph
from hcmut_paths.graph.subgraph_builder import (
    add_nearby_intersections,
    build_subgraph,
    collect_route_nodes,
)
from hcmut_paths.rendering.edge_renderer import render_subgraph_edges
from hcmut_paths.rendering.folium_map_factory import create_base_map
from hcmut_paths.rendering.graph_panel_renderer import render_graph_info_panel
from hcmut_paths.rendering.layer_control_renderer import (
    inject_layer_control_styles,
    render_layer_control,
)
from hcmut_paths.rendering.location_marker_renderer import render_main_location_markers
from hcmut_paths.rendering.path_layer_renderer import render_path_layers
from hcmut_paths.rendering.vertex_renderer import render_selected_vertices
import time


class RouteMapPipeline:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def run(self) -> PipelineResult:
        initial_bach_khoa, initial_ben_thanh = initial_bbox_coordinates()
        bbox = build_bbox(
            initial_bach_khoa,
            initial_ben_thanh,
            self.settings.lat_padding,
            self.settings.lon_padding,
        )

        print("Downloading map data...")
        print("Downloading and consolidating map data...")

        graph = load_consolidated_graph(
            bbox,
            self.settings.custom_filter,
            self.settings.intersection_tolerance_m,
        )

        print(f"Consolidated graph loaded:")
        print(f"Nodes: {len(graph.nodes)}")
        print(f"Edges: {len(graph.edges)}")

        directed_graph = to_weighted_digraph(graph)

        gate_selection, attempts = find_best_gate_pair(
            graph,
            directed_graph,
            BACH_KHOA_GATES,
            BEN_THANH_GATES,
        )

        for attempt in attempts:
            if attempt.skipped:
                print(f"Skip {attempt.start_gate} -> {attempt.end_gate}")
            else:
                print(
                    f"{attempt.start_gate} -> {attempt.end_gate} "
                    f"= {attempt.distance_m / 1000:.2f} km"
                )

        print("\n================================")
        print("BEST GATE COMBINATION")
        print("================================")
        print(f"HCMUT : {gate_selection.start_gate}")
        print(f"Ben Thanh : {gate_selection.end_gate}")
        print(f"Distance : {gate_selection.distance_m/1000:.2f} km")

        bach_khoa_coordinate = BACH_KHOA_GATES[gate_selection.start_gate]
        ben_thanh_coordinate = BEN_THANH_GATES[gate_selection.end_gate]

        origin = nearest_node(graph, bach_khoa_coordinate)
        destination = nearest_node(graph, ben_thanh_coordinate)

        real_origin_node = origin
        real_destination_node = destination

        print(f"\nOrigin node: {origin}")
        print(f"Destination node: {destination}")

        connector_result = connect_gate_nodes(
            graph,
            origin,
            destination,
            bach_khoa_coordinate,
            ben_thanh_coordinate,
            self.settings.origin_gate_node,
            self.settings.destination_gate_node,
        )

        print(
            f"HCMUT gate connector = "
            f"{connector_result.origin_connector_length_m:.2f} meters"
        )
        print(
            f"Ben Thanh connector = "
            f"{connector_result.destination_connector_length_m:.2f} meters"
        )

        print("\n================================")
        print("FINAL REAL DISTANCE")
        print("================================")

        real_distance = (
            gate_selection.distance_m
            + connector_result.origin_connector_length_m
            + connector_result.destination_connector_length_m
        )

        print(f"Road distance : " f"{gate_selection.distance_m / 1000:.2f} km")

        print(
            f"Connector distance : "
            f"{(connector_result.origin_connector_length_m + connector_result.destination_connector_length_m)/1000:.2f} km"
        )

        print(f"Final distance : " f"{real_distance / 1000:.2f} km")

        directed_graph = to_weighted_digraph(graph)
        origin = connector_result.origin_gate_node
        destination = connector_result.destination_gate_node

        print(f"\nFinding {self.settings.k_paths} shortest paths...")

        start_time = time.perf_counter()

        paths, explanation_data, execution_ms = find_k_shortest_paths(
            directed_graph,
            origin,
            destination,
            self.settings.k_paths,
            {},
        )

        end_time = time.perf_counter()

        print(f"\nYen execution time: " f"{(end_time - start_time)*1000:.2f} ms")

        print(f"Found {len(paths)} paths")

        lengths = route_lengths(directed_graph, paths)

        selected_nodes = collect_route_nodes(paths)

        if len(selected_nodes) < self.settings.target_vertices:
            print(
                f"\nAdding more intersections with "
                f"{self.settings.min_node_gap_m:g}m gap..."
            )
            selected_nodes = add_nearby_intersections(
                graph,
                selected_nodes,
                bach_khoa_coordinate,
                ben_thanh_coordinate,
                self.settings.target_vertices,
                self.settings.min_node_gap_m,
            )

        print(f"\nSelected vertices: {len(selected_nodes)}")
        selected_nodes_list, node_to_index = build_node_index(selected_nodes)

        real_node_labels = {
            "HCMUT_GATE": node_to_index.get(real_origin_node),
            "BEN_THANH_GATE": node_to_index.get(real_destination_node),
        }

        print("\n================================")
        print("VERTEX TABLE")
        print("================================")

        vertex_lines = []

        for node in selected_nodes_list:

            idx = node_to_index[node]

            lat = graph.nodes[node]["y"]
            lon = graph.nodes[node]["x"]

            line = f"Vertex {idx}: " f"lat={lat:.8f}, " f"lon={lon:.8f}"

            print(line)

            vertex_lines.append(line)

        with open(
            "vertex_table.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write("\n".join(vertex_lines))

        explanation_lines = []

        explanation_lines.append(
            f"K shortest paths requested = {self.settings.k_paths}"
        )

        explanation_lines.append("")

        for item in explanation_data:

            if item["type"] == "initial":

                explanation_lines.append("========================================")

                explanation_lines.append("STEP 1")

                explanation_lines.append("========================================")

                explanation_lines.append("Initial shortest path:")

                explanation_lines.append(
                    display_path(
                        item["path"],
                        node_to_index,
                        directed_graph,
                        real_node_labels,
                    )
                )

                explanation_lines.append(f"Cost = {item['cost']/1000:.3f} km")

                explanation_lines.append("")

                explanation_lines.append(f"Total edges = {len(item['path']) - 1}")

                explanation_lines.append("")

                explanation_lines.append(
                    "Yen Algorithm now cuts each edge one-by-one to generate alternative paths."
                )

                explanation_lines.append("")

            elif item["type"] == "iteration":

                explanation_lines.append("========================================")

                explanation_lines.append(f"ITERATION {item['iteration']}")

                remaining_k = self.settings.k_paths - item["iteration"]

                explanation_lines.append(
                    f"Searching for path K = {item['iteration'] + 1}"
                )

                explanation_lines.append(f"Remaining paths to discover = {remaining_k}")

                explanation_lines.append(
                    "Yen algorithm removes one edge from the previous shortest path to generate alternative candidates."
                )

                explanation_lines.append("========================================")

                explanation_lines.append("")

                for spur in item["spur_operations"]:

                    explanation_lines.append(f"SPUR EDGE INDEX = {spur['spur_index']}")

                    if spur.get("failed"):

                        explanation_lines.append("No valid spur path found.")

                        explanation_lines.append("")
                        continue

                    explanation_lines.append("Root path:")

                    explanation_lines.append(
                        display_path(
                            spur["root_path"],
                            node_to_index,
                            directed_graph,
                            real_node_labels,
                        )
                    )

                    explanation_lines.append("")

                    explanation_lines.append("Candidate path:")

                    explanation_lines.append(
                        display_path(
                            spur["candidate_path"],
                            node_to_index,
                            directed_graph,
                            real_node_labels,
                        )
                    )

                    explanation_lines.append("")

                    explanation_lines.append(
                        f"Candidate cost = {spur['candidate_cost']/1000:.3f} km"
                    )

                    explanation_lines.append("")

                    if spur["inserted"]:

                        explanation_lines.append("Inserted into heap.")

                    else:

                        explanation_lines.append("Ignored because path already exists.")

                    explanation_lines.append("")

                    explanation_lines.append(f"Heap size = {spur['heap_size']}")

                    explanation_lines.append("")

                    explanation_lines.append("Current heap:")

                    for heap_item in spur["heap_snapshot"]:

                        explanation_lines.append(
                            f"[{heap_item['heap_index']}] "
                            f"{heap_item['cost']/1000:.3f} km"
                        )

                        explanation_lines.append(
                            display_path(
                                heap_item["path"],
                                node_to_index,
                                directed_graph,
                                real_node_labels,
                            )
                        )

                    explanation_lines.append("")

            elif item["type"] == "selected":

                explanation_lines.append("========================================")

                explanation_lines.append(
                    f"SELECTED PATH FOR K = {item['iteration'] + 1}"
                )

                explanation_lines.append("========================================")

                explanation_lines.append(
                    display_path(
                        item["path"],
                        node_to_index,
                        directed_graph,
                        real_node_labels,
                    )
                )

                explanation_lines.append(f"Cost = {item['cost']/1000:.3f} km")

                explanation_lines.append(f"Remaining heap = {item['heap_remaining']}")

                explanation_lines.append("")

        explanation_lines.append("========================================")

        explanation_lines.append("FINAL SUMMARY")

        explanation_lines.append("========================================")

        explanation_lines.append(f"Execution Time = {execution_ms:.2f} ms")

        explanation_lines.append(f"Total paths found: {len(paths)}")
        explanation_lines.append("")

        for idx, path in enumerate(paths):
            length = lengths[idx]
            explanation_lines.append(f"Path [{idx}] - {length / 1000:.3f} km")
            explanation_lines.append(
                display_path(
                    path,
                    node_to_index,
                    directed_graph,
                    real_node_labels,
                )
            )
            explanation_lines.append("")
            
        with open(
            "shortest_path_yen_algorithms_heapify.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write("\n".join(explanation_lines))

        for idx, path in enumerate(paths):

            length = lengths[idx]

            print(f"\n================================")
            print(f"Path {idx+1}")
            print(f"================================")

            print(f"Distance: {length / 1000:.2f} km")

            print(f"Vertices: {len(path)}")

            print("Route:")

            print(
                display_path(
                    path,
                    node_to_index,
                    directed_graph,
                    real_node_labels,
                )
            )

        subgraph = build_subgraph(graph, selected_nodes)

        print(f"Subgraph nodes: {len(subgraph.nodes)}")
        print(f"Subgraph edges: {len(subgraph.edges)}")

        center = Coordinate(
            lat=(ben_thanh_coordinate.lat + bach_khoa_coordinate.lat) / 2,
            lon=(ben_thanh_coordinate.lon + bach_khoa_coordinate.lon) / 2,
        )

        map_obj = create_base_map(center)
        map_name = map_obj.get_name()

        render_main_location_markers(
            map_obj,
            ben_thanh_coordinate,
            bach_khoa_coordinate,
            gate_selection.end_gate,
            gate_selection.start_gate,
            GATE_DISPLAY_NAMES,
        )
        render_selected_vertices(
            map_obj,
            graph,
            selected_nodes,
            node_to_index,
        )

        all_paths_group = render_path_layers(
            map_obj,
            graph,
            directed_graph,
            paths,
            lengths,
            node_to_index,
            GATE_DISPLAY_NAMES,
            gate_selection.start_gate,
            gate_selection.end_gate,
            self.settings.path_colors,
            self.settings.base_path_weight,
        )
        all_paths_group.add_to(map_obj)

        render_layer_control(map_obj)
        inject_layer_control_styles(map_obj)

        render_subgraph_edges(
            map_obj,
            graph,
            subgraph,
            self.settings.min_length_threshold_m,
        )

        export_path_csv_files(
            self.settings.csv_output_folder,
            graph,
            directed_graph,
            paths,
        )

        print("\nCSV exported successfully")

        render_graph_info_panel(
            map_obj,
            map_name,
            graph,
            subgraph,
            selected_nodes_list,
            node_to_index,
        )

        export_html_map(map_obj, self.settings.output_html)

        print("\n=================================================")
        print("DONE")
        print("=================================================")
        print(f"HTML map saved as:")
        print(self.settings.output_html)
        print("\nOpen the HTML file in browser.")
        print("You can zoom, click nodes, and inspect edges.")

        export_graph_txt(
            self.settings.graph_txt_path,
            graph,
            subgraph,
            selected_nodes_list,
            node_to_index,
        )

        print("\ngraph.txt exported successfully")

        return PipelineResult(
            html_path=self.settings.output_html,
            graph_txt_path=self.settings.graph_txt_path,
        )

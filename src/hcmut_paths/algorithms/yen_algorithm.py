from __future__ import annotations

import heapq
import time
import networkx as nx


def edge_distance(graph, u, v):

    return graph[u][v]["length"] / 1000


def path_cost(graph, path):

    total = 0

    for u, v in zip(path[:-1], path[1:]):
        total += graph[u][v]["length"]

    return total


def detailed_path(graph, path):

    output = []

    for u, v in zip(path[:-1], path[1:]):

        dist = edge_distance(graph, u, v)

        output.append(
            (u, v, dist)
        )

    return output


def yen_k_shortest_paths(
    graph,
    source,
    target,
    k,
):

    start_time = time.perf_counter()

    explanation_data = []

    shortest_path = nx.dijkstra_path(
        graph,
        source,
        target,
        weight="length",
    )

    A = [shortest_path]

    B = []

    explanation_data.append(
        {
            "type": "initial",
            "path": shortest_path,
            "cost": path_cost(graph, shortest_path),
            "edges": detailed_path(
                graph,
                shortest_path,
            ),
        }
    )

    for kth in range(1, k):

        previous_path = A[-1]

        iteration_data = {
            "type": "iteration",
            "iteration": kth,
            "spur_operations": [],
        }

        for i in range(len(previous_path) - 1):

            spur_node = previous_path[i]

            root_path = previous_path[: i + 1]

            graph_copy = graph.copy()

            removed_edges = []

            for path in A:

                if (
                    len(path) > i
                    and path[: i + 1] == root_path
                ):

                    u = path[i]
                    v = path[i + 1]

                    if graph_copy.has_edge(u, v):

                        graph_copy.remove_edge(u, v)

                        removed_edges.append((u, v))

            try:

                spur_path = nx.dijkstra_path(
                    graph_copy,
                    spur_node,
                    target,
                    weight="length",
                )

                total_path = root_path[:-1] + spur_path

                if len(total_path) != len(set(total_path)):
                    continue

                total_cost = path_cost(
                    graph,
                    total_path,
                )

                candidate_exists = any(
                    heap_item[1] == total_path
                    for heap_item in B
                )

                accepted_exists = any(
                    accepted_path == total_path
                    for accepted_path in A
                )

                inserted = False

                if (
                    not candidate_exists
                    and not accepted_exists
                ):

                    heapq.heappush(
                        B,
                        (
                            total_cost,
                            total_path,
                            spur_node,
                            root_path,
                        ),
                    )

                    inserted = True
                    remaining_needed = k - len(A)
                    if len(B) > remaining_needed:
                        B = heapq.nsmallest(remaining_needed, B)
                        heapq.heapify(B)

                heap_snapshot = []

                for idx, heap_item in enumerate(sorted(B)):

                    heap_snapshot.append(
                        {
                            "heap_index": idx,
                            "cost": heap_item[0],
                            "path": heap_item[1],
                        }
                    )

                iteration_data["spur_operations"].append(
                    {
                        "spur_index": i,
                        "spur_node": spur_node,
                        "root_path": root_path,
                        "candidate_path": total_path,
                        "candidate_cost": total_cost,
                        "inserted": inserted,
                        "heap_size": len(B),
                        "heap_snapshot": heap_snapshot,
                        "edges": detailed_path(
                            graph,
                            total_path,
                        ),
                    }
                )

            except nx.NetworkXNoPath:

                iteration_data["spur_operations"].append(
                    {
                        "spur_index": i,
                        "spur_node": spur_node,
                        "root_path": root_path,
                        "failed": True,
                    }
                )

        explanation_data.append(iteration_data)

        if not B:
            break

        (
            best_cost,
            best_candidate,
            best_spur_node,
            best_root_path,
        ) = heapq.heappop(B)

        A.append(best_candidate)

        explanation_data.append(
            {
                "type": "selected",
                "iteration": kth,
                "path": best_candidate,
                "cost": best_cost,
                "heap_remaining": len(B),
            }
        )

    execution_ms = (
        time.perf_counter() - start_time
    ) * 1000

    return (
        A,
        explanation_data,
        execution_ms,
    )
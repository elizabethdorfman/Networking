import math
import sys


def calc_bellman_ford(source_node):
    distances = [math.inf] * num_nodes
    distances[source_node] = 0

    for iteration in range(num_nodes - 1):
        for from_node in range(num_nodes):
            for to_node in range(num_nodes):
                if matrix[from_node][to_node] != math.inf:
                    if (
                        distances[from_node] + matrix[from_node][to_node]
                        < distances[to_node]
                    ):
                        distances[to_node] = (
                            distances[from_node] + matrix[from_node][to_node]
                        )

    for from_node in range(num_nodes):
        for to_node in range(num_nodes):
            if matrix[from_node][to_node] != math.inf:
                if (
                    distances[from_node] + matrix[from_node][to_node]
                    < distances[to_node]
                ):
                    return [None] * num_nodes

    return distances


def print_bellman_ford(num_nodes, matrix):
    for source_node in range(num_nodes):
        distances = calc_bellman_ford(source_node)
        print(f"Node {source_node}: {distances}")


if __name__ == "__main__":
    input_file = sys.stdin.read

    matrix_data = input_file().splitlines()

    num_nodes = int(matrix_data[0])

    matrix = []

    for row_index in range(num_nodes):
        matrix.append([])
        for col_index in range(num_nodes):
            num_to_insert = matrix_data[1 + row_index * num_nodes + col_index]
            if num_to_insert == "f":
                matrix[row_index].append(float("inf"))
            else:
                matrix[row_index].append(int(num_to_insert))

    print_bellman_ford(num_nodes, matrix)

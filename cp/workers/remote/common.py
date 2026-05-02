"""Shared helpers for cluster workers."""


def get_node_count_per_zone(zone_count: int, node_count: int) -> list[int]:
    """Distribute nodes across zones as evenly as possible."""
    counts = [0] * zone_count
    index = 0

    for _ in range(node_count):
        counts[index] += 1
        index += 1
        if index == zone_count:
            index = 0

    return counts

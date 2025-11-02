#!/usr/bin/env python3
import sys
from collections import defaultdict, deque


def solve(edges: list[tuple[str, str]]) -> list[str]:
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    all_nodes = set(adj.keys())
    all_sh = {n for n in all_nodes if n.isupper()}
    all_gates = []
    for sh in all_sh:
        for node in adj[sh]:
            if node.islower():
                all_gates.append((sh, node))

    def is_connected(u, v, disc):
        if u.isupper() and v.islower():
            return (u, v) not in disc
        elif v.isupper() and u.islower():
            return (v, u) not in disc
        else:
            return True

    inf = float('inf')

    def compute_dists(start, disc):
        dist = {n: inf for n in all_nodes}
        dist[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if is_connected(u, v, disc) and dist[v] > dist[u] + 1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    memo = {}

    def get_sequence(pos, disc):
        disc_fs = frozenset(disc)
        key = (pos, disc_fs)
        if key in memo:
            return memo[key]
        dists = compute_dists(pos, disc)
        reach_d = {sh: dists[sh] for sh in all_sh}
        min_d = min(reach_d.values())
        if min_d == inf:
            memo[key] = []
            return []
        remaining = [g for g in all_gates if g not in disc]
        sorted_rem = sorted(remaining)
        for gate in sorted_rem:
            new_disc = disc | {gate}
            new_dists = compute_dists(pos, new_disc)
            new_reach_d = {sh: new_dists[sh] for sh in all_sh}
            new_min_d = min(new_reach_d.values())
            if new_min_d == inf:
                seq = [f"{gate[0]}-{gate[1]}"]
                memo[key] = seq
                return seq
            cand_sh = [sh for sh, d in new_reach_d.items() if d == new_min_d]
            target = min(cand_sh)
            dist_to_target = compute_dists(target, new_disc)
            possible_next = []
            for neigh in adj[pos]:
                if is_connected(pos, neigh, new_disc) and dist_to_target[neigh] == dist_to_target[pos] - 1:
                    possible_next.append(neigh)
            if not possible_next:
                continue
            next_pos = min(possible_next)
            if next_pos.isupper():
                continue
            sub = get_sequence(next_pos, new_disc)
            if sub is not None:
                seq = [f"{gate[0]}-{gate[1]}"] + sub
                memo[key] = seq
                return seq
        memo[key] = None
        return None

    result = get_sequence('a', set())
    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()

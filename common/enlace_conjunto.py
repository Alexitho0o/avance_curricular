"""Emparejamiento bipartito y pares forzados bajo máxima cardinalidad."""
from collections import defaultdict


def matching(graph, forbidden=None):
    """Un máximo; sus elecciones arbitrarias nunca se publican como enlaces."""
    owner = {}
    def augment(u, seen):
        for v in sorted(graph[u]):
            if (u, v) == forbidden or v in seen:
                continue
            seen.add(v)
            if v not in owner or augment(owner[v], seen):
                owner[v] = u
                return True
        return False
    for u in sorted(graph):
        augment(u, set())
    return {u: v for v, u in owner.items()}


def solve(graph):
    """Componentes, cardinalidad máxima y aristas presentes en todos los máximos."""
    reverse = defaultdict(set)
    for u, vv in graph.items():
        for v in vv:
            reverse[v].add(u)
    pending = set(graph)
    forced, components = {}, []
    while pending:
        start = min(pending)
        left, right, queue = {start}, set(), [start]
        while queue:
            u = queue.pop()
            for v in graph[u] - right:
                right.add(v)
                for other in reverse[v] - left:
                    left.add(other)
                    queue.append(other)
        pending -= left
        sub = {u: graph[u] for u in left}
        maximum = matching(sub)
        fixed = {u: v for u, v in maximum.items()
                 if len(matching(sub, (u, v))) < len(maximum)}
        forced.update(fixed)
        components.append({'personas_umas': len(left), 'personas_mrun_candidatas': len(right),
                           'maximo_pares': len(maximum), 'pares_forzados_condicionales': len(fixed)})
    return forced, components

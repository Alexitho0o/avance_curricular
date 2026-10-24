"""Contrasta los pares forzados con enumeración independiente de todos los máximos."""
import itertools
import unittest
from common.enlace_conjunto import solve

class TestEnlace(unittest.TestCase):
    def test_all_three_by_three_graphs(self):
        edges = list(itertools.product(range(3), range(3)))
        for mask in range(512):
            graph = {u: {v for i,(a,v) in enumerate(edges) if a==u and mask>>i&1} for u in range(3)}
            assignments = []
            for choice in itertools.product(*[[None]+sorted(graph[u]) for u in range(3)]):
                values = [v for v in choice if v is not None]
                if len(set(values)) == len(values):
                    assignments.append({(u,v) for u,v in enumerate(choice) if v is not None})
            size = max(map(len, assignments))
            expected = set.intersection(*(a for a in assignments if len(a)==size))
            forced, components = solve(graph)
            self.assertEqual(set(forced.items()), expected)
            self.assertEqual(sum(c['maximo_pares'] for c in components), size)
    def test_joint_resolution(self):
        forced, _ = solve({'a': {'x'}, 'b': {'x','y'}, 'c': {'y','z'}})
        self.assertEqual(forced, {'a':'x','b':'y','c':'z'})

if __name__ == '__main__': unittest.main()

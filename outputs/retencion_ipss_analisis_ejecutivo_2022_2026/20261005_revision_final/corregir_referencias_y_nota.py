"""Corrección mínima OOXML sobre una copia guardada/recalculada por Excel.

Entrada: copia derivada del libro 20261002_181327, guardada con Excel.
Salida: la misma copia derivada, sin tocar el original.
Conserva datos, fórmulas de celda, estilos y objetos; corrige referencias
de gráficos al libro local y una nota contradictoria.
"""
from pathlib import Path
import re
import zipfile
from xml.sax.saxutils import escape

path = Path('/Users/alexi/Desktop/RETENCION_IPSS_FINAL_REVISADO_20261005.xlsx')
old = 'Conclusión: la caída de retención entre 2022-2023 y 2024-2025 es real y consistente con lo publicado por SIES — la brecha entre la cifra interna y la oficial se mantiene acotada (menor a 2 puntos porcentuales) en los cuatro años.'
new = 'Lectura de los resultados (B/C/E): las tasas internas y las publicadas por SIES son cercanas en 2023 y 2025. En 2022 la tasa interna supera a SIES en 4,49 puntos porcentuales y en 2024 queda 9,08 puntos por debajo. Estas dos brechas siguen sin una causa completamente verificada; el gráfico conserva ambas series para mostrar la diferencia.'
with zipfile.ZipFile(path) as book:
    entries = [(info, book.read(info.filename)) for info in book.infolist()]
changed = []
count = 0
result = []
for info, data in entries:
    name = info.filename
    if name.startswith('xl/externalLinks/'):
        changed.append(name + ': eliminado vínculo externo heredado')
        continue
    before = data
    if name.startswith('xl/charts/chart') and name.endswith('.xml'):
        count += data.count(b'[1]!RET_')
        data = data.replace(b'[1]!RET_', (path.name + '!RET_').encode())
    elif name == 'xl/sharedStrings.xml':
        assert data.count(escape(old).encode()) == 1
        data = data.replace(escape(old).encode(), escape(new).encode())
    elif name == 'xl/workbook.xml':
        data = re.sub(rb'<externalReferences>.*?</externalReferences>', b'', data)
    elif name == 'xl/_rels/workbook.xml.rels':
        data = re.sub(rb'<Relationship\b[^>]*Type="[^"]*/externalLink"[^>]*/>', b'', data)
    elif name == '[Content_Types].xml':
        data = re.sub(rb'<Override\b[^>]*PartName="/xl/externalLinks/[^"]*"[^>]*/>', b'', data)
    if before != data:
        changed.append(name)
    result.append((info, data))
assert count == 18, count
temp = path.with_suffix('.tmp.xlsx')
with zipfile.ZipFile(temp, 'w') as book:
    for info, data in result:
        book.writestr(info, data)
with zipfile.ZipFile(temp) as book:
    assert book.testzip() is None
temp.replace(path)
print('Referencias de gráfico corregidas:', count)
print('Partes modificadas:', changed)

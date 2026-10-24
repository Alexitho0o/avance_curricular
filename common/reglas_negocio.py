"""Reglas internas explícitas, separadas de los atributos formales SIES.

Contrato: docs/unificacion_proyectos_y_reglas_negocio_20261015.md.
No asigna mallas UMAS ni modifica las reglas de cargas congeladas.
"""
from __future__ import annotations


def inicio_codigo_oferta(registros, codigo_unico):
    """Primera oferta del código completo, incluso sin matrícula/vigencia actual.

Entrada: proyección H5 con anio y codigo_unico. No consulta ANO_INICIO,
matrícula, etiqueta de plan, nombre, familia ni vigencia para elegir el inicio.
La cobertura describe la fuente recibida, no una fecha de creación inferida.
"""
    if not isinstance(codigo_unico, str) or not codigo_unico:
        raise ValueError('Código Único literal obligatorio')
    coverage, years = set(), set()
    for row in registros:
        year = row['anio']
        if type(year) is not int or not 1900 <= year <= 2200:
            raise ValueError('Año de oferta debe ser entero válido')
        coverage.add(year)
        if row['codigo_unico'] == codigo_unico:
            years.add(year)
    first = min(years) if years else None
    return {'regla': 'INT-OFERTA-INICIO-001', 'codigo_unico': codigo_unico,
            'anio_inicio_diccionario': first, 'anios_ofertados': sorted(years),
            'cobertura_fuente': sorted(coverage),
            'coincide_limite_inferior_fuente': bool(years and first == min(coverage)),
            'estado': 'OFERTA_LOCALIZADA' if years else 'SIN_OFERTA_EN_FUENTE',
            'campo_formal_anio_inicio_sustituido': False}

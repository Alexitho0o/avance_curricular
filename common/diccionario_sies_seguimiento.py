"""Consulta única de códigos SIES por expediente/contexto; no calcula retención."""
import copy
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rut_normalizado(value):
    """Normalización de la reproducción vigente; requiere DV, no lo inventa."""
    s = str(value).upper().replace('.', '').replace(' ', '')
    if not re.fullmatch(r'\d+-[0-9K]', s):
        raise ValueError('Identidad RUT con DV requerida; no se realiza cruce aproximado')
    body, dv = s.split('-')
    return str(int(body)) + '-' + dv


def aplicar_adjudicaciones(rows, operations):
    result = copy.deepcopy(rows)
    index = {r['observacion_id']: r for r in result}
    if len(index) != len(result):
        raise ValueError('Observaciones duplicadas')
    allowed = {'codigo_interno_adoptado', 'estado_interno', 'regla', 'clasificacion', 'requisito_pendiente'}
    for op in operations:
        row = index[op['observacion_id']]
        before, after = op['estado_antes'], op['estado_despues']
        if set(before) != set(after) or any(before[k] != after[k] for k in before if k not in allowed):
            raise ValueError('Operación altera campos fuera de autorización')
        if row == after:
            continue
        if row != before:
            raise ValueError('Estado previo incompatible con adjudicación')
        row.clear()
        row.update(copy.deepcopy(after))
    return result


class DiccionarioSiesSeguimiento:
    """Lee una instantánea verificada; no escribe ni consulta servicios externos."""
    def __init__(self, root=None, descriptor=None):
        self.root = Path(root or ROOT).resolve()
        if descriptor is None:
            project = json.loads((self.root / 'PROYECTO_IPSS.json').read_text())
            active = json.loads((self.root / project['recursos_comunes']['diccionario_sies_seguimiento']).read_text())
            descriptor = self.root / active['descriptor']
            if sha256(descriptor) != active['sha256']:
                raise ValueError('Descriptor alterado')
        self.descriptor = json.loads(Path(descriptor).read_text())
        for relative, expected in self.descriptor['componentes_sha256'].items():
            if sha256(self.root / relative) != expected:
                raise ValueError('Componente de consulta alterado: ' + relative)
        path = Path(self.descriptor['base_privada']['ruta']).resolve()
        if path.is_relative_to(self.root) or sha256(path) != self.descriptor['base_privada']['sha256']:
            raise ValueError('Base privada inválida o alterada')
        self.db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
        self.db.execute('PRAGMA query_only=ON')
        self.edicion = self.descriptor['edicion']

    def close(self):
        self.db.close()

    def consultar(self, *, persona, codcli, plan, anio, periodo, carrera=None, sede=None, jornada=None):
        """Exige persona y contexto temporal. Devuelve candidatos sin adjudicar nuevos."""
        persona = rut_normalizado(persona)
        if not all(str(x or '').strip() for x in (codcli, plan, anio, periodo)):
            raise ValueError('CODCLI, plan, año y período son obligatorios')
        owner_count = self.db.execute('SELECT COUNT(DISTINCT persona) FROM observaciones WHERE codcli=?', (str(codcli),)).fetchone()[0]
        if owner_count > 1:
            return self._exception('CODCLI_CON_VARIAS_IDENTIDADES')
        where = 'persona=? AND codcli=? AND plan=? AND anio=? AND periodo=?'
        args = [persona, str(codcli), str(plan), str(anio), str(periodo)]
        for column, value in [('carrera', carrera), ('sede', sede), ('jornada', jornada)]:
            if value is not None:
                where += ' AND ' + column + '=?'
                args.append(str(value))
        rows = [json.loads(x[0]) for x in self.db.execute('SELECT payload FROM observaciones WHERE ' + where, args)]
        if not rows:
            return self._exception('CONTEXTO_NO_LOCALIZADO')
        if len(rows) != 1:
            return self._exception('CONTEXTO_MULTIPLE', rows)
        r = rows[0]
        documentary = r['codigo_documental_atribuible']
        internal = r['codigo_interno_adoptado']
        if documentary and internal and documentary != internal:
            return self._exception('CONFLICTO_DOCUMENTAL_INTERNO', rows)
        code = documentary or internal or None
        level = 'B/C_DOCUMENTAL_ANUAL_ATRIBUIDO' if documentary else 'D_CORRESPONDENCIA_INTERNA_APROBADA' if internal else 'E_PENDIENTE'
        return {'edicion': self.edicion, 'codigo_sies': code, 'nivel_respaldo': level,
                'estado': 'REUTILIZABLE' if code else 'EXCEPCION',
                'motivo': r['estado_interno'], 'codigo_documental': documentary or None,
                'codigo_interno': internal or None, 'codigo_propuesto_no_adoptado': r['codigo_propuesto'] or None,
                'aceptacion_sies': r['aceptacion_SIES'],
                'asignacion_plan_periodo': r['plan_efectivo_periodo'],
                'regla': r['regla'], 'pendiente': r['requisito_pendiente'],
                'observacion_id': r['observacion_id'], 'evidencia': r}

    def _exception(self, reason, rows=None):
        return {'edicion': self.edicion, 'codigo_sies': None, 'estado': 'EXCEPCION',
                'nivel_respaldo': 'E_PENDIENTE', 'motivo': reason, 'evidencia': rows or []}

    def codigos_mu(self, *, persona, anio, familia=None):
        """Código literal de MU anual: no infiere plan ni corte trimestral."""
        identity = rut_normalizado(persona)
        rows = [json.loads(x[0]) for x in self.db.execute(
            'SELECT payload FROM mu_anual WHERE persona=? AND anio=?', (identity, str(anio)))]
        if familia is not None:
            rows = [r for r in rows if r['codigo'].rsplit('V', 1)[0] == familia]
        return {'codigos': sorted({r['codigo'] for r in rows}), 'evidencias': rows,
                'alcance': 'B código anual observado; no acredita expediente, plan ni aceptación SIES'}

    def seguir_cohorte(self, *, persona, anio_mu, codigo_origen, destinos):
        """Conserva código de origen; consulta versión destino sin extrapolarla."""
        original = self.codigos_mu(persona=persona, anio=anio_mu)
        if codigo_origen not in original['codigos']:
            raise ValueError('Código de origen no respaldado en MU para persona/año')
        results = []
        for target in destinos:
            if str(target.get('anio')) != str(anio_mu) or target.get('corte') not in ('T2', 'T3'):
                raise ValueError('Seguimiento T2/T3 requiere mismo año que la MU de origen')
            if not target.get('fuente_periodo'):
                raise ValueError('Debe indicarse la fuente que vincula corte y período académico')
            q = {k: target[k] for k in ('codcli', 'plan', 'anio', 'periodo', 'carrera', 'sede', 'jornada') if k in target}
            found = self.consultar(persona=persona, **q)
            results.append({'corte': target['corte'], 'codigo_cohorte_origen': codigo_origen,
                            'codigo_contexto_destino': found['codigo_sies'],
                            'version_distinta_observada': bool(found['codigo_sies'] and found['codigo_sies'] != codigo_origen),
                            'consulta': found, 'fuente_periodo': target['fuente_periodo'],
                            'vigencia_retencion': 'NO_CALCULADA_POR_ESTE_DICCIONARIO'})
        return results

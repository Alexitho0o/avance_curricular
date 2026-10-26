"""Move seven authorized amounts from enrollment fee to tuition, V05 to V06."""

import csv
import io
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preparar_etapa1_octubre_20261020 import FIELDS, KEY, ROOT, sha, tsv, write_once


def serialize(rows):
    stream = io.StringIO(newline='')
    csv.writer(stream, delimiter=';', lineterminator='\n').writerows(rows)
    return stream.getvalue().encode('utf-8')[:-1]


def main():
    source = ROOT / '10_entrega/etapa1_octubre_20261023_v05/CARGA_OFERTA_2027_ETAPA1_17467_20261023_V05.csv'
    evidence = ROOT / '11_gobernanza/etapa1_octubre_20261023_v05/rechazo_124430/23-10-2026_12-44-30_Oferta-Académica-Vigente-Editada-TP.csv.txt'
    previous_manifest = ROOT / '11_gobernanza/etapa1_octubre_20261023_v05/MANIFIESTO.json'
    input_hashes = {str(p): sha(p) for p in (source, evidence, previous_manifest)}
    assert sha(source) == '917de0e0b8a25dfe1edcac20962c32f5819de262ef6969255dc47b326312fb56'
    raw = source.read_bytes()
    before = list(csv.reader(io.StringIO(raw.decode('utf-8')), delimiter=';', strict=True))
    assert len(before) == 161 and all(len(row) == 48 for row in before)
    assert serialize(before) == raw
    after = [row[:] for row in before]
    idx = {c: i for i, c in enumerate(FIELDS)}
    amounts = {'53':'990000','66':'990000','68':'990000','69':'990000','70':'990000','96':'990000','99':'400000'}
    changes = []
    found = []
    for i, row in enumerate(after):
        code = row[idx['COD_CARRERA']]
        if code not in amounts:
            continue
        assert row[idx['COD_NIVEL_GLOBAL']] == '3' and row[idx['COD_NIVEL_CARRERA']] == '5'
        assert row[idx['VIGENCIA_CARRERA']] == '1' and row[idx['FORMATO_VALOR']] == '1'
        assert row[idx['VALOR_MATRICULA_ANUAL']] == amounts[code]
        assert row[idx['ARANCEL_ANUAL']] == '0'
        for field, value in [('VALOR_MATRICULA_ANUAL','0'), ('ARANCEL_ANUAL',amounts[code])]:
            old = row[idx[field]]
            row[idx[field]] = value
            changes.append([i+1,code,row[idx['NOMBRE_CARRERA']],field,old,value,'Confirmacion explicita del usuario: los montos son arancel y matricula queda en 0'])
        found.append(code)
    assert Counter(found) == Counter(amounts.keys())
    differences = [(i,j) for i,(a,b) in enumerate(zip(before,after)) for j in range(48) if a[j] != b[j]]
    assert len(differences) == len(changes) == 14
    assert all(j in {idx['VALOR_MATRICULA_ANUAL'],idx['ARANCEL_ANUAL']} for i,j in differences)
    changed_rows = {i for i,j in differences}
    assert len(changed_rows) == 7
    for i,(a,b) in enumerate(zip(before,after)):
        if i not in changed_rows:
            assert a == b
        for field in KEY + ['VIGENCIA_CARRERA','VACANTES_PRIMER_SEMESTRE','VACANTES_SEGUNDO_SEMESTRE','FECHA_ADMISION_INICIAL']:
            assert a[idx[field]] == b[idx[field]]
        if b[idx['VIGENCIA_CARRERA']] == '1':
            assert int(b[idx['ARANCEL_ANUAL']]) > 0
    payload = serialize(after)
    assert not payload.endswith((b'\n', b'\r')) and not payload.startswith(b'\xef\xbb\xbf')
    assert len(payload.split(b'\n')) == 161
    assert list(csv.reader(io.StringIO(payload.decode('utf-8')), delimiter=';', strict=True)) == after
    assert len({tuple(r[idx[k]] for k in KEY) for r in after}) == 161
    assert sum(int(r[idx[c]]) for r in after for c in ['VACANTES_PRIMER_SEMESTRE','VACANTES_SEGUNDO_SEMESTRE']) == 5671
    assert dict(Counter(r[idx['VIGENCIA_CARRERA']] for r in after)) == {'1':95,'2':52,'3':14}
    name = 'CARGA_OFERTA_2027_ETAPA1_17467_20261023_V06.csv'
    outputs = [ROOT / '10_entrega/etapa1_octubre_20261023_v06' / name, Path.home() / 'Desktop' / name]
    audit = ROOT / '06_validaciones/etapa1_octubre_20261023_v06'
    gov = ROOT / '11_gobernanza/etapa1_octubre_20261023_v06'
    for path in outputs:
        write_once(path, payload)
    assert sha(outputs[0]) == sha(outputs[1])
    tsv(audit / 'CAMBIOS_POR_CELDA.tsv', [['fila_csv','cod_carrera','nombre_sies','campo','anterior','nuevo','respaldo']] + changes)
    controls = {'filas':161,'columnas':48,'celdas_modificadas':14,'registros_modificados':7,'otros_registros_intactos':154,'otros_campos_intactos':True,'vacantes_total':5671,'vigencia1':95,'vigencia2':52,'vigencia3':14,'arancel_positivo_en_todos_vigencia1':True,'sin_encabezado':True,'sin_salto_final':True,'codificacion':'UTF-8 sin BOM','separador':';'}
    write_once(audit / 'CONTROLES.json', (json.dumps(controls, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    note = '''# V06: correccion autorizada de matricula y arancel

Proceso 2026, Oferta Academica 2027, Etapa 1 octubre, ID 17467.
Base: V05 rechazada por ARANCEL_ANUAL = 0 en siete diplomados con vigencia 1.
El usuario confirmo que los montos corresponden a arancel y la matricula es 0.
Esta confirmacion corrige la interpretacion de encabezados del Excel de
Docencia; se conserva intacto el archivo institucional original.

Codigos 53,66,68,69,70,96: matricula 0; arancel anual 990000.
Codigo 99: matricula 0; arancel anual 400000.
Exactamente 14 celdas modificadas en siete filas. Todos los otros valores,
filas, claves, fechas, vacantes, enlaces, vigencias y vacios quedan intactos.
161 registros, 48 columnas, 5.671 vacantes. Sin encabezado ni salto final.

V06 sustituye V05 para el siguiente intento de carga; no se borra V05.
Estado: PREPARADO PARA REINTENTO, PENDIENTE DE ACEPTACION PES.
El control local confirma arancel mayor a cero para toda vigencia 1;
no acredita ausencia de otras validaciones de plataforma. No se envio a PES.
Conservar el resultado de carga y conciliar reporte 6048 antes de congelar.
Respaldo local reproducible con fuentes, hashes, script y diferencias.
No se realizo commit ni push.
'''
    write_once(gov / 'ESTADO_Y_REANUDACION.md', note.encode('utf-8'))
    manifest = {'fecha':datetime.now(ZoneInfo('America/Santiago')).isoformat(),'estado':'V06_PREPARADA_PENDIENTE_ACEPTACION_PES','autorizacion_usuario':'si, esos montos son el arancel y la matricula queda en 0. Corrige solo eso','entradas':[{'ruta':p,'sha256':h} for p,h in input_hashes.items()],'script':{'ruta':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},'controles':controls,'git_branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT.parent,text=True).strip(),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),'salidas':[{'ruta':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs]}
    if not (gov / 'MANIFIESTO.json').exists():
        write_once(gov / 'MANIFIESTO.json', (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    assert all(sha(Path(p)) == h for p,h in input_hashes.items())
    print(json.dumps({'controles':controls,'salidas':manifest['salidas']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()

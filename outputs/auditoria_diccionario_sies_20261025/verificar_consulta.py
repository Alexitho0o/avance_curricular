"""Auditoría de solo lectura. Resultados públicos exclusivamente agregados."""
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256


def verify_file(item):
    p, expected = item
    try:
        actual = sha256(p)
        return {'ruta': p, 'esperado': expected, 'observado': actual,
                'estado': 'COINCIDE' if actual == expected else 'DIFIERE'}
    except (OSError, ValueError) as error:
        return {'ruta': p, 'esperado': expected, 'estado': 'NO_LEIBLE',
                'error': type(error).__name__}


def main():
    service = DiccionarioSiesSeguimiento()
    desc = service.descriptor
    selected = {}
    for (payload,) in service.db.execute('SELECT payload FROM observaciones ORDER BY id'):
        row = json.loads(payload)
        typ = 'documental' if row['codigo_documental_atribuible'] else 'interna' if row['codigo_interno_adoptado'] else 'pendiente'
        if typ not in selected:
            selected[typ] = dict(persona=row['persona'], codcli=row['CODCLI'], plan=row['plan'],
                                 anio=row['ano'], periodo=row['periodo'], carrera=row['carrera'],
                                 sede=row['sede_dimension'], jornada=row['jornada_sies'])
        if len(selected) == 3:
            break
    commands = list(desc['componentes_sha256'])[1:]
    with tempfile.TemporaryDirectory(prefix='qa_diccionario_', dir=Path.home()/'.local/share/ipss') as tmp:
        answers = []
        modes = []
        for i, command in enumerate(commands):
            dest = Path(tmp)/f'respuesta_{i}.json'
            proc = subprocess.run([sys.executable, '-B', str(ROOT/command), '--salida-privada', str(dest)],
                input=json.dumps([{'metodo': 'consultar', 'entrada': q} for q in selected.values()]),
                text=True, capture_output=True, cwd=ROOT)
            if proc.returncode:
                raise RuntimeError('Falló consumidor '+command+'; no se exponen respuestas individuales')
            answers.append(json.loads(dest.read_text()))
            modes.append(oct(dest.stat().st_mode & 0o777))
        parity = all(a == answers[0] for a in answers)
    test = subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests',
                           '-p','test_diccionario_sies_seguimiento.py'],cwd=ROOT,capture_output=True,text=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(verify_file, desc['entradas_sha256'].items()))
    desktop = Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx'
    tracked = subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    result = {'clasificacion':'B/C', 'edicion':service.edicion,
        'tres_consumidores':len(commands),'contextos_por_consumidor':len(selected),
        'paridad_consumidores':parity,'permisos_temporales':modes,
        'pruebas_sinteticas_codigo_salida':test.returncode,
        'pruebas_sinteticas_resumen':test.stderr[-600:],
        'fuentes_descriptor':files,
        'fuentes_coincidentes':sum(f['estado']=='COINCIDE' for f in files),
        'fuentes_con_diferencia':sum(f['estado']=='DIFIERE' for f in files),
        'fuentes_no_leibles':sum(f['estado']=='NO_LEIBLE' for f in files),
        'v17_escritorio_sha256':sha256(desktop),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'cambios_previos_sha256':{p:sha256(ROOT/p) for p in tracked},
        'bases_modificadas':False,'denominadores_modificados':False}
    service.close()
    (OUT/'QA_CONSULTA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('fuentes_descriptor','cambios_previos_sha256')},ensure_ascii=False))


if __name__=='__main__':
    main()

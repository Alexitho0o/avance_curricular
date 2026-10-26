"""Freeze the exact submitted V06, recording acceptance reported by the user."""

import csv
import io
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preparar_etapa1_octubre_20261020 import FIELDS, ROOT, sha, tsv, write_once


def main():
    name = 'CARGA_OFERTA_2027_ETAPA1_17467_20261023_V06.csv'
    source = ROOT / '10_entrega/etapa1_octubre_20261023_v06' / name
    desktop = Path.home() / 'Desktop' / name
    frozen = ROOT / '07_resultados/cargas_congeladas/20261023_etapa1_octubre_v06_aceptada'
    gov = ROOT / '11_gobernanza/etapa1_octubre_20261023_v06'
    expected = 'd7fe88035cd1215d448272a9854bee0932c45c200f4f80bb58636b62a6ae4e0b'
    assert sha(source) == expected
    assert sha(desktop) == expected, 'Desktop differs; do not assert it is the submitted V06'
    payload = source.read_bytes()
    rows = list(csv.reader(io.StringIO(payload.decode('utf-8')), delimiter=';', strict=True))
    assert len(rows) == 161 and all(len(row) == 48 for row in rows)
    assert not payload.endswith((b'\r', b'\n'))
    dictionaries = [dict(zip(FIELDS,row)) for row in rows]
    inactive = sorted((r['COD_CARRERA'] for r in dictionaries if r['VIGENCIA_CARRERA']=='3'),key=int)
    assert inactive == ['40','63','64','65','67','71','95','97','98','101','102','103','104','105']
    assert Counter(r['VIGENCIA_CARRERA'] for r in dictionaries) == {'1':95,'2':52,'3':14}
    assert sum(int(r[c]) for r in dictionaries for c in ['VACANTES_PRIMER_SEMESTRE','VACANTES_SEGUNDO_SEMESTRE']) == 5671

    dependency_rel = [
        '00_fuentes_originales/etapa1_octubre_20261020/reporte_dinamico_6047_2026-10-20_09:05:04.csv',
        '00_fuentes_originales/etapa1_octubre_20261020/Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf',
        '03_fuentes_institucionales/entregas_docencia/20261023_diplomados_vf/Oferta Diplomados 2027 - SIES vf.xlsx',
        '04_scripts/preparar_etapa1_octubre_20261020.py',
        '04_scripts/preparar_etapa1_octubre_fechas_20261020.py',
        '04_scripts/preparar_prueba_pes_etapa1_octubre_20261020.py',
        '04_scripts/corregir_salto_final_etapa1_20261020.py',
        '04_scripts/preparar_carga_etapa1_v05_20261023.py',
        '04_scripts/corregir_aranceles_etapa1_v06_20261023.py',
        '11_gobernanza/etapa1_octubre_20261023_v05/MANIFIESTO.json',
        '11_gobernanza/etapa1_octubre_20261023_v06/MANIFIESTO.json',
        '11_gobernanza/etapa1_octubre_20261023_v05/rechazo_124430/23-10-2026_12-44-30_Oferta-Académica-Vigente-Editada-TP.csv.txt',
        '06_validaciones/etapa1_octubre_20261023_v05/DECISIONES_21_DIPLOMADOS.tsv',
        '06_validaciones/etapa1_octubre_20261023_v05/CAMBIOS_POR_CELDA.tsv',
        '06_validaciones/etapa1_octubre_20261023_v06/CAMBIOS_POR_CELDA.tsv',
        '06_validaciones/etapa1_octubre_20261023_v06/CONTROLES.json',
    ]
    dependencies = [{'ruta':str(ROOT/p),'sha256':sha(ROOT/p)} for p in dependency_rel]
    write_once(frozen / name, payload)
    assert sha(frozen/name) == expected
    (frozen/name).chmod(0o444)
    for version in ('v05','v06'):
        src = ROOT / f'06_validaciones/etapa1_octubre_20261023_{version}/CAMBIOS_POR_CELDA.tsv'
        write_once(frozen / f'CAMBIOS_{version.upper()}.tsv', src.read_bytes())
    decisions = ROOT / '06_validaciones/etapa1_octubre_20261023_v05/DECISIONES_21_DIPLOMADOS.tsv'
    write_once(frozen / decisions.name, decisions.read_bytes())
    readme = '''# Etapa 1 octubre: V06 aceptada, copia congelada

Proceso 2026, Oferta Academica 2027, segundo proceso, Etapa 1, ID 17467.
Fecha de confirmacion del usuario: 23-10-2026 (America/Santiago).
El usuario confirma: "quedo cargada ok en PES" y solicita congelar V06.
Respaldo de aceptacion: declaracion del usuario en esta conversacion.
No se observo directamente PES ni se recibio comprobante, ID de ejecucion
o reporte 6048. No se inventan esos datos.

La copia congelada es identica byte a byte a V06 del proyecto y Escritorio.
Se establece solo lectura en esta copia. Conservarla; futuras rectificaciones
deben generar una nueva version, sin sobrescribir la aceptada.
Este registro sustituye el estado pendiente de aceptacion de la preparacion
V06; los manifiestos anteriores se conservan como antecedentes historicos.
No sustituye las cargas aceptadas de agosto/septiembre, de otro proceso.

161 registros, 48 columnas. 140 pregrados sin cambios frente a V04.
21 diplomados: 7 vigentes con nuevos estudiantes y 14 no vigentes.
Vigencias globales: 95 con vigencia 1; 52 con vigencia 2; 14 con vigencia 3.
Vigencia 3 por decision del usuario: 40,63,64,65,67,71,95,97,98,101,102,103,104,105.
No se borraron filas. No se dedujo la vigencia solo por diferencias de nombres.
Vacantes: 5.461 pregrado + 210 diplomados = 5.671. Los 7 diplomados vigentes
tienen 15 por semestre por instruccion del usuario (fuente Excel: 15 total).
Arancel: 990000 para 53,66,68,69,70,96; 400000 para 99. Matricula 0.
La reclasificacion de matricula a arancel fue confirmada por el usuario.
Enlaces de diplomados vacios segun manual Etapa 1 p.26, columna AJ.
CSV UTF-8 sin BOM, punto y coma, sin encabezado ni salto final.

Pendientes posteriores, sin impedir conservar la carga aceptada:
- Descargar reporte 6048 y conciliar vigencias, importes, vacantes y claves.
- Adjuntar comprobante/estado de PES si se entrega.
- Preparar Etapa 2 (02 al 13/11/2026, manual p.29), diferenciando programas
  nuevos/faltantes de programas ya registrados. No duplicar por nombre.
- Para rectificacion de datos no modificables de oferta vigente, el manual
  pp.16-17 exige solicitud antes del cierre de Etapa 1, 23/10/2026; no esperar
  un eventual rechazo en noviembre para iniciar ese procedimiento.

Gobernanza local reproducible: entradas, scripts, hashes, decisiones y diffs.
No se realizo commit ni push; no equivale a publicacion en GitHub.
'''
    write_once(frozen/'README_CARGA_CONGELADA.md',readme.encode('utf-8'))
    manifest = {
        'estado':'ACEPTADA_EN_PES_SEGUN_CONFIRMACION_USUARIO_CONGELADA',
        'fecha_confirmacion_usuario':'2026-10-23',
        'registro_local':datetime.now(ZoneInfo('America/Santiago')).isoformat(),
        'proceso':'Oferta Academica 2027, proceso 2026, segundo proceso octubre',
        'etapa':1,'id_carga':17467,'version':'V06',
        'evidencia_aceptacion':{'tipo':'declaracion_usuario','texto':'quedo cargada ok en PES, congela la V06 como la version aceptada de la etapa 1','verificacion_directa_pes':False,'comprobante':None},
        'fuente_v06':str(source),'copia_escritorio':str(desktop),'copia_congelada':str(frozen/name),'sha256_csv':expected,'bytes':len(payload),
        'controles':{'filas':161,'columnas':48,'vacantes':5671,'pregrado':140,'diplomados_vigencia1':7,'diplomados_vigencia3':14,'vigencias':{'1':95,'2':52,'3':14}},
        'dependencias':dependencies,'script_congelamiento':{'ruta':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},
        'conciliacion_6048':'PENDIENTE_NO_SE_HA_RECIBIDO_REPORTE',
        'estado_previo_conservado':str(gov/'MANIFIESTO.json'),
        'git':{'rama':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT.parent,text=True).strip(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),'commit_realizado':False,'push_realizado':False}
    }
    if not (frozen/'MANIFIESTO_ACEPTACION.json').exists():
        write_once(frozen/'MANIFIESTO_ACEPTACION.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    write_once(gov/'ACEPTACION_PES_CONFIRMADA_20261023.json',(frozen/'MANIFIESTO_ACEPTACION.json').read_bytes())
    files = [p for p in frozen.iterdir() if p.is_file() and p.name != 'MANIFIESTO_SHA256.tsv']
    tsv(frozen/'MANIFIESTO_SHA256.tsv',[['archivo','bytes','sha256']]+[[p.name,p.stat().st_size,sha(p)] for p in sorted(files)])
    assert all(sha(Path(d['ruta']))==d['sha256'] for d in dependencies)
    assert sha(source)==sha(desktop)==sha(frozen/name)==expected
    print(json.dumps({'congelada':str(frozen/name),'sha256':expected,'solo_lectura':oct((frozen/name).stat().st_mode & 0o777),'estado':manifest['estado'],'pendiente':'Conciliacion reporte 6048'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()

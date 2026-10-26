"""Cierra evidencia agregada, preserva checkpoint previo y no publica ni activa."""
from pathlib import Path
import json,hashlib,datetime,subprocess,shutil,sqlite3
O=Path(__file__).parent;A=O.parent;R=A.parents[1];P=Path('/Users/alexi/.local/share/ipss/fase3_candidata_20261025')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assert str(R)=='/Users/alexi/Documents/GitHub/avance_curricular'
expected={'PROYECTO_IPSS.json':'afac5dea027deb118f33188fc839e5b1f085ee14f60f74ed0479ddb3c69616b2','agent.md':'bd2e8e51fabed44e8f3908164a2d12f5b8263e9790cf30e935aa8b529a84926e','docs/README.md':'59d183afeab8466553e55eea7d810a8530202f76de9d73c2310566ebde795875','data/diccionario_sies_seguimiento/activo.json':'a041fa4d8c1cd25006959fc2b05089eab396f9b684cb35c942e7263343890497'}
assert all(sha(R/p)==h for p,h in expected.items())
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head=='55e3b709afb9483f0ecdd2d166f67229a454a5ef'
qa=read(O/'QA_EXCEL.json');assert sha(qa['archivo'])==sha(qa['escritorio'])==qa['sha256']
shutil.copy2(P/'build.mjs',O/'build.mjs')
text='''# Fase 3 — candidata consolidada y verificada

**B/C — Resultado:** ocho atribuciones anuales incorporadas exclusivamente a la edición candidata v8. Se conservó v7 activa. Cinco afectan a los contextos T2/T3 del Excel y tres corresponden a T1 de 2025. No se adoptaron las 16 propuestas internas ni los 12 criterios T2 pendientes.

| Alcance (B/C) | Antes | Candidata | Denominador fijo |
|---|---:|---:|---:|
| Histórico con código | 21.725 | 21.733 | 24.774 observaciones |
| Histórico pendiente | 3.049 | 3.041 | 24.774 observaciones |
| Contextos V17/V18 con código | 2.750 | 2.755 | 2.854 observaciones |
| Contextos V17/V18 pendientes | 104 | 99 | 2.854 observaciones |
| Pendientes del foco multiversión del Excel | 24 | 24 | 1.077 observaciones |

**E — No se alcanzó el 100%.** Las ocho recuperaciones reparan atribuciones documentales, no distinguen las versiones de los 24 contextos del foco multiversión. No confundir este avance con una reducción de ese foco.

**C — Hito1:** copia privada de SQLite, ocho estados previos exactos y cambios limitados a atribución/evidencia. Cuatro enlaces anuales explícitos añadidos al índice MU; no son cuatro matrículas nuevas. Los enlaces existentes permanecen iguales. Descriptor candidato separado, sin cambiar el puntero común.

**C — Hito2:** 24.774 consultas verificadas; ocho diferencias previstas y 24.766 respuestas conservadas salvo nombre de edición. Tres consumidores dan las mismas respuestas en un proceso aislado con descriptor candidato; los consumidores productivos siguen leyendo v7. Pasaron las 12 pruebas existentes y se rechazó un hash alterado.

**C — Hito3:** copia V18_CANDIDATA en Escritorio, con actualización de hojas52/54. Las 53 hojas restantes, 13 gráficos y 35 tablas conservan sus partes originales byte a byte. Se conserva el texto de todas las fórmulas; solo se actualizan seis caches dependientes y notas correspondientes. 28 controles aritméticos correctos; sin errores en hojas afectadas. Fuentes, cohortes, denominadores y tasas conservados.

**C/E — Límites de QA:** recálculo de dependencias agregadas mediante Artifact Tool y cotejo independiente; no recálculo global ni apertura en Excel nativo. Se revisaron visualmente las vistas de las hojas afectadas generadas por Artifact Tool; la copia final conserva estilos originales. Esta revisión no vuelve a certificar las tasas históricas de hojas inalteradas.

**C — Privacidad:** SQLite, operaciones individuales y copia completa del Excel fuera de Git. El Excel hereda las hojas individuales de V17 y no se publica en el repositorio. Código, descriptor sin identificadores, manifiesto y agregados se conservan localmente en el proyecto. Ningún dato subido a servicios externos.

**C — Reproducción:** consolidar.py → qa_consumidores.py; ejecutar las 12 pruebas del servicio; build.mjs con Artifact Tool → ensamblar.py → finalizar.py. Los scripts de construcción se detienen ante salidas ya existentes; no sobrescribir una edición congelada. Ensamblar usa el Python del runtime incluido con lxml. Fuentes y rutas fijadas mediante hashes en los manifiestos de fases1/2 y descriptor previo; detalle individual sólo en la ruta privada. La promoción, actualización de consumidores remotos y publicación quedan para la fase4 con autorización aplicable.

**B/C — Git:** rama feature/ire-2026; HEAD antes/después 55e3b709afb9483f0ecdd2d166f67229a454a5ef. Tres modificaciones previas conservadas por hash. Sin commit, push ni cambios al canon.
'''
(O/'INFORME_FASE3.md').write_text(text)
# Confirm public outputs have no literal personal identifiers from candidate database.
d=read(O/'descriptor_candidato.json');db=sqlite3.connect('file:'+d['base_privada']['ruta']+'?mode=ro',uri=True);secrets=set()
for a,b in db.execute('select distinct persona,codcli from observaciones'):secrets.update([a,b])
db.close()
for p in O.iterdir():
 if p.is_file() and p.suffix in ['.json','.md','.py','.mjs']:
  content=p.read_text();assert not any(s and s in content for s in secrets),p.name
manifest={'clasificacion':'C','fecha_hora':datetime.datetime.now().astimezone().isoformat(),'estado':'CANDIDATA_VERIFICADA_NO_PROMOVIDA','head_antes':head,'head_despues':head,'commit':False,'push':False,'edicion_activa':'v7_20261023_inf35_03_t3','edicion_candidata':d['edicion'],'salida_excel':qa,'diccionario_privado':d['base_privada'],'documentacion_sin_identificadores':True,'fuentes':{'fase2_manifest':{'ruta':str(A/'fase2_20261025/MANIFEST_FASE2.json'),'sha256':sha(A/'fase2_20261025/MANIFEST_FASE2.json')},'operaciones':{'ruta':str(P.parent/'fase2_historico_20261025/OPERACIONES_CANDIDATAS.json'),'sha256':sha(P.parent/'fase2_historico_20261025/OPERACIONES_CANDIDATAS.json')}},'archivos':{p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name!='MANIFEST_FASE3.json'},'preservacion_hashes':expected,'pendientes':['Promoción de edición candidata','16 propuestas internas y 12 criterios de continuidad sin adoptar','3.041 observaciones históricas y 99 contextos del Excel pendientes','24 pendientes del foco multiversión del Excel sin reducción','Apertura y recálculo global en Excel nativo no realizados']}
write(O/'MANIFEST_FASE3.json',manifest)
cp=A/'CHECKPOINT_CIERRE.json';backup=A/'historial_plan/v2/CHECKPOINT_ANTES_FASE3.json';assert not backup.exists();shutil.copy2(cp,backup);x=read(cp);x['tipo']='checkpoint_fase3_candidata_verificada';x['fecha_hora']=manifest['fecha_hora'];x['fases'][2].update(estado='CANDIDATA_VERIFICADA_NO_PROMOVIDA',hitos=[{'hito':i,'estado':s,'evidencia':'fase3_20261025/INFORME_FASE3.md'} for i,s in [(1,'OCHO_OPERACIONES_CONSOLIDADAS_EN_CANDIDATA'),(2,'QA_GLOBAL_Y_CONSUMIDORES_CORRECTOS'),(3,'V18_CANDIDATA_GENERADA_QA_NO_NATIVO')]])
x['fase3_resultado']={'descriptor':str(O/'descriptor_candidato.json'),'sha256':sha(O/'descriptor_candidato.json'),'excel':qa['escritorio'],'excel_sha256':qa['sha256'],'promocion_activo':False,'historico_pendientes_candidata':3041,'v17_contextos_pendientes_candidata':99,'multiversion_excel_pendientes':24};x['siguiente']='Fase4: revisar y autorizar promoción/publicación de código y agregados sin datos individuales; pendientes D permanecen separados.';x['checkpoint_anterior']={'archivo':str(backup.relative_to(A)),'sha256':sha(backup)};write(cp,x)
print(json.dumps({'manifest':str(O/'MANIFEST_FASE3.json'),'excel':qa['escritorio'],'sha256':qa['sha256'],'privacidad':'OK','head':head},ensure_ascii=False))

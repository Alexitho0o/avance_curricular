"""Prepara paquete revisable sin activar, instalar, commitear ni publicar."""
from pathlib import Path
import json,hashlib,subprocess,copy,zipfile,difflib,sqlite3
O=Path(__file__).parent;A=O.parent;R=A.parents[1];F3=A/'fase3_20261025'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def txt(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x)
source=read(O/'PLUGIN_FUENTE.json');assert source['plugin']['version']=='1.1.3';contents=source['contents'];updated=copy.deepcopy(contents)
reference='''# Consulta única de códigos UMAS–SIES por expediente y período

C — Alcance: seguimiento académico IPSS; no es un motor de carga ni una regla de vigencia o de retención. A oficial, B observado, C implementación, D decisión interna, E pendiente.

1. Localiza el repositorio autorizado `avance_curricular` (en el Mac de origen: `/Users/alexi/Documents/GitHub/avance_curricular`). Lee `PROYECTO_IPSS.json`, clave `recursos_comunes.diccionario_sies_seguimiento`; resuelve su ruta contra la raíz del repositorio. No elijas la edición por fecha o nombre ni congeles una versión en la skill.
2. Lee el puntero y descriptor. Usa `common/diccionario_sies_seguimiento.py`, clase `DiccionarioSiesSeguimiento`, que comprueba hashes y abre la base privada en solo lectura. La ruta privada no debe incorporarse a Git, archivos de publicación ni herramientas externas.
3. Reutiliza `scripts/consultar_diccionario_sies_seguimiento.py`, o sus consumidores `scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py` y `procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py`. Entrada JSON por stdin; salida únicamente en archivo privado nuevo fuera de Git mediante `--salida-privada`. No imprimir identificadores ni respuestas individuales en el chat.
4. Consulta exacta con persona normalizada, CODCLI, plan, año y período; carrera/sede/jornada cuando corresponda. No inventar DV, convertir P en RUT sin puente explícito, usar nombre como llave ni escoger versión por totales. Una persona puede tener varios CODCLI; no elegir una matrícula por orden de filas.
5. Separar `B/C_DOCUMENTAL_ANUAL_ATRIBUIDO`, `D_CORRESPONDENCIA_INTERNA_APROBADA` y `E_PENDIENTE`. La evidencia anual no demuestra aceptación SIES ni fecha administrativa exacta del plan. Candidato calculado no equivale a adoptado.
6. Conservar código T1 de origen separado del código del contexto destino. No extender aprobaciones personales ni código de otro año sin respaldo. `seguir_cohorte` exige fuente del vínculo corte/período y año compatible; los períodos nativos no se convierten automáticamente en T2/T3.
7. Leer primero diagnóstico y checkpoint existentes; revisar únicamente excepciones con una fuente o criterio nuevo. No volver a investigar códigos documentados sin contradicción nueva. No modificar bases, reglas, denominadores ni tasas mediante esta consulta.
8. Registrar edición/hash efectivamente leídos, contexto, respaldo, fuente/hoja/fila en salida privada y resultado agregado sin identificadores. Una nueva edición exige QA, responsable, motivo, fecha/hora, alerta y autorización aplicable; no cambiar puntero, commit ni push por leer esta referencia.

E — Estas instrucciones no instalan un servidor ni proporcionan acceso remoto a SQLite. Sin ejecutor local o fuentes privadas disponibles, declarar «consulta individual no ejecutada: falta acceso local al diccionario»; no cargar la base al complemento ni reconstruir la equivalencia con una copia empaquetada. GitHub contiene código y documentación autorizados, no las identidades. La versión vigente es la que indique el puntero verificado, no la candidata ni una cifra histórica de esta conversación.
'''
refpath='references/diccionario-sies-seguimiento.md';updated[refpath]=reference
for p in ['skills/consultar-fuentes-ipss/SKILL.md','skills/ipss-verificacion-cifras-matricula/SKILL.md']:
 updated[p]+='\n## Código SIES por expediente, plan y período\n\nPara seguimiento T1/T2/T3 o equivalencia personal UMAS–SIES, consultar primero el [punto de consulta único](../../references/diccionario-sies-seguimiento.md). Leer el puntero del repositorio y usar el consumidor común; no copiar versiones o reconstruir códigos por totales. Sin acceso local declarar la consulta pendiente. Esta instrucción no cambia vigencia, elegibilidad ni denominadores.\n'
for p in ['references/coordinacion.md','references/entorno.md']:
 updated[p]+='\n## Diccionario personal de seguimiento IPSS\n\nConsultar [el servicio común UMAS–SIES](diccionario-sies-seguimiento.md). Las skills comparten el puntero del proyecto; no mantienen otra tabla de equivalencias. El complemento no obtiene acceso automático a la base privada ni sustituye el QA de una edición.\n'
for p in ['plugin.json','.codex-plugin/plugin.json']:
 x=json.loads(updated[p]);before=copy.deepcopy(x);x['version']='1.1.4';assert {k:v for k,v in x.items() if k!='version'}=={k:v for k,v in before.items() if k!='version'};updated[p]=json.dumps(x,ensure_ascii=False,indent=2)+'\n'
plugin=O/'plugin_candidato'
for p,v in updated.items():txt(plugin/p,v)
with zipfile.ZipFile(O/'actualizacion_plugin_1.1.4.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(updated):z.writestr(p,updated[p])
txt(O/'PLUGIN_CAMBIOS.diff',''.join(''.join(difflib.unified_diff(contents.get(p,'').splitlines(True),v.splitlines(True),fromfile='actual/'+p,tofile='candidato/'+p)) for p,v in updated.items()))
# Prepare local source skill patch separately: do not overwrite differing local source.
local=Path('/Users/alexi/.codex/skills/ipss-verificacion-cifras-matricula/SKILL.md').resolve();old=local.read_text();addition=updated['skills/ipss-verificacion-cifras-matricula/SKILL.md'][len(contents['skills/ipss-verificacion-cifras-matricula/SKILL.md']):]
txt(O/'skill_local_candidata/SKILL.md',old+addition);txt(O/'skill_local_candidata/diccionario-sies-seguimiento.md',reference)
# Exact Git package. Only relevant hunk of PROYECTO_IPSS; preserve unrelated pending keys locally.
package=O/'git_candidato';paths=['common/diccionario_sies_seguimiento.py','scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py','tests/test_diccionario_sies_seguimiento.py','docs/DICCIONARIO_SIES_SEGUIMIENTO.md','agent.md','docs/README.md']
for path in paths:txt(package/path,(R/path).read_text())
project=json.loads(subprocess.check_output(['git','-C',str(R),'show','HEAD:PROYECTO_IPSS.json'],text=True));project['recursos_comunes']['diccionario_sies_seguimiento']='data/diccionario_sies_seguimiento/activo.json';write(package/'PROYECTO_IPSS.json',project)
# Include descriptor history only; no individual adjudication payloads.
for p in sorted((R/'data/diccionario_sies_seguimiento').glob('v*/descriptor.json')):txt(package/p.relative_to(R),p.read_text())
candidate=read(F3/'descriptor_candidato.json');candidate['edicion']='v8_20261025_ocho_p';candidate['estado']='VERIFICADA_PARA_PROMOCION';dest='data/diccionario_sies_seguimiento/v8_20261025_ocho_p/descriptor.json';write(package/dest,candidate)
write(package/'data/diccionario_sies_seguimiento/activo.json',{'descriptor':dest,'sha256':sha(package/dest)})
alert={'clasificacion':'C/E','estado':'PROMOCION_PENDIENTE_AUTORIZACION','responsable_preparacion':'Codex; solicitud de Alexi de ejecutar fase4','responsable_aprobacion':None,'fecha_aprobacion':None,'motivo':'Ocho atribuciones anuales por puente documental explícito verificadas en fases1–3','edicion_anterior':read(R/'data/diccionario_sies_seguimiento/activo.json'),'edicion_propuesta':read(package/'data/diccionario_sies_seguimiento/activo.json'),'denominadores_alterados':False,'reversion':'Restituir activo.json con descriptor y hash de edicion_anterior; conservar ambas bases privadas.'}
write(package/'data/diccionario_sies_seguimiento/v8_20261025_ocho_p/ALERTA_PROMOCION.json',alert)
for name in ['QA_DICCIONARIO.json','QA_CONSUMIDORES.json','QA_EXCEL.json','INFORME_FASE3.md']:txt(package/('docs/qa_diccionario_v8_20261025/'+name),(F3/name).read_text())
# Public data audit uses exact existing identities, not a claim of universal secret scanning.
db=sqlite3.connect('file:'+candidate['base_privada']['ruta']+'?mode=ro',uri=True);ids={v for row in db.execute('select distinct persona,codcli from observaciones') for v in row};db.close()
files=list(package.rglob('*'))+list(plugin.rglob('*'));count=0
for p in files:
 if p.is_file():
  assert p.suffix not in ['.xlsx','.sqlite','.csv'];s=p.read_text();assert not any(x and x in s for x in ids),p;count+=1
manifest={'clasificacion':'C','estado':'PREPARADO_NO_APLICADO','git_archivos':{str(p.relative_to(package)):sha(p) for p in package.rglob('*') if p.is_file()},'plugin':{'plugin_id':source['plugin']['plugin_id'],'expected_release_id':source['plugin']['current_release_id'],'version_actual':'1.1.3','version_propuesta':'1.1.4','archivo':str(O/'actualizacion_plugin_1.1.4.zip'),'sha256':sha(O/'actualizacion_plugin_1.1.4.zip'),'archivos_modificados':list(updated),'alcance':'overlay; otros archivos, skills y permisos conservados'},'skill_local':{'ruta_original':str(local),'sha256_previo':sha(local),'candidata':str(O/'skill_local_candidata/SKILL.md'),'referencia_destino':str(local.parents[2]/refpath),'instalada':False},'QA':{'archivos_texto_sin_identificadores_conocidos':count,'bases_y_excel_excluidos':True,'otros_cambios_PROYECTO_IPSS_excluidos':['estados_umas_vig_sies','contrato_exploratorio_datos_alumnos'],'defaultPrompt_y_metadatos_preservados':True},'pendientes':['Autorización para promover, commit/push e instalar/publicar complemento','Lectura remota posterior y prueba de consumo tras promoción','GPT heredados DATOS ALUMNOS KPI, Gestor Académico y Experto Matrícula: sin fuente editable verificada; no se modifican sus cachés']}
write(O/'PAQUETE_PUBLICACION.json',manifest)
print(json.dumps({'archivos_git':len(manifest['git_archivos']),'archivos_plugin':len(updated),'qa':manifest['QA']},ensure_ascii=False))

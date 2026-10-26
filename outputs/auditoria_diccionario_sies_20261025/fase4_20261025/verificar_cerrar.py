"""QA del paquete aislado y checkpoint sin mutar instalación ni remoto."""
from pathlib import Path
import json,subprocess,sys,hashlib,datetime,shutil
O=Path(__file__).parent;A=O.parent;R=A.parents[1];G=O/'git_candidato';P=Path('/Users/alexi/.local/share/ipss/fase3_candidata_20261025')
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Append current-edition clarification, preserving historical descriptions verbatim.
doc=G/'docs/DICCIONARIO_SIES_SEGUIMIENTO.md';old=doc.read_text();section='''
## Edición v8 preparada el 25-10-2026

C — Esta sección describe la edición preparada para promoción; el puntero del proyecto determina cuál está realmente activa. v8 conserva v7 y añade ocho atribuciones documentales anuales verificadas mediante puente explícito de identidad. Cuatro enlaces de MU se incorporan al índice, sin nuevas filas de matrícula. Las referencias anteriores a 25/23 documentos o a índices iniciales corresponden a sus ediciones históricas, no a un control actualizado de cobertura total.

B/C — Histórico candidato: 21.569 documentales, 164 exclusivamente internos aprobados y 3.041 pendientes sobre 24.774 observaciones. Excel candidato: 2.742 documentales, 13 internos y 99 pendientes sobre 2.854 contextos. Los 24 pendientes del foco multiversión del Excel no cambian. Ninguna cifra es una tasa de retención.

C/E — Las 16 propuestas y 12 criterios de continuidad de fase1 no se adoptaron. No se cambian tasas ni denominadores. La candidata requiere la promoción autorizada del puntero. SQLite y Excel completo permanecen fuera de Git. Fuentes privadas deben estar disponibles localmente para reproducir datos; publicar documentación no las publica ni da acceso remoto.

C — QA de esta edición en docs/qa_diccionario_v8_20261025/. El verificador histórico scripts/verificar_diccionario_sies_seguimiento.py escribe en v1 y no debe ejecutarse sin adaptar el destino. El QA de fase3 es el pertinente para esta candidata; no declarar que un verificador viejo certifica v8. Al promover, registrar autorización, responsable, fecha/hora y alerta de activación; verificar hashes y conservar el descriptor anterior para reversión.
'''
assert '## Edición v8 preparada' not in old;doc.write_text(old+section)
ops=read(P.parent/'fase2_historico_20261025/OPERACIONES_CANDIDATAS.json')['operaciones'];req=[]
for op in ops:
 x=op['estado_despues_propuesto'];req.append({'metodo':'consultar','entrada':dict(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo'],carrera=x['carrera'],sede=x['sede_dimension'],jornada=x['jornada_sies'])})
commands=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py'];responses=[]
for i,cmd in enumerate(commands):
 dst=P/f'fase4_consumidor_{i}.json';assert not dst.exists()
 result=subprocess.run([sys.executable,'-B',str(G/cmd),'--salida-privada',str(dst)],input=json.dumps(req),capture_output=True,text=True);assert result.returncode==0,result.stderr
 responses.append(read(dst))
assert responses[0]==responses[1]==responses[2]
assert all(x['codigo_sies']==op['estado_despues_propuesto']['codigo_documental_atribuible'] for x,op in zip(responses[0],ops))
tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_diccionario_sies_seguimiento.py'],cwd=G,capture_output=True,text=True);assert tests.returncode==0,tests.stderr
assert sha(R/'data/diccionario_sies_seguimiento/activo.json')=='a041fa4d8c1cd25006959fc2b05089eab396f9b684cb35c942e7263343890497'
assert sha(Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx'))=='8b461d53f75ac26e2e38aa46d0aae921736d21ac2a64034cfd26c08495756a52'
assert sha(Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx'))=='2bd21ca31d391b59f4bd2c56d4876becd12aae05cb9673a7e069b5542ed66b01'
pack=read(O/'PAQUETE_PUBLICACION.json');pack['git_archivos']['docs/DICCIONARIO_SIES_SEGUIMIENTO.md']=sha(doc);write(O/'PAQUETE_PUBLICACION.json',pack)
qa={'clasificacion':'C','estado':'PREPUBLICACION_CORRECTA','paquete_aislado_consumidores':3,'consultas_por_consumidor':8,'paridad':True,'edicion_leida_paquete':responses[0][0]['edicion'],'pruebas_existentes':12,'puntero_productivo_intacto':True,'V17_V18_intactas':True,'publicacion_verificada':False,'plugin_instalacion_verificada':False,'limites':['No se publicó ni activó el paquete.','El plugin propuesto es un contrato de consulta local, no un acceso remoto a SQLite.','Los tres GPT heredados no tienen fuente editable verificada en esta entrega.']};write(O/'QA_PREPUBLICACION.json',qa)
report='''# Fase4 — paquete preparado; publicación pendiente

C — Hito1 completado: paquete explícito de 23 archivos para Git y siete para el complemento institucional 1.1.4. Código, descriptores y QA sin identificadores individuales. Excel y SQLite no incluidos. Dos claves previas ajenas de PROYECTO_IPSS permanecen fuera del paquete y no se modifican en el checkout.

B/C — Hito2 preparado: tres consumidores del paquete aislado leen v8_20261025_ocho_p y coinciden en las ocho recuperaciones. Pasan las 12 pruebas existentes. Producto real sigue en v7. El complemento remoto leído sigue en 1.1.3 (pluginrel_6ad8ac3a43ac8191ac0b2d173b4e9130). Se conserva identidad, permisos, defaultPrompt y todas las habilidades no modificadas. Overlay propuesto, no subido. Skill local preparada desde su propia fuente sin sobreescribir diferencias locales.

E — Hito3 pendiente: activar/publicar exige autorización específica, según PLAN_CIERRE_100_POR_CIENTO.md fase4/hito2. Después debe releerse el release publicado y ejecutarse prueba de consumo de la instalación real. No declarar esta fase completada solo por preparar archivos.

## Alcance exacto a aprobar (D pendiente)

1. Promover v8 local con respaldo de puntero y alerta con responsable, fecha/hora y autorización; mantener las bases privadas.
2. Commit y push exclusivamente de los 23 archivos enumerados en PAQUETE_PUBLICACION.json, usando el contenido preparado; conservar todos los cambios ajenos. La incorporación de PROYECTO_IPSS debe aislar solo la clave diccionario_sies_seguimiento, no sus otras dos claves pendientes.
3. Instalar el añadido de consulta en la skill local y publicar el overlay 1.1.4 del complemento Análisis institucional de Alexi, usando expected_release_id. Si el remoto cambió, detener y rebasar el parche antes de subir.
4. Verificar lectura posterior, versión efectiva y consumidores. No publicar Excel, SQLite, operaciones individuales ni salidas de consultas.

C — Para revisar: git_candidato/ contiene los archivos finales propuestos; PLUGIN_CAMBIOS.diff muestra el cambio remoto; skill_local_candidata/ conserva la propuesta local. No editar cachés instaladas ni copiar equivalencias. Las instrucciones consultan siempre PROYECTO_IPSS y su puntero verificado.

E — Los GPT heredados DATOS ALUMNOS KPI, Gestor Académico y Experto Matrícula no se actualizan mediante un ID supuesto ni desde su caché: falta fuente editable verificada. El complemento institucional y sus dos skills pertinentes sí tienen propuesta concreta. La publicación del contrato no equivale a conectividad remota con datos privados.

B/C — HEAD local/remoto comprobado 55e3b709afb9483f0ecdd2d166f67229a454a5ef. Sin commit/push, sin cambio de puntero, Excel, bases ni denominadores. La cobertura candidata permanece 3.041 pendientes históricos y 99 contextos del Excel; no es 100%.
''';(O/'INFORME_FASE4.md').write_text(report)
cp=A/'CHECKPOINT_CIERRE.json';backup=A/'historial_plan/v2/CHECKPOINT_ANTES_FASE4.json';assert not backup.exists();shutil.copy2(cp,backup);x=read(cp);x['fecha_hora']=datetime.datetime.now().astimezone().isoformat();x['fases'][3].update(estado='PAQUETE_VERIFICADO_PENDIENTE_AUTORIZACION_PUBLICACION',hitos=[{'hito':1,'estado':'PAQUETE_EXPLICITO_PREPARADO'},{'hito':2,'estado':'QA_LOCAL_CORRECTO_PUBLICACION_PENDIENTE_AUTORIZACION'},{'hito':3,'estado':'VERIFICACION_POST_PUBLICACION_NO_EJECUTADA'}]);x['siguiente']='Autorizar alcance exacto de INFORME_FASE4.md; luego promover, publicar y verificar, sin datos personales ni cambios ajenos.';x['fase4_evidencia']={'informe':'fase4_20261025/INFORME_FASE4.md','paquete':'fase4_20261025/PAQUETE_PUBLICACION.json','qa':'fase4_20261025/QA_PREPUBLICACION.json'};x['checkpoint_anterior']={'archivo':str(backup.relative_to(A)),'sha256':sha(backup)};write(cp,x)
print(json.dumps(qa,ensure_ascii=False))

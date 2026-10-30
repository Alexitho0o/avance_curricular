"""Documentación y controles de cierre H015."""
import json
import re
import sqlite3
import subprocess
from pathlib import Path
from inventario import OUT, ROOT, P, CLOUD, load, dump, sha, table

def main():
    rows=load(OUT/'INVENTARIO.json')['archivos']
    photo=load(OUT/'FOTO_T2_2025.json'); residual=load(OUT/'RESIDUAL_59.json')
    qa=load(OUT/'QA_CANDIDATA.json'); cohorts=photo['resumen']
    def write(name,body):(OUT/name).write_text(body.strip()+'\n')
    def rel(p):return str(p.relative_to(ROOT))
    assert len({r['ruta'] for r in rows})==len(rows)==117
    assert all((CLOUD/r['ruta']).stat().st_size==r['bytes'] for r in rows)
    write('INVENTARIO_FUENTES_H015.md','# Inventario físico consolidado · H015\n\n117 archivos de trabajo y control. Dos archivos de sistema excluidos. Un hash citado acredita la versión referenciada; una mención por nombre sola no demuestra su uso. El JSON conserva las rutas de la evidencia por hito. COBERTURA_FUENTES_LEIDAS.json detalla hojas y períodos observados. La modificación de un libro no acredita el cierre académico.\n\n'+table(['Ruta por categoría','SHA-256 (B)','Tipo','Años/períodos','Corte','H007–H014 por hash','T2-2025','59 E'],[(r['ruta'],r['sha256'],r['tipo'],r['cobertura'],r['corte_estado'],', '.join(r['hitos_con_hash']) or 'Sin uso acreditado por hash',r['T2_2025'],r['para_59']) for r in rows]))
    write('FOTO_T2_2025.md','# Foto candidata T2-2025 · posiciones del padrón T1\n\n'+photo['regla']+'\n\n'+table(['Cohorte','Fuente','Padrón','Actividad PROM','Presencia DA sin exigir corte','Matrícula de período o foto parcial','C4 PROM','C4 período/parcial','Estados de período/parcial','Alcance'],[(z['cohorte'],z['archivo'],z['padron'],z['actividad_PROM_2025_2'],z['coincidencias_DA_sin_restringir_corte'],z['matricula_T2_o_foto_parcial'],z['C4_PROM'],z['C4_intake'],str(z['estados_observados']),z['corte']) for z in photo['por_fuente']])+'\n\nLas fuentes se superponen. FOTO_T2_2025.json contiene la unión por posición y el contraste de estados. En 2025-2.xlsx, Hoja1 contiene matrículas del período 3 y Detalle1 es una selección de ingreso.')
    requirements={
        'MU_PLAN_MENOS_DE_TRES_PERSONAS':'Tres personas documentales del mismo plan/año.',
        'MU_PLAN_NO_UNANIME':'Evidencia que discrimine las versiones documentadas.',
        'NUNCA_INFORMADO_PENDIENTE_DECISION_FASE_3':'Decisión de Fase 3; sin asignación por referencia grupal.',
        'PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':'Acreditar régimen y período del plan.',
        'PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'Primer T1 único del expediente con sede y jornada compatibles.',
        'SIN_CODIGO_ANUAL_COMPATIBLE':'Un código del año compatible en oferta.',
        'SIN_FAMILIA_H002_U_OFERTA_ANUAL':'Correspondencia de familia y oferta anual acreditadas.',
        'SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN':'T1 individual del mismo expediente y plan.',
        'TIPO_O_DURACION_NO_COINCIDE':'Perfil compatible o referencia documental bajo D7 extendida.'}
    mot=residual['por_resultado'];rates=qa['ensayo_v23']['tasas']
    report=OUT/'INFORME_H015.md'
    write(report.name,'# H015 · fuentes internas, foto T2-2025 y residual de v22\n\n**CANDIDATA · Fase 1.** La unidad de la foto es una posición del padrón de seguimiento. La unidad del diccionario es un contexto.\n\n## Inventario (B/C)\n\n117 archivos con SHA-256, incluidos 113 en las categorías 01–12, la ampliación 13 y tres archivos de raíz. Ver INVENTARIO_FUENTES_H015.md e INVENTARIO.json. H008 sí referenció archivos consolidados, pero no inventarió la carpeta completa. MAT_IP_CIISA_2021.xlsx, 2025-2.xlsx y los dos libros de intake no tienen uso acreditado por hash en H007–H014. La MU aporta filas individuales de 2021. Los tres libros de intake sirven de contraste sin acreditar el cierre completo de T2.\n\n## Foto (D/B/C/E)\n\nAlexi acepta PROMEDIOS como fuente de actividad del período. Para estado prevalece una foto DA con corte acreditado. FOTO_T2_2025.md y .json documentan cada extracto y las diferencias.\n\n'+table(['Cohorte','Padrón','Con foto','C4','C4 con foto','C4 vigentes','C4 no vigentes','C4 en conflicto','C4 sin foto'],[(z['cohorte'],z['padron'],z['foto_disponible'],z['C4'],z['C4_con_foto'],z['C4_estados_candidatos'].get('VIGENTE',0),z['C4_estados_candidatos'].get('NO VIGENTE',0),z['C4_estados_candidatos'].get('CONFLICTO ENTRE EXTRACTOS',0),z['C4_restantes']) for z in cohorts])+'\n\nPROMEDIOS respalda las 72 posiciones C4; una también figura en la foto parcial H008. En el padrón completo, la foto parcial coincide con PROMEDIOS en dos posiciones y difiere o presenta estados múltiples en otras dos. Quedan 118 estados en conflicto en la cohorte 2024 y 80 en 2025. Las 661 C4 sin foto quedan E. La ausencia no acredita salida ni inactividad.\n\n## Contextos (B/C/D/E)\n\nCuatro contextos de dos expedientes pasan a respaldados en el ensayo por MAT_IP_CIISA_2021.xlsx, el plan observado y el expediente. v22 sigue en 2.990/3.049 y 99/99. v23 candidata alcanza 2.994/3.049 y 99/99. Ver RESIDUAL_59.json y QA_CANDIDATA.json.\n\n'+table(['Plan','Año','Período','Nivel','Código','Contextos'],[(z['plan'],z['anio'],z['periodo'],z['nivel'],z['codigo'],z['n']) for z in residual['por_plan_anio_periodo'] if z['nivel']])+'\n\n'+table(['Motivo residual','Contextos','Requisito'],[(z['resultado'],z['n'],requirements[z['resultado']]) for z in mot if z['estado']=='E'])+'\n\nLos 25 NUNCA_INFORMADO quedan sin código hasta Fase 3: 24 IIND20251 y uno IECIRE20121. La etiqueta se limita a las fuentes examinadas. Los demás requieren evidencia individual del mismo expediente y plan, un perfil compatible, régimen acreditado o referencia documental suficiente y unánime según el motivo.\n\n## Control de indicadores (C)\n\n'+table(['Control','Numerador','Denominador','Diferencia v22/ensayo v23 (pp)'],[(k,v['numerador'],v['denominador'],'0,00') for k,v in rates.items()])+'\n\nEl ensayo usa una copia privada y un puntero aislado. La foto candidata no sustituye las banderas de R19. Orden de reproducción: inventario.py, extraer.py, perfilar.py, foto.py, residual.py, candidata.py y cerrar.py.')
    mpath=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json';md=mpath.with_suffix('.md')
    m=load(mpath);r={'id':'R32','pregunta':'¿Qué cobertura interna respalda la foto T2-2025 y qué cambia en el residual de v22?','resultado_clave':'CANDIDATA H015. Foto para 72/733 C4, 661 sin foto; cuatro asignaciones nuevas, 55 E. v23 en ensayo; v22 activa.','archivo':rel(report),'hoja_o_seccion':'Foto y residual','script_productor':rel(OUT/'cerrar.py'),'commit':'PUBLICACION_H015; base eb389ed','sha256':sha(report),'clase':'B fuentes; C cruce; D criterio; E pendientes','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Nueva fuente interna de cierre o decisión explícita para Fase 2/3.','limites':'Foto y diccionario candidatos. Sin cambio de tasas.'}
    m['resultados']=[x for x in m['resultados'] if x['id']!='R32']+[r]
    mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    line='| '+' | '.join([r['id']+' · '+r['pregunta']]+[r[k] for k in ['resultado_clave','archivo','script_productor','commit','sha256','clase','fecha_resultado','no_recalcular_salvo']])+' |'
    lines=[v for v in md.read_text().splitlines() if not v.startswith('| R32 ·')]
    i=next(i for i,v in enumerate(lines) if v.startswith('| R31 ·'));lines.insert(i+1,line)
    md.write_text(('\n'.join(lines)+'\n').replace('Mapa (31 resultados)','Mapa (32 resultados)'))
    private=load(P/'FOTO_T2_2025_PRIVADA.json')
    assert len(private)==1708 and len({(x['pos'],x['cohorte']) for x in private})==1708
    assert sum(x['C4'] for x in private)==733 and sum(x['C4'] and x['foto_disponible'] for x in private)==72
    assert sum(z['n'] for z in mot if z['estado']=='E')==55 and residual['nuevas']==4 and qa['observaciones_cambiadas']==4
    assert all(v['delta_pp']==0 for v in rates.values())
    assert all((v['numerador'],v['denominador'])==(qa['v22']['tasas'][k]['numerador'],qa['v22']['tasas'][k]['denominador']) for k,v in rates.items())
    archive=load(P.parent/'h010_20261030/ESTADO_INICIAL.json')
    assert all(sha(ROOT/f)==h for f,h in archive['ajenos'].items())
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()
    assert all(s in status for s in archive['status_ajenos'].splitlines())
    cat=ROOT/qa['descriptor_candidato']['descriptor'];ptr=ROOT/'data/diccionario_sies_seguimiento/activo.json'
    assert load(ptr)==qa['activa'] and sha(cat)==qa['descriptor_candidato']['sha256']
    manifest=OUT/'MANIFEST.json';qa_file=OUT/'QA_H015.json'
    public=sorted(set([f for f in OUT.iterdir() if f.is_file()]+[mpath,md,cat,cat.parent/'CAPA_PROMEDIOS.json',manifest,qa_file]))
    assert all(f.suffix in ('.md','.json','.py') for f in public)
    dump(manifest,{'base':'eb389ed','archivos_publicacion':[rel(f) for f in public],'sha256':{rel(f):sha(f) for f in public if f not in (manifest,qa_file)},'archivo_inventario':'INVENTARIO.json','antecedentes':{rel(f):sha(f) for f in [ROOT/'outputs/primer_t1_h014_20261030/RESIDUAL_E_ACTUAL.json',ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/h008_20261030/INVENTARIO_FOTOS_H008.md',ROOT/'data/reglas_negocio/indicador_intertrimestral/REGLA.json',ptr]}})
    dump(qa_file,{'estado':'PASS','archivos_inventariados':117,'posiciones':1708,'C4':733,'C4_con_foto':72,'residual_inicial':59,'altas_candidatas':4,'residual_final':55,'delta_pp':0.0,'controles':list(rates),'puntero_activo':load(ptr),'cambios_ajenos_intactos':len(archive['status_ajenos'].splitlines()),'hallazgos_privacidad':[]})
    desc=load(ROOT/load(ptr)['descriptor']);db=sqlite3.connect(Path(desc['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    ids={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};db.close()
    ids.update({v.split('-')[0] for v in ids if '-' in v})
    pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(x) for x in sorted(ids) if len(x)>=6)+r')(?!\w)')
    generic=re.compile(r'(?<!\w)(?:\d{7,8}-[0-9Kk]|\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]|\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
    for f in public:
        for n,l in enumerate(f.read_text().splitlines(),1):
            if pattern.search(l) or generic.search(l):
                qa_file.unlink();raise ValueError(f'Privacidad: {rel(f)} línea {n}')
    print('PASS',len(public),'archivos')
if __name__=='__main__':main()

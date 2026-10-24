#!/usr/bin/env python3
"""Proyecta H5/H6/H7 y sector 2026 a un libro académico sin identidades."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from common.consulta_sies_historica import ConsultaHistorica, verificar_paquete


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def j(value): return json.dumps(value,ensure_ascii=False,sort_keys=True)
def joined(values): return '\n'.join(str(v) for v in values)
def clave(values): return '|'.join(str(len(str(v)))+':'+str(v) for v in values)
def sheet(name,title,note,headers,rows,widths):
    return dict(name=name,title=title,note=note,headers=headers,rows=rows,widths=widths)


def prepare():
    descriptor,blobs=verificar_paquete()
    m=json.loads(blobs['maestro.json']); assert not m['reglas_efectivas']
    base=ROOT/'data/versiones_historicas_sies_umas'
    h6=base/'fase_6_20261015'; hm=json.loads((h6/'manifest.json').read_text())
    assert sha(h6/'manifest.json')=='6d5ef5ccc04cbb28ae87d968a87bc329bb8993255b72ed73302a1e60264d4faa'
    for name in ['consultas_sies_anuales.tsv','consultas_umas.tsv','ejemplos_piloto.json']:
        assert sha(h6/name)==hm['outputs'][name],name
    h7=base/'fase_7_20261015'; h7m=json.loads((h7/'manifest.json').read_text())
    assert sha(h7/'resumen.json')==h7m['outputs']['resumen.json']
    sector_path=ROOT/'data/enriquecimiento_mu2026/20261015_oferta_literal/catalogo_carrera_sector_2026.json'
    assert sha(sector_path)=='cdfaf46841c58d00c55f3f85da072e4778eda590d0ca3b9f210a051f38619f6c'
    sector=json.loads(sector_path.read_text())
    for role in ['sector','oferta_literal']:
        source=sector['fuentes'][role]; assert sha(Path(source['path']))==source['sha256']
    sectors=sector['por_codigo_unico']
    hist=list(csv.DictReader((h6/'consultas_sies_anuales.tsv').open(),delimiter='\t'))
    offers={(r['anio'],r['codigo_unico']):r for r in m['oferta_anual']}
    bycode=defaultdict(list)
    for r in m['oferta_anual']:bycode[r['codigo_unico']].append(r)
    sheets=[]; dictionary=[]
    for u in m['universo_sies']:
        code=u['codigo_unico']; rows=sorted(bycode[code],key=lambda r:r['anio'])
        last=rows[-1] if rows else {}; current=offers.get((2026,code),{})
        comp=last.get('componentes_sies',{}); sec=sectors.get(code,{})
        if sec: assert sec['nombre_oferta_literal']==current['nombre_carrera']
        dictionary.append([code,current.get('nombre_carrera',''),last.get('nombre_carrera',''),
            last.get('anio'),u['nombre_primera_matricula_observada'],comp.get('carrera',''),
            comp.get('sede',''),comp.get('jornada',''),comp.get('version',''),
            current.get('jornada',''),current.get('modalidad',''),current.get('tipo_plan_sies',''),
            'Sí' if current else 'No observada',u['anios_oferta'],u['anios_mrun'],
            joined(sorted({c['codcarpr'] for c in m['equivalencias_programa_2026'] if c['codigo_unico']==code})),
            u['candidatos_plan'],0,sec.get('sector_ipss',''),
            'RESPALDADO_2026' if sec else 'SIN_SECTOR_ACREDITADO_EN_ESTA_EDICION',
            ('sector_2026: por_codigo_unico['+code+'].evidencia_sector\n'+sec['evidencia_sector']['regla']) if sec else '',u['presencia']])
    sheets.append(sheet('Diccionario SIES','Diccionario por Código Único','141 códigos. Nombre 2026 literal; nombre histórico y MRUN separados. Sector es referencia 2026.',
        ['Código Único','Nombre oficial 2026','Último nombre oferta histórica','Año última oferta','Primer nombre observado MRUN','Código carrera SIES','Sede SIES','Jornada SIES código','Versión SIES','Jornada oferta 2026','Modalidad oferta 2026','Tipo plan oferta 2026','Oferta 2026','Años oferta','Años MRUN','Códigos internos relacionados','Relaciones candidatas de plan','Reglas efectivas','Sector IPSS 2026','Estado sector','Evidencia sector','Presencia'],dictionary,
        [24,48,48,16,48,17,13,17,13,23,24,26,20,35,35,35,20,16,28,44,65,24]))
    history=[]
    mrun={(int(r['cat_periodo']),r['codigo_unico']):r for r in m['mrun_anual']}
    assert len(mrun)==len(m['mrun_anual'])
    for row in hist:
        year=int(row['anio']); code=row['codigo_unico']; offer=offers.get((year,code),{}); comp=offer.get('componentes_sies',{}); mr=mrun.get((year,code),{})
        history.append([year,code,row['estado_consulta'],row['motivo'],row['nombre_anual_oferta'],
            row['nombre_oferta_2026'],offer.get('jornada',''),row['modalidad_oferta'],
            row['tipo_plan_oferta'],comp.get('version',''),comp.get('carrera',''),comp.get('sede',''),
            row['nombre_mrun'],int(row['registros_mrun']),row['presencia'],row['vigencia_oferta'],
            row['fuente_oferta'],row['registro_mrun_ejemplo'],
            mr.get('jornada',''),mr.get('modalidad',''),mr.get('version',''),mr.get('cod_carrera',''),
            mr.get('cod_sede',''),mr.get('tipo_plan_carr',''),mr.get('vigencia_carrera',''),clave([year,code])])
    sheets.append(sheet('Historia SIES','Historia anual de oferta y MRUN','767 claves año + Código Único. Registros MRUN no equivalen a personas únicas. Fuente: consultas SIES H6.',
        ['Año','Código Único','Estado consulta','Motivo','Nombre anual oferta','Nombre oficial 2026','Jornada oferta','Modalidad oferta','Tipo plan oferta','Versión SIES','Código carrera SIES','Sede SIES','Nombre MRUN','Registros MRUN','Presencia','Vigencia oferta','Localizador oferta','Fila ejemplo MRUN','Jornada MRUN','Modalidad MRUN','Versión MRUN','Código carrera MRUN','Sede MRUN','Tipo plan MRUN','Vigencia MRUN','Clave anual'],history,
        [12,24,30,32,48,48,25,24,28,14,17,13,48,18,23,34,70,20,25,25,16,23,16,28,32,35]))
    plans=[]
    for p in m['planes_umas']:
        plans.append([p['CODPESTUD'],joined(p['nombres_internos_catalogo']),
            joined(sorted({c['Codcarr'] for c in p['contextos_catalogo']})),
            joined(sorted({c['Sede'] for c in p['contextos_catalogo']})),joined(p['jornadas_promedios']),
            joined(p['anios_actividad_observada']),p['presencia'],p['estado_equivalencia'],
            joined(p['codigos_sies_candidatos']),p['candidatos_plan_sies'],0,
            int(p['filas_promedios']),p['fila_plan_ejemplo'],p['fila_promedios_ejemplo'],'No acreditada'])
    sheets.append(sheet('Planes UMAS','Inventario de planes UMAS','236 planes, incluidos los que no tienen actividad en el reporte. Año del identificador no determina vigencia.',
        ['Plan UMAS','Nombres internos catálogo','Códigos carrera catálogo','Sedes catálogo','Jornadas observadas','Años actividad observada','Presencia','Estado equivalencia','Códigos SIES candidatos','Relaciones candidatas','Reglas efectivas','Filas PROMEDIOS','Fila catálogo ejemplo','Fila PROMEDIOS ejemplo','Asignación temporal'],plans,
        [25,49,25,18,22,30,30,32,35,21,18,20,23,25,26]))
    candidates=[]; groups=defaultdict(list)
    for c in m['candidatos_plan_sies']:
        code=c['codigo_unico']; comp=c['componentes_sies']; current=offers.get((2026,code),{})
        candidates.append([c['id'],c['codcarpr'],c['plan_umas'],c['sede_umas'],c['jornada_umas'],
            c['nombre_interno'],2026,code,current.get('nombre_carrera',''),comp['version'],
            current.get('jornada',''),current.get('modalidad',''),c['estado'],
            'Sí' if c['presencia_oferta_2026'] else 'No observada',joined(c['equivalencias_ids']),
            'maestro H5: candidatos_plan_sies[id='+c['id']+'].fuentes','No',joined(c['anios_actividad_observada_jornada'])])
        if c['jornada_umas']:
            groups[(c['codcarpr'],c['plan_umas'],c['sede_umas'],c['jornada_umas'],c['nombre_interno'])].append(c)
    sheets.append(sheet('Candidatos','Relaciones candidatas entre plan y Código Único','513 relaciones H5. No acreditan una versión efectiva. Jornada J3 sin correspondencia UMAS se mantiene vacía.',
        ['ID candidato','Código carrera UMAS','Plan UMAS','Sede UMAS','Jornada UMAS','Nombre interno','Ámbito candidato','Código Único candidato','Nombre oficial 2026','Versión SIES','Jornada oferta 2026','Modalidad oferta 2026','Estado','Oferta 2026','Relaciones de programa','Localizadores fuentes','Habilitada para resolver','Años actividad observada'],candidates,
        [33,23,25,16,18,49,20,26,48,16,25,26,54,20,47,85,27,30]))
    programs=[]
    for p in m['equivalencias_programa_2026']:
        programs.append([p['id'],p['codcarpr'],p['nombre_interno'],p['sede_umas'],p['jornada_umas'],
            p['codigo_unico'],2026,p['tipo_plan_sies_operativo'],p['estado'],
            'Sí' if p['presencia_oferta_2026'] else 'No observada',
            'maestro H5: equivalencias_programa_2026[id='+p['id']+'].fuentes'])
    sheets.append(sheet('Programas UMAS','Relaciones de programa del catálogo operativo','257 relaciones, incluso sin plan asociado. No acreditan vigencia de malla ni sustituyen la oferta anual publicada.',
        ['ID relación','Código carrera UMAS','Nombre interno relación','Sede UMAS','Jornada UMAS','Código Único relacionado','Ámbito catálogo','Tipo plan operativo código','Estado','Oferta 2026','Localizador fuentes'],
        programs,[33,23,49,16,18,27,20,26,53,20,85]))
    grouped=[]
    for fields,cs in sorted(groups.items()):
        codes=sorted({c['codigo_unico'] for c in cs}); available=any((2026,code) in offers for code in codes)
        grouped.append([*fields,2026,joined(codes),len(codes),
            'PENDIENTE_EVIDENCIA' if available else 'SIN_OFERTA_ANUAL',
            '' if available else 'CODIGO_NO_OBSERVADO',
            joined(sorted({offers[(2026,code)]['nombre_carrera'] for code in codes if (2026,code) in offers})),
            clave(fields),clave(fields[:4]),joined(sorted(c['id'] for c in cs))])
    sheets.append(sheet('Claves UMAS','Agrupación exacta de candidatos','Una fila por código interno + plan + sede + jornada + nombre. Año candidato 2026; período y régimen no acreditados.',
        ['Código carrera UMAS','Plan UMAS','Sede UMAS','Jornada UMAS','Nombre interno','Ámbito candidato','Códigos candidatos','Destinos distintos','Estado H5','Motivo H5','Nombres oficiales 2026','Clave candidata','Clave contexto','IDs candidatos'],grouped,
        [23,25,16,18,49,20,34,20,30,30,49,75,54,65]))
    examples=[]
    for case in json.loads((h6/'ejemplos_piloto.json').read_text()):
        e=case.get('ejemplo',{})
        inventory=case['tipo']=='INVENTARIO_CANDIDATOS_NO_ES_ACTIVIDAD'
        if inventory:
            item=case['ejemplos'][0]
            e={'PLAN_DE_ESTUDIO':item['plan_umas'],'codigo_unico':item['codigo_unico'],
               'estado_resolucion':item['estado'],'diagnostico':item['id']}
        year=e.get('ANO',e.get('anio',''))
        if isinstance(year,str) and year.isdigit():year=int(year)
        examples.append([case['caso'],case['tipo'],year,e.get('PERIODO',''),
            e.get('REGIMEN',''),e.get('CODCARR',''),e.get('PLAN_DE_ESTUDIO',''),e.get('CARRERA',''),
            e.get('SEDE_LISTADO',''),e.get('JORNADA',''),e.get('estado_adaptacion',''),
            e.get('estado_resolucion',e.get('estado_consulta',case.get('estado',''))),
            joined(e.get('codigos_candidatos',[])),e.get('codigo_unico',''),
            e.get('diagnostico',e.get('motivo','')),e.get('fila_promedios_ejemplo',''),
            e.get('fila_contextos_h4',''),e.get('registro_mrun_ejemplo',''),
            'Ejemplo de inventario; no representa actividad ni acredita jornada UMAS para J3.' if inventory else 'No acredita asignación individual.'])
    sheets.append(sheet('Ejemplos','Casos generales del cruce','Casos observados del piloto H6, sin identidades. Las filas fuente permiten revisar la evidencia original.',
        ['Caso','Tipo de evidencia','Año','Período','Régimen','Código carrera UMAS','Plan UMAS','Nombre interno','Sede UMAS','Jornada UMAS','Adaptación H6','Resultado','Códigos candidatos','Código consultado SIES','Motivo','Fila PROMEDIOS','Fila contexto H4','Fila MRUN','Lectura del ejemplo'],examples,
        [43,34,14,14,21,23,25,49,16,18,34,32,36,26,48,19,20,18,54]))
    rules=[
        ['Uso','Celdas amarillas','Complete año y Código Único, o las ocho dimensiones UMAS. Se conserva la escritura literal.'],
        ['Unión','Oferta y MRUN','Año + Código Único exacto. Presencia en MRUN no acredita oferta ausente ni asignación individual.'],
        ['Unión','Candidatos UMAS','Código interno + plan + sede + jornada + nombre interno. Solo ámbito candidato 2026.'],
        ['Unión','Regla efectiva','Añade año + período + régimen a la clave. No hay reglas acreditadas en esta edición.'],
        ['Versión','Código Único','Versión SIES distingue atributos de programas. Su aparición no prueba por sí sola una nueva malla UMAS.'],
        ['Nombre','Oferta 2026','Se conserva el nombre literal. Jornada, modalidad, tipo de plan y nombre interno son campos separados.'],
        ['Sector','Referencia 2026','61 códigos con evidencia sectorial anterior. No extrapolar a otros códigos o años.'],
        ['Faltantes','Sector sin evidencia','El vacío no significa que la carrera carezca de sector. Estado explícito pendiente.'],
        ['Faltantes','Oferta 2007–2009','Sin cobertura anual disponible. Se conservan observaciones MRUN, sin inventar programas no observados.'],
        ['Faltantes','Actividad UMAS','El extracto aporta años 2019–2026. Un plan sin actividad no se declara cerrado.'],
        ['Estado','PENDIENTE_EVIDENCIA','Uno o más candidatos, ninguno acreditado. No seleccionar el primero ni la versión máxima.'],
        ['Estado','SIN_EQUIVALENCIA','No hay regla aplicable. Revisar nombre exacto, sede, jornada y fuentes; no crear alias.'],
        ['Estado','SIN_OFERTA_ANUAL','Sin cobertura anual o código no observado. No es evidencia de inexistencia de la oferta real.'],
        ['Estado','ENTRADA_INCOMPLETA','Falta año entero o un campo literal. NULL, NONE y NAN son faltantes.'],
        ['Estado','FUERA_AMBITO','Consulta fuera de 2007–2026. No se usa el catálogo 2027 como alternativa.'],
        ['Formato','Espacios y mayúsculas','Búsqueda sensible a mayúsculas y espacios internos. Elimine solo espacios periféricos antes de pegar.'],
        ['Ámbito','Período y régimen','Son literales UMAS. Completarlos no convierte candidatos de programa en equivalencias temporales.'],
        ['Unidades','Filas y personas','Filas PROMEDIOS y registros MRUN son observaciones. No sumarlas como estudiantes únicos.'],
        ['Actualización','Nueva evidencia','No editar estados para acreditar versiones. Revisar evidencia y generar otra edición del maestro y del libro.'],
        ['Actualización','Control de cambios','Esta edición H8 reemplaza la búsqueda anterior de cuatro campos y elimina el selector manual de versión.'],
        ['Actualización','Fuentes congeladas','El libro es un snapshot 2026-10-15. No sincroniza automáticamente con reportes o sistemas.'],
        ['Validación','Motor de cálculo','Fórmulas probadas en Artifact Tool. No se afirma recálculo nativo en Microsoft Excel.'],
    ]
    sources=dict(m['fuentes'])
    sources['sector_2026']={'path':str(sector_path),'sha256':sha(sector_path)}
    sources['consultas_h6']={'path':str(h6/'consultas_sies_anuales.tsv'),'sha256':hm['outputs']['consultas_sies_anuales.tsv']}
    sources['ejemplos_h6']={'path':str(h6/'ejemplos_piloto.json'),'sha256':hm['outputs']['ejemplos_piloto.json']}
    sources['integracion_h7']={'path':str(h7/'resumen.json'),'sha256':h7m['outputs']['resumen.json']}
    for id,source in sources.items(): rules.append(['Fuente',id,Path(source['path']).name+'\nSHA-256: '+source['sha256']])
    sheets.append(sheet('Guía','Reglas, fuentes y actualización','Fuentes fijadas por hash. Los identificadores de fuente remiten al maestro H5 y al expediente de fases.',
        ['Tema','Regla o fuente','Definición y evidencia'],rules,[22,36,105]))
    assert len(dictionary)==141 and len(plans)==236 and len(candidates)==513 and len(history)==767
    assert sum(bool(r[1]) for r in dictionary)==124
    assert sum(bool(r[18]) for r in dictionary)==61
    query=ConsultaHistorica(); tests=[]
    for row in list(csv.DictReader((h6/'consultas_umas.tsv').open(),delimiter='\t')):
        params={k:row[k] for k in ('periodo','regimen','codcarpr','nombre_interno','plan_umas','sede_umas','jornada_umas')};params['anio']=int(row['anio'])
        tests.append({'params':params,'estado':row['estado_resolucion'],'candidatos':json.loads(row['codigos_candidatos']),'motivo':row['motivo_h5']})
    # Additional boundaries absent from the observed universe.
    regular=dict(anio=2026,periodo='1',regimen='TRIMESTRAL',codcarpr='ILOG',nombre_interno='INGENIERIA EN LOGISTICA',plan_umas='ILOG20241',sede_umas='RE',jornada_umas='O')
    for delta in [{'anio':2008},{'anio':2027},{'anio':2006},{'periodo':''},{'plan_umas':'NAN'},
                  {'nombre_interno':'ingenieria en logistica'},{'nombre_interno':'INGENIERIA EN  LOGISTICA'},
                  {'jornada_umas':'V'},{'sede_umas':'CO'},{'periodo':'2','regimen':'OTRO'}]:
        params=dict(regular,**delta); result=query.consultar_umas(**params)
        tests.append({'params':params,'estado':result['estado'],'candidatos':sorted({c['codigo_unico'] for c in result.get('candidatos',[])}),'motivo':result.get('motivo','')})
    payload={'revision':'H8_20261015','descriptor_h7':descriptor,'sheets':sheets,
             'tests_umas':tests,'tests_sies':hist,'sector_sha256':sha(sector_path),
             'maestro_sha256':hashlib.sha256(blobs['maestro.json']).hexdigest()}
    return payload


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
    data=prepare();raw=(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    if args.salida.exists() and args.salida.read_bytes()!=raw:raise ValueError('Salida existente distinta')
    args.salida.parent.mkdir(parents=True,exist_ok=True);args.salida.write_bytes(raw)
    print(j({'hojas':{s['name']:len(s['rows']) for s in data['sheets']},'casos_umas':len(data['tests_umas'])}))

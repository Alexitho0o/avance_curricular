"""Prepara suplemento privado desde la fase 3; entradas de solo lectura."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import json,os,hashlib,openpyxl
OUT=Path(__file__).resolve().parent
P=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025')
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
slots=json.loads(Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json').read_text())
headers=['Fila padrón original','Cohorte T1','Año observado','Período nativo','Tipo documento','Documento original','Identidad normalizada','CODCLI','Carrera UMAS','Plan observado','Sede contexto','Jornada contexto','Código origen T1','Código destino','Respaldo destino','Relación código','Cuenta posición','Cuenta contexto','Origen multiversión','Comparación de plan','Excepciones','Regla aplicada','Pendiente','Evidencia PROMEDIOS','Evidencia MU','Fuente origen','Ver padrón','Grupo resumen 54']
rows=[]
status={'B/C_DOCUMENTAL_ANUAL_ATRIBUIDO':'B/C Documental anual','D_CORRESPONDENCIA_INTERNA_APROBADA':'D Interno aprobado','E_PENDIENTE':'E Pendiente'}
V18=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx')
z=ZipFile(V18)
def cells(i):
    out={}
    for c in E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:c',NS):
        v=c.find('s:v',NS);t=c.find('s:is',NS)
        out[c.get('r')]=''.join(t.itertext()) if t is not None else v.text if v is not None else None
    return out
c54=cells(54)
groups={}
for rn in range(6,227):
    key=tuple(c54.get(f'{k}{rn}') or '' for k in ['A','B','C','E','F','G','H','I','M','K'])
    assert key not in groups
    groups[key]=rn
def evidence(es):return '\n'.join(f"{e.get('fuente','')} | {e.get('hoja','')} | fila {e.get('fila','')}" for e in es)
for s in slots:
    for index,c in enumerate(s['contextos'] or [None]):
        base=[s['fila_origen_foto'],s['anio_origen'],s['anio_observado'],int(s['periodo_nativo']),s['tipo_doc'],str(s['documento_original']),str(s['persona'])]
        if c:
            dest=c['codigo_destino'] or 'Pendiente';st=status[c['respaldo_destino']];multi='Sí' if c['multiversion_origen_heredado'] else 'No'
            planlabel='Mismo plan observado en contexto nativo 1 de año origen' if c['comparacion_plan']=='MISMO_PLAN_OBSERVADO' else 'Sin contexto nativo 1 del mismo CODCLI en año origen'
            key=tuple(str(x) for x in [s['anio_origen'],s['anio_observado'],s['periodo_nativo'],c['carrera_umas'],c['plan_destino'],s['codigo_origen_T1'],dest,st,multi,planlabel])
            # Original sheet uses an empty destination for an unresolved context.
            if key not in groups and dest=='Pendiente':key=key[:6]+('',)+key[7:]
            assert key in groups, 'El grupo no reproduce la hoja 54'
            row=base+[str(c['CODCLI']),c['carrera_umas'],c['plan_destino'],c['sede_contexto'],c['jornada_contexto'],s['codigo_origen_T1'],dest,st,c['relacion_codigo'],int(index==0),1,multi,c['comparacion_plan'],'; '.join(c['excepciones']),c['regla_existente'],c['pendiente_existente'],evidence(c['fuentes_promedios']),evidence(c['fuentes_matricula']),str(s['fuente_origen']),None,groups[key]]
        else:
            row=base+['Pendiente','Pendiente','Pendiente',None,None,s['codigo_origen_T1'],'Pendiente','Sin contexto','SIN_CONTEXTO',1,0,'Pendiente','Sin contexto comparable','Sin contexto en diccionario',None,'No implica deserción ni ausencia en matrícula',None,None,str(s['fuente_origen']),None,None]
        assert len(row)==len(headers)
        rows.append(row)
assert len(rows)==6374
names=[s.get('name') for s in E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',NS)]
names+=['56_Vista_T1_T2_T3','57_Trazabilidad_Actual']
guide=[]
private_names={names[i-1] for i in [10,12,21,25,26]}|{names[55]}
sources={9:'MU y cohortes elegibles; 2379 filas verificadas en fase 1',11:'MU consolidada 2022–2026; 10200 filas',20:'Padrón intertrimestral original;4473 pertenencias',24:'Foto matrícula T3 2025',25:'Foto matrícula T3 2026'}
for i,name in enumerate(names,1):
    if i in [10,12,21,25,26]:role='Detalle local';content=sources[i-1];formula='Datos literales + fórmulas de maqueta original; fuente conservada'
    elif i==28:role='Guía actual';content='Inventario de las 57 hojas de esta edición';formula='Generada desde el paquete final'
    elif i==56:role='Vista derivada privada';content='6374 filas;6358 posiciones y2854 contextos, sin duplicar el padrón';formula='Consulta exacta del diccionario v8; enlace a fuente/hoja/fila'
    elif i==57:role='Resumen actual';content='Cobertura, pendientes, navegación y límites de recálculo';formula='SUMIFS/COUNTIFS sobre hoja56'
    elif i==54:role='Resumen de contextos';content='221 grupos por código/plan/período';formula='N: COUNTIF de grupos de hoja56'
    elif i==53:role='Códigos T1';content='Conteos de seguimiento y numeradores existentes; no nuevos cierres';formula='F/K/M desde56;G/H materializados reproducibles de entrega vigente;I=G/H'
    elif i==52:role='Resumen actual';content='Tasas existentes y cobertura del diccionario activo v8';formula='Enlaces a18,53,54; pendientes distintos de deserción'
    elif i==55:role='Pendientes actuales';content='66 renuncias, alcance, pendientes SIES y QA nativo';formula='Notas + conteo pendiente enlazado a52'
    elif i>=30:role='Auditoría histórica';content='Fotografía de su edición; no representa el estado vigente del diccionario';formula='Materializado o fórmulas de esa edición; no sustituye hojas52–57'
    elif i in [19,20,24,27,29]:role='Cálculo / control';content='Actividad y matrícula diferenciadas; correcciones V14–V18 conservadas';formula='Fórmulas recuperadas y vigentes; no cambiar denominadores'
    elif i in [5,6,13,14,15,16,17,18]:role='Resumen / comparación';content='Cálculo anual y comparación; conservar filtros, categorías y diseño';formula='Fórmulas restauradas;tasas=retenidos/elegibles, no promedio de porcentajes'
    else:role='Referencia / navegación';content='Texto, catálogo o fuente según encabezado propio';formula='Entrada literal o navegación; sin adjudicaciones nuevas'
    guide.append([name,role,content,'Maqueta original + V18 + vista fase3','Abrir hoja',formula,'Restringida local' if name in private_names else 'Agregada / técnica'])
w=openpyxl.load_workbook(V18,read_only=True,data_only=True)
payload={'headers':headers,'rows':rows,'guide':guide,'rows53':[list(r) for r in w['53_Codigos_T1_Confirmados'].iter_rows(min_row=6,max_row=223,max_col=13,values_only=True)],'expected54':{str(r):int(c54[f'N{r}']) for r in range(6,227)},'resumen':json.loads((OUT.parent/'fase3/RESULTADOS_FASE3.json').read_text())['resumen_periodo']}
w.close()
with os.fdopen(os.open(P/'payload.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(payload,f,ensure_ascii=False)
print(json.dumps({'filas_vista':len(rows),'hojas_guia':len(guide),'grupos':len(groups)}))

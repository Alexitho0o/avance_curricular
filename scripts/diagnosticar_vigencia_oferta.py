#!/usr/bin/env python3
"""Audita vigencia anual de oferta; conserva excepciones y no asigna mallas."""
import csv,gzip,hashlib,io,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/diagnostico_vigencia_oferta/20261016'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=ROOT/'data/reglas_negocio/20261015/fuentes/Oferta_Academica_2010_al_2026_SIES_12_01_2026_WEB_E.csv.gz'
    raw=gzip.decompress(source.read_bytes())
    assert hashlib.sha256(raw).hexdigest()=='f3e2222dbdc710226fe86f71f543916781af5744117e52b03ddf8551552fcded'
    reader=csv.DictReader(io.StringIO(raw.decode('latin1')),delimiter=';')
    rows=[]
    for n,r in enumerate(reader,2):
        if r['Código IES']!='162':continue
        rows.append({'anio':int(r['Año'][4:]),'codigo_unico':r['Código Único'],'nombre':r['Nombre Carrera'],
          'tipo_carrera':r['Tipo Carrera'],'duracion_total':r['Duración Total'],'modalidad':r['Modalidad'],
          'jornada':r['Jornada'],'vigencia':r['Vigencia'],'registro_csv':n})
    assert len(rows)==747
    index={(r['anio'],r['codigo_unico']):r for r in rows};assert len(index)==747
    hist=defaultdict(list);families=defaultdict(list)
    for r in rows:
        hist[r['codigo_unico']].append(r)
        families[r['anio'],r['codigo_unico'].rsplit('V',1)[0],r['tipo_carrera']].append(r)
    changes=[]
    for code,rr in hist.items():
        rr.sort(key=lambda r:r['anio'])
        for a,b in zip(rr,rr[1:]):
            if a['vigencia']!=b['vigencia']:changes.append({'codigo_unico':code,'anterior':a,'siguiente':b,'anios_sin_observacion':b['anio']-a['anio']-1})
    new='Vigente con estudiantes nuevos';old='Vigente sin estudiantes nuevos'
    reopening=[r for r in changes if r['anterior']['vigencia']==old and r['siguiente']['vigencia']==new]
    simultaneous=[]
    for (y,f,t),rr in sorted(families.items()):
        codes=[r['codigo_unico'] for r in rr if r['vigencia']==new]
        if len(codes)>1:simultaneous.append({'anio':y,'familia':f,'tipo':t,'codigos_con_nuevos':sorted(codes)})
    cp=ROOT/'data/versiones_historicas_sies_umas/fase_2_20261015/cohortes_observadas.tsv'
    cm=json.loads((cp.parent/'manifest.json').read_text());assert sha(cp)==cm['outputs'][cp.name]
    alerts=[]
    for r in csv.DictReader(cp.open(),delimiter='\t'):
        offer=index.get((int(r['cat_periodo']),r['codigo_unico']))
        if offer and offer['vigencia']==old and r['anio_ing_carr_act']==r['cat_periodo']:
            alerts.append({'oferta':offer,'mrun':r,'interpretacion':'REQUIERE_TIPO_PLAN_E_INGRESO_ORIGINAL_NO_ERROR_AUTOMATICO'})
    summary={'filas_oferta_ipss':len(rows),'codigos':len(hist),'vigencias':dict(Counter(r['vigencia'] for r in rows)),
      'cambios_vigencia':len(changes),'transiciones_sin_nuevos_a_con_nuevos':len(reopening),
      'codigos_con_transicion_sin_nuevos_a_con_nuevos':len({r['codigo_unico'] for r in reopening}),
      'familia_anio_tipo_con_varios_codigos_admiten_nuevos':len(simultaneous),
      'grupos_mrun_ingreso_actual_del_anio_en_oferta_sin_nuevos':len(alerts),
      'asignaciones_modificadas':0}
    outputs={'oferta_anual.json':sorted(rows,key=lambda r:(r['codigo_unico'],r['anio'])),
      'cambios_vigencia.json':changes,'retornos_a_con_nuevos.json':reopening,
      'admision_simultanea.json':simultaneous,'alertas_ingreso_actual.json':alerts,'resumen.json':summary}
    OUT.mkdir(parents=True,exist_ok=True)
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    docs=['manual_oferta_2026_texto_completo.json','manual_oferta_acceso_2027_texto_completo.json']
    sources={str(p.relative_to(ROOT)):sha(p) for p in [source,cp]+[source.parent/d for d in docs]}
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_sha256':sources,'script_sha256':sha(__file__),'salidas_sha256':{n:sha(OUT/n) for n in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()

"""C: redistribución agregada por código T1 de indicadores y pendientes heredados.

Conserva las fuentes, denominadores y numeradores vigentes. T2-2025 mantiene el
valor institucional 600 y deja pendiente el desglose por código: no adopta una
exclusión por tipo documental. El auxiliar se resuelve junto a este archivo.
No escribe identificadores personales ni consulta servicios externos.
"""
from pathlib import Path
import argparse
import collections
import csv
import importlib.util
import json
import openpyxl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Carpeta de salida agregada; debe no contener los tres resultados.")
    args = parser.parse_args()
    filenames = ["seguimiento_T1_agregado_20261023.json",
                 "seguimiento_T1_agregado_20261023.csv",
                 "proxy_T1_reconstruccion_controles.json"]
    existing = [str(args.output_dir / name) for name in filenames
                if (args.output_dir / name).exists()]
    if existing:
        parser.error("Salidas existentes; elija otra carpeta: " + ", ".join(existing))
    auxiliary = Path(__file__).resolve().with_name("v13_20261023_reconstruir_proxy_t1.py")
    spec = importlib.util.spec_from_file_location("v13_proxy_t1", auxiliary)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    m = module.reconstruir_proxy(args.repo_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "proxy_T1_reconstruccion_controles.json").write_text(
        json.dumps(m["out"], ensure_ascii=False, indent=2))
    R=m['R'];M=m['M'];src=m['src'];sha=m['sha'];origins=m['origins'];byrow=m['byrow'];vig=m['vig'];anyrows=m['anyrows']
    assert all(z['coincide'] for z in m['out'] if z['cohorte'] in [2024,2026])
    groups=collections.defaultdict(list)
    for (year,k),o in m['keys'].items():groups[(year,o['codigo_origen'],o['carrera'])].append((k,o))
    rows=[];checks=collections.defaultdict(collections.Counter)
    for (year,code,career),mem in sorted(groups.items()):
     n=len(mem);period_year=2025 if year==2024 else year
     t2=None if year==2025 else sum(k in vig[(period_year,2)] for k,o in mem)
     t3=sum(k in vig[(2025,3)] for k,o in mem) if year==2024 else sum(byrow[o['fila_foto']][16]==1 for k,o in mem)
     d3=n if year==2024 else sum(byrow[o['fila_foto']][17]==1 for k,o in mem)
     for k,o in mem:
      rr=byrow[o['fila_foto']];assert rr[1]==year and rr[2]==1 and str(rr[9])==career
      if year in [2025,2026]:
       assert rr[16] == int(rr[15]=='VIG 1');assert rr[17]==int(rr[15] not in ['NO APLICA','PENDIENTE','Sin foto'])
     rows.append({'cohorte_T1':year,'codigo_SIES_T1':code,'carrera_T1':career,'denominador_T1_original':n,'periodo_T2':f'{period_year}-2','T2_numerador':t2,'T2_denominador':n,'T2_tasa':t2/n if t2 is not None and n else None,'T2_alcance':'Pendiente de linaje del proxy' if year==2025 else 'Proxy actividad y estado académico VIGENTE en PROMEDIOS; no foto de cierre','periodo_T3':f'{period_year}-3','T3_numerador':t3,'T3_denominador_vigente':d3,'T3_tasa':t3/d3 if d3 else None,'T3_alcance':'Proxy actividad y estado académico VIGENTE en PROMEDIOS; no foto de cierre' if year==2024 else 'Foto de matrícula, indicadores Q/R heredados de hoja20','T3_fuera_denominador_tasa_heredada':n-d3,'clasificacion':'B origen T1 documentado; C redistribución; E proxy y pendientes de linaje'})
     checks[year].update({'denominador_T1':n,'T2_numerador_desglosable':0 if t2 is None else t2,'T3_numerador':t3,'T3_denominador':d3,'grupos':1})
    assert dict(checks[2024])=={'denominador_T1':558,'T2_numerador_desglosable':160,'T3_numerador':175,'T3_denominador':558,'grupos':len([r for r in rows if r['cohorte_T1']==2024])}
    assert checks[2025]['denominador_T1']==1150 and checks[2025]['T3_numerador']==1023 and checks[2025]['T3_denominador']==1150
    assert checks[2026]['denominador_T1']==1471 and checks[2026]['T2_numerador_desglosable']==1042 and checks[2026]['T3_numerador']==1360 and checks[2026]['T3_denominador']==1467
    controlcells=['D7','E7','F7','G7','H7','D8','E8','F8','G8','H8','D11','E11','F11','G11','H11'];cache={}
    for label,p in [('original',src),('V12',Path(M['salida']))]:
     assert sha(p)==(M['fuentes'][str(src)] if label=='original' else M['salida_sha256'])
     w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['18_Foto_Intertrimestral'];cache[label]={c:s[c].value for c in controlcells};w.close()
    assert cache['original']==cache['V12']
    summ=[{'cohorte_T1':y,'denominador_T1_original':checks[y]['denominador_T1'],'periodo_T2':f'{2025 if y==2024 else y}-2','T2_numerador_heredado':600 if y==2025 else checks[y]['T2_numerador_desglosable'],'T2_denominador':checks[y]['denominador_T1'],'T2_tasa_heredada':(600 if y==2025 else checks[y]['T2_numerador_desglosable'])/checks[y]['denominador_T1'],'T2_estado_desglose':'Pendiente de linaje del proxy' if y==2025 else 'Conciliado con valor heredado','periodo_T3':f'{2025 if y==2024 else y}-3','T3_numerador_heredado':checks[y]['T3_numerador'],'T3_denominador_tasa_heredada':checks[y]['T3_denominador'],'T3_tasa_heredada':checks[y]['T3_numerador']/checks[y]['T3_denominador'],'clasificacion':'B/C'} for y in [2024,2025,2026]]
    refs={'codigo_T1':{'ruta':str(m['op']),'sha256':sha(m['op']),'campos':['fila_foto','anio','carrera','codigo_origen','fuente','respaldo'],'control':'3179 orígenes; fila_foto identifica la fila de hoja20; el código fue contrastado con MU por el constructor gobernado.'},'indicadores_foto':{'ruta':str(src),'sha256':sha(src),'hoja':'20_Foto_BBDD','rango':'B6:R4478','criterio':'GRUPO=1; Q=VIGENTE T3; R=EN BASE T3. Se reproducen valores existentes y se comprueban contra P, sin nueva clasificación.'},'proxy':{'ruta':str(m['prom']),'sha256':sha(m['prom']),'hoja':'Hoja1','columnas':['RUT','ANO','PERIODO','ESTADO_ACADEMICO'],'criterio_reproducido':'Intersección por llave corporal RUT usada en hoja20; persona única por año/grupo, con al menos un registro del año-período y ESTADO_ACADEMICO=VIGENTE. No se requiere coincidencia del código SIES de destino.'},'control_proxy':{'ruta':str(src),'sha256':sha(src),'hoja':'26_Avance_Curricular_Resumen','filas':[1850,1851,1852,1853,1854,1855],'limite':'Conteos proxy son literales en E; fórmula de tasa F=E/C. Constructor original no incorporado según README del subproyecto.'},'V12':{'ruta':M['salida'],'sha256':M['salida_sha256'],'hoja':'18_Foto_Intertrimestral','controles':cache['V12']}}
    result={'objetivo':'Distribuir indicadores heredados por código T1 documentado, sin alterar población ni asignación de destino.','resumen':summ,'por_codigo_T1':rows,'referencias':refs,'QA':{'3179_origenes_asignados_una_vez':sum(r['denominador_T1_original'] for r in rows)==3179,'grupos_por_ano':{str(y):checks[y]['grupos'] for y in checks},'conteos_restantes_coinciden':True,'V12_y_original_15_celdas_iguales':True,'proxy_2025_no_desglosado':True,'fuentes_sin_cambios':sha(src)==M['fuentes'][str(src)] and sha(m['prom'])=='aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015','sin_adjudicaciones_version':True,'sin_cambios_denominadores':True},'diagnostico_proxy_2025_C_E':{'denominador_fijo':1150,'numerador_T2_heredado':600,'R_y_P_usando_llave_corporal':{'personas_con_registro':694,'VIGENTE':611},'solo_R_condicion_diagnostica_NO_ADOPTADA':{'personas_con_registro':680,'VIGENTE':600},'documentos_P':{'total':20,'con_registro':14,'VIGENTE':11},'estado':'No se adopta exclusión P ni se distribuye600 por código; falta linaje de indicador individual original.'},'limites':['2024 se sigue en2025-2/3 por alcance explícito de hoja26; no cambiarlo a2024.','Proxy de actividad usa estado académico del extracto; no acredita vigencia de matrícula al cierre.','Coincidencia de cifras no demuestra que el constructor original usó idéntico código.','RUT corporal para proxy es implementación de reproducción; no se usa para adjudicar identidad documental SIES.','T3-2026 conserva denominador de tasa1467 y población original1471; cuatro casos quedan fuera por fórmula heredada R.','No usa versión SIES de destino como filtro de continuidad; código de clasificación es siempre T1.','T2-2025 queda con total600 visible y desglose Pendiente, no cero.']}
    text=json.dumps(result,ensure_ascii=False,indent=2);assert not any(str(o['documento_original']) in text or (o['persona'] and o['persona'] in text) for o in origins)
    O=args.output_dir/'seguimiento_T1_agregado_20261023.json';O.write_text(text+'\n')
    with (args.output_dir/'seguimiento_T1_agregado_20261023.csv').open('w',encoding='utf-8-sig',newline='') as f:
     writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');writer.writeheader();writer.writerows(rows)
    print(json.dumps({'resumen':summ,'QA':result['QA'],'archivo':str(O),'sha256':sha(O)},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

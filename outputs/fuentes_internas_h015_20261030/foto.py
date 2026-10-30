"""Foto interna candidata. El año de ingreso de PROMEDIOS se recupera por expediente."""
import collections as C
from inventario import P,OUT,ROOT,H8,load,dump,table
def main():
    import os
    os.umask(0o077)
    x=load(P/'indices.json');schema=load(OUT/'COBERTURA_FUENTES_LEIDAS.json')
    pad=x['padrón'];partial=x['parcial'];intakes={'2 y 3er Intake.xlsx','2025-2.xlsx','Matricula 2 y 3er 2024.xlsx'}
    rules=load(load(H8/'FUENTES_H008.json')['entradas']['reglas_estado']['ruta'])['equivalencias']
    lookup={(r['estado_umas'],r['situacion_umas']):str(r['resultado']) for r in rules}
    simple=C.defaultdict(set)
    for (st,_),v in lookup.items():simple[st].add(v)
    ranks={'1':1,'NO APLICA':2,'PENDIENTE':3,'0':4,'E':5}
    label={'1':'VIGENTE','0':'NO VIGENTE','NO APLICA':'NO APLICA','PENDIENTE':'PENDIENTE','E':'ESTADO NO DETERMINADO'}
    choose=lambda sts:min(sts,key=lambda v:ranks.get(v,5)) if sts else ''
    fy=C.defaultdict(set);all_da=C.defaultdict(lambda:C.defaultdict(set));intake=C.defaultdict(lambda:C.defaultdict(set))
    for f,sh,b,ident,exp,car,s,j,ing,ping,y,t,estado,sit in x['da']:
        if ing not in ('2024','2025') and not (exp and ing.isdigit()):continue
        if exp and ing.isdigit():fy[b,exp].add(ing)
        if ing not in ('2024','2025'):continue
        pair=(b,int(ing));v=lookup.get((estado,sit),'E');all_da[f][pair].add(v)
        if (f in intakes and y=='2025' and t=='2') or f==partial:intake[f][pair].add(v)
    # La presencia por fuente se registra primero. Un indicio sin año de ingreso
    # inequívoco no entra por la llave R19.
    promos=C.defaultdict(lambda:C.defaultdict(set));raw_states=C.defaultdict(C.Counter);missing=C.Counter()
    for f,b,exp,car,plan,st,er,con in x['prom']:
        ing=fy[b,exp]
        if len(ing)!=1:missing[f,'SIN_ANIO_INGRESO_UNICO']+=1;continue
        y=next(iter(ing))
        if y not in ('2024','2025'):continue
        k=(b,int(y));results=simple[st];v=next(iter(results)) if len(results)==1 else 'E'
        promos[f][k].add(v);raw_states[f][st]+=1
    files=sorted({s['archivo'] for s in schema if s['clase_contenido'] in ('PROMEDIOS','DA')})
    available=[];private=[];counts=C.Counter();cross=C.Counter();mixed=C.Counter()
    for s in pad:
        k=(s['body'],s['cohorte'])
        pro={f:choose(d[k]) for f,d in promos.items() if k in d}
        pico={f:choose(d[k]) for f,d in intake.items() if k in d}
        has_partial=partial in pico
        levels=set(pro.values());state=label[next(iter(levels))] if len(levels)==1 else 'CONFLICTO ENTRE EXTRACTOS' if levels else 'SIN ESTADO'
        # Sólo la foto de cierre previamente acreditada tiene prioridad para estado.
        if has_partial:state=label[pico[partial]]
        cls='PROMEDIOS + FOTO PARCIAL H008' if pro and has_partial else 'PROMEDIOS' if pro else 'FOTO PARCIAL H008' if has_partial else 'SOLO MATRÍCULA DE PERÍODO, SIN CIERRE' if pico else 'SIN EVIDENCIA DE FOTO'
        observed=bool(pro or has_partial)
        counts[s['cohorte'],s['C4'],cls,state,observed]+=1
        if pro and has_partial:cross[s['cohorte'],'COINCIDE' if levels=={pico[partial]} else 'DISTINTO_O_MULTIPLE']+=1
        if len(levels)>1:mixed[s['cohorte'],s['C4']]+=1
        private.append(s|{'fuentes_prom':pro,'fuentes_intake':pico,'estado':state,'foto_disponible':observed,'clase_fuente':cls})
    for f in files:
        for year in (2024,2025):
            group=[s for s in pad if s['cohorte']==year];prom=promos[f];da=all_da[f];t=intake[f]
            pr=[s for s in group if (s['body'],year) in prom];capt=[s for s in group if (s['body'],year) in da];ii=[s for s in group if (s['body'],year) in t]
            counts_source=C.Counter(label[choose(prom[s['body'],year])] for s in pr) if pr else C.Counter(label[choose(t[s['body'],year])] for s in ii)
            state_da=C.Counter(label[choose(da[a['body'],year])] for a in capt)
            overlap=C.Counter()
            for a in capt:
                ky=(a['body'],year)
                observed={choose(d[ky]) for d in promos.values() if ky in d}
                if observed:
                    value=choose(da[ky])
                    overlap['COINCIDENCIA' if observed=={value} else 'DIFERENCIA_O_ESTADO_INCIERTO']+=1
            available.append({'archivo':f,'cohorte':year,'padron':len(group),'actividad_PROM_2025_2':len(pr),'coincidencias_DA_sin_restringir_corte':len(capt),'matricula_T2_o_foto_parcial':len(ii),'C4_PROM':sum(s['C4'] for s in pr),'C4_intake':sum(s['C4'] for s in ii),'estados_observados':dict(counts_source),'estado_DA_extracto_sin_inferir_cierre':dict(state_da),'comparacion_DA_con_PROM':dict(overlap),'corte':'Cierre T2 parcial acreditado H008' if f==partial else 'Actividad 2025-2. Estado del extracto' if f.startswith('PROMEDIOS') else 'Corte T2 no acreditado; sólo contraste'})
    summary=[]
    for year in [2024,2025]:
        g=[s for s in private if s['cohorte']==year];z=[s for s in g if s['C4']]
        summary.append({'cohorte':year,'padron':len(g),'PROM':sum(bool(s['fuentes_prom']) for s in g),'foto_disponible':sum(s['foto_disponible'] for s in g),'C4':len(z),'C4_con_foto':sum(s['foto_disponible'] for s in z),'C4_restantes':sum(not s['foto_disponible'] for s in z),'estados_candidatos':dict(C.Counter(s['estado'] for s in g if s['foto_disponible'])),'C4_estados_candidatos':dict(C.Counter(s['estado'] for s in z if s['foto_disponible']))})
    dump(P/'FOTO_T2_2025_PRIVADA.json',private)
    dump(OUT/'FOTO_T2_2025.json',{'estado':'CANDIDATA_FASE_1','resumen':summary,'por_fuente':available,'particion':[{'cohorte':k[0],'C4':k[1],'fuente':k[2],'estado':k[3],'disponible':k[4],'posiciones':n} for k,n in sorted(counts.items())],'comparacion_PROM_con_foto_parcial':[{'cohorte':k[0],'resultado':k[1],'n':v} for k,v in sorted(cross.items())],'conflictos_entre_PROM':[{'cohorte':k[0],'C4':k[1],'n':v} for k,v in sorted(mixed.items())],'filas_PROM_sin_anio_inequivoco':[{'archivo':k[0],'motivo':k[1],'filas':v} for k,v in sorted(missing.items())],'estado_academico_PROM_por_extracto':dict(raw_states),'unidad':'Posiciones del padrón por cohorte; fuentes superpuestas, no sumar columnas ni fuentes.','regla':'Llave R19 cuerpo normalizado + año de ingreso del expediente. PROMEDIOS obtiene año por cuerpo y CODCLI inequívocos en DA. Prioridad R19 dentro de cada fuente. Un estado con resultados posibles diferentes queda E sin SITUACION. La actividad académica es del período; ESTADO_ACADEMICO corresponde a cada extracto. Sólo una foto DA con cierre acreditado prevalece para estado. Ausencia no equivale a VIG 0.'})
    print(summary)
if __name__=='__main__':main()

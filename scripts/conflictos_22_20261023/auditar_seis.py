from pathlib import Path
import sqlite3,json,hashlib,collections
P=Path('/Users/alexi/.local/share/ipss/analisis_conflictos_22_20261023');P.mkdir(exist_ok=True)
assert not (P/'.git').exists()
p='/Users/alexi/.local/share/ipss/cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite'
c=sqlite3.connect('file:'+p+'?mode=ro',uri=True);rs=[json.loads(x[0]) for x in c.execute('select payload from observaciones')]
fs=['carrera','sede','jornada','ano','plan','ingreso_DA']
g=collections.defaultdict(list)
for r in rs:
 if r['codigo_documental_atribuible']:g[tuple(str(r[k]) for k in ['persona','CODCLI','plan','carrera','sede_dimension','jornada_sies','ano'])].append(r)
a=[]
for key,gr in g.items():
 codes={r['codigo_documental_atribuible'] for r in gr}
 if len(codes)!=1:continue
 ins={str(r['fechas_declaradas'].get('DA_ANOINGRESO') or '') for r in gr};r=gr[0]
 a.append({'persona':r['persona'],'CODCLI':r['CODCLI'],'plan':r['plan'],'carrera':r['carrera'],'sede':r['sede_dimension'],'jornada':r['jornada_sies'],'ano':str(r['ano']),'ingreso_DA':next(iter(ins)) if len(ins)==1 else '', 'codigo':next(iter(codes)),'fold':int(hashlib.sha256(r['persona'].encode()).hexdigest()[:16],16)%5,'obs':gr})
def key(r):return tuple(str(r.get(f) or '') for f in fs)
errors=[]
for fold in range(5):
 train=[r for r in a if r['fold']!=fold];test=[r for r in a if r['fold']==fold];m=collections.defaultdict(lambda:collections.defaultdict(set))
 for r in train:
  if '' not in key(r):m[key(r)][r['codigo']].add(r['persona'])
 for r in test:
  d=m.get(key(r),{})
  if len(d)==1 and len(next(iter(d.values())))>=3:
   pred=next(iter(d))
   if pred!=r['codigo']:errors.append(dict(r,pred=pred,train=[t for t in train if key(t)==key(r)],all_group=[t for t in a if key(t)==key(r)]))
assert len(errors)==6
for i,r in enumerate(errors,1):r['id']='E%02d'%i
(P/'ERRORES6_DETALLE.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2,default=str))
out=[]
for r in errors:
 q={k:r[k] for k in ['id','carrera','sede','jornada','ano','plan','ingreso_DA','codigo','pred','fold']}
 q.update({'personas_train':len({t['persona'] for t in r['train']}),'total_grupo_codigos':dict(collections.Counter(t['codigo'] for t in r['all_group'])),'periodos':sorted({o['periodo'] for o in r['obs']})})
 out.append(q)
Path('/tmp/errores6_agregado.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))

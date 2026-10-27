from pathlib import Path
import json,sqlite3,os,hashlib
R=Path(__file__).resolve().parents[2];P=Path.home()/'.local/share/ipss/fase_g_v19_candidata_20261027';P.mkdir(mode=0o700,parents=True,exist_ok=True);src=Path.home()/'.local/share/ipss/fase_g_hito1_20261027/DETALLE_PRIVADO.json';m=R/'outputs/fase_g_hito1_mu_siguiente_20261027/MANIFEST.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(m)=='e238bc4af9707bb1ac918ca423a8d4b612fa07ae80f7f7c8bc878794516ef5e4';assert h(src)==json.loads(m.read_text())['detalle_privado']['sha256'];db=sqlite3.connect((Path.home()/'.local/share/ipss/fase_f_v18_candidata_20261027/DICCIONARIO_V18_CANDIDATA.sqlite').as_uri()+'?mode=ro',uri=True);x=json.loads(src.read_text());picked=[];other=[]
for z in x:
 if z['nivel']=='D1_PROPUESTA':z['autorizacion']='D1';picked.append(z);continue
 if z['nivel']!='D2_PROPUESTA':continue
 n=str(int(z['anio'])+1);rr=db.execute('select codcli,payload from observaciones where persona=? and anio=?',(z['persona'],n)).fetchall();same=any(cli==z['codcli'] and (p:=json.loads(payload)).get('codigo_interno_adoptado')==z['codigo_candidato'] and p.get('plan')==z['plan'] and p.get('carrera')==z['carrera'] for cli,payload in rr);different=any(cli!=z['codcli'] and (p:=json.loads(payload)).get('codigo_documental_atribuible') and p.get('carrera')!=z['carrera'] for cli,payload in rr)
 if same:z['autorizacion']='D2A_INTERNA_NO_DOCUMENTAL';picked.append(z)
 elif z['anio']=='2023' and different:other.append(z)
assert len(picked)==105 and sum(z['autorizacion']=='D2A_INTERNA_NO_DOCUMENTAL' for z in picked)==22 and len(other)==96
for name,v in [('APROBADOS_PRIVADO.json',picked),('OTRA_CARRERA_96_PRIVADO.json',other)]:
 p=P/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False));os.chmod(p,0o600)
print('83 D1 + 22 D2a; 96 cambio de carrera para revisión')

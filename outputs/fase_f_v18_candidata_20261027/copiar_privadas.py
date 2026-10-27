from pathlib import Path
import json,sys,shutil,datetime
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import sha256
P=Path.home()/'.local/share/ipss/fase_f_v18_candidata_20261027';root=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES');sub=root/'07_PRIVADAS_DICCIONARIO';cat1=R/'data/catalogo_fuentes/CATALOGO_FUENTES.json';cat2=root/'CATALOGO_FUENTES.json';assert cat1.read_bytes()==cat2.read_bytes();cat=json.loads(cat1.read_text());dp=R/'data/diccionario_sies_seguimiento/v18_20261027_candidata_fase_f/descriptor.json';d=json.loads(dp.read_text());mp=R/d['capa_promedios']['metadata'];assert sha256(mp)==d['capa_promedios']['sha256'];m=json.loads(mp.read_text());entries=[]
for step,kind,obj in [(15,'v18_20261027_base',d['base_privada']),(16,'v18_20261027_capa_promedios',m['capa_privada'])]:
 src=Path(obj['ruta']);h=sha256(src);assert h==obj['sha256'];folder=sub/kind;folder.mkdir(parents=True,exist_ok=True);dst=folder/src.name
 if dst.exists():assert sha256(dst)==h;action='YA_EXISTIA_IDENTICO'
 else:
  tmp=dst.with_name(dst.name+'.copiando');assert not tmp.exists();shutil.copyfile(src,tmp);assert sha256(tmp)==h;tmp.rename(dst);action='COPIADO'
 assert sha256(src)==sha256(dst)==h
 entries.append({'paso':f'{step}/{step}','conjunto':kind,'archivo':src.name,'ruta_origen':str(src),'ruta_consolidada':str(dst),'sha256':h,'bytes':src.stat().st_size,'hash_fijado_por':str(dp.relative_to(R)),'accion':action,'contiene_identificadores':True,'fecha_hora':datetime.datetime.now().astimezone().isoformat()})
existing=cat.get('catalogo_privadas',[]);assert not any(str(e['paso']).split('/')[0] in ('15','16') for e in existing);cat['catalogo_privadas']=existing+entries;raw=json.dumps(cat,ensure_ascii=False,indent=1);cat1.write_text(raw,encoding='utf-8');cat2.write_text(raw,encoding='utf-8');assert cat1.read_bytes()==cat2.read_bytes();print(json.dumps({'copias':entries,'catalogo_sha256':sha256(cat1)},ensure_ascii=False))

"""Consolida sólo altas verificadas en una copia SQLite candidata; el puntero real es de lectura."""
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
import openpyxl
from inventario import P,ROOT,OUT,CLOUD,load,dump,sha
from extraer import full,txt
H13=ROOT/'outputs/activacion_v21_h013_20261030'
sys.path.insert(0,str(H13))
from activar import probe

def main():
    os.umask(0o077);new=[z for z in load(P/'RESIDUAL_59_PRIVADO.json') if z['estado']=='ASIGNADA']
    if not new:return
    ptr=ROOT/'data/diccionario_sies_seguimiento/activo.json';initial=ptr.read_bytes();a=load(ptr);old=load(ROOT/a['descriptor'])
    assert old['edicion']=='v22_20261030_h014' and sha(ROOT/a['descriptor'])==a['sha256']
    base=Path(old['base_privada']['ruta']);assert sha(base)==old['base_privada']['sha256']
    destdir=ROOT/'data/diccionario_sies_seguimiento/v23_20261030_h015_candidata';destdir.mkdir(parents=True,exist_ok=True)
    temp=P/'candidata.tmp.sqlite'
    if temp.exists():temp.unlink()
    source=sqlite3.connect(base.as_uri()+'?mode=ro',uri=True);c=sqlite3.connect(temp);source.backup(c)
    c.execute('alter table asignaciones_v22 rename to asignaciones_v23')
    target={r['observacion_id']:r for r in load(P/'indices.json')['objetivos']};inv={Path(r['ruta']).name:r for r in load(OUT/'INVENTARIO.json')['archivos']}
    granular=[]
    # Segunda lectura independiente de la fila MU. Se conserva la referencia exacta sólo en privado.
    for z in new:
        oid=z['observacion_id'];obs=target[oid];matches=[]
        for f in z['fuentes']:
            path=CLOUD/inv[f]['ruta'];assert sha(path)==inv[f]['sha256']
            if f!='MAT_IP_CIISA_2021.xlsx':raise ValueError('Implementar verificación independiente del nuevo esquema antes de consolidar '+f)
            wb=openpyxl.load_workbook(path,read_only=True,data_only=True);it=wb['MAT_2021'].values;hd=next(it)
            for n,v in enumerate(it,2):
                r=dict(zip(hd,v))
                if txt(r['MC_CAT_PERIODO'])=='MAT_'+str(z['anio_fuente']) and full(r['MM_N_DOCUMENTO'],r['MM_DV'])==obs['persona'] and r['MC_CODIGO_UNICO']==z['codigo']:
                    matches.append({'archivo':f,'hoja':'MAT_2021','fila':n,'sha256':inv[f]['sha256']})
            wb.close()
        assert len(matches)==1,(z['plan'],len(matches))
        assert c.execute('select nivel_asignacion from asignaciones_v23 where observacion_id=?',(oid,)).fetchone()==('E',)
        evidence={'fuente_MU':matches,'plan_y_expediente':'Actividad PROMEDIOS del año de la MU y DA por persona+CODCLI+carrera+sede+jornada; un único expediente/plan compatible','anio_fuente':z['anio_fuente'],'oferta_control':'Año del T1 fuente para D10; año del contexto para T1/herencia','clase':'B/C' if z['nivel']=='DOCUMENTAL_T1' else 'D/C'}
        payload=json.loads(c.execute('select payload from observaciones where id=?',(oid,)).fetchone()[0])
        payload.update(desfase=z['anio_fuente']-int(obs['ano']),nivel_asignacion=z['nivel'],regla='H015_'+z['nivel'],año_T1_fuente=z['anio_fuente'],evidencia_asignacion=[evidence],clase=evidence['clase'],codigo_documental_atribuible=z['codigo'] if z['nivel']=='DOCUMENTAL_T1' else None,codigo_interno_adoptado=z['codigo'] if z['nivel']!='DOCUMENTAL_T1' else None,estado_interno=z['nivel'],requisito_pendiente=None)
        if z['nivel']=='PRIMER_T1_POSTERIOR':payload['marcas']=sorted(set(payload.get('marcas',[]))|{'OFERTA_AÑO_T1'})
        c.execute('update observaciones set payload=? where id=?',(json.dumps(payload,ensure_ascii=False,sort_keys=True),oid))
        c.execute('update asignaciones_v23 set nivel_asignacion=?,regla=?,año_T1_fuente=?,evidencia=?,clase=?,codigo=? where observacion_id=?',(z['nivel'],payload['regla'],z['anio_fuente'],json.dumps([evidence],ensure_ascii=False,sort_keys=True),evidence['clase'],z['codigo'],oid))
        granular.append({'observacion_id':oid,**evidence})
    c.commit();assert c.execute('pragma integrity_check').fetchone()==('ok',)
    changed={i for (i,orig),(j,now) in zip(source.execute('select id,payload from observaciones order by id'),c.execute('select id,payload from observaciones order by id')) if orig!=now};assert changed=={z['observacion_id'] for z in new}
    assert source.execute('select * from mu_anual order by rowid').fetchall()==c.execute('select * from mu_anual order by rowid').fetchall()
    source.close();c.close();dest=P/'DICCIONARIO_V23_CANDIDATA.sqlite';temp.replace(dest);dump(P/'REFERENCIAS_4_PRIVADAS.json',granular)
    meta=load(ROOT/old['capa_promedios']['metadata']);assert sha(ROOT/old['capa_promedios']['metadata'])==old['capa_promedios']['sha256'] and sha(meta['capa_privada']['ruta'])==meta['capa_privada']['sha256']
    meta['sha256_base_diccionario']=sha(dest);dump(destdir/'CAPA_PROMEDIOS.json',meta)
    desc=old|{'edicion':destdir.name,'estado':'CANDIDATA_NO_ACTIVA','DECISION':'H015 Fase 1. Propuesta para decisión posterior de Alexi.','ACTIVO_ANTERIOR':a,'base_privada':{'ruta':str(dest),'sha256':sha(dest)},'capa_promedios':{'metadata':str((destdir/'CAPA_PROMEDIOS.json').relative_to(ROOT)),'sha256':sha(destdir/'CAPA_PROMEDIOS.json')},'contrato':'v22 más las cuatro observaciones aprobables en asignaciones_v23. Separación documental/interna igual a v22. No seleccionada por activo.json.'};dump(destdir/'descriptor.json',desc)
    test_pointer={'descriptor':str((destdir/'descriptor.json').relative_to(ROOT)),'sha256':sha(destdir/'descriptor.json')}
    base_rates=probe(ROOT)
    with tempfile.TemporaryDirectory(dir=P) as t:
        root=Path(t);(root/'PROYECTO_IPSS.json').symlink_to(ROOT/'PROYECTO_IPSS.json')
        for f in [*desc['componentes_sha256'],test_pointer['descriptor'],desc['capa_promedios']['metadata']]:
            path=root/f;path.parent.mkdir(parents=True,exist_ok=True);path.symlink_to(ROOT/f)
        dump(root/ptr.relative_to(ROOT),test_pointer);trial=probe(root)
    assert all((v['numerador'],v['denominador'],v['delta_pp'])==(trial['tasas'][k]['numerador'],trial['tasas'][k]['denominador'],0.0) for k,v in base_rates['tasas'].items())
    assert ptr.read_bytes()==initial and sha(base)==old['base_privada']['sha256']
    dump(OUT/'QA_CANDIDATA.json',{'estado':'PASS_V23_CANDIDATA_NO_ACTIVA','activa':a,'descriptor_candidato':test_pointer,'observaciones_cambiadas':len(changed),'v22':base_rates,'ensayo_v23':trial,'metodo':'Mismo recálculo H013/H014. Control institucional sobre bases aprobadas. La nueva foto candidata no reemplaza los indicadores R19.'})
    print('PASS candidata',len(changed))
if __name__=='__main__':main()

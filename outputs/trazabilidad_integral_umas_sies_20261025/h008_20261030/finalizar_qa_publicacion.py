"""Lista de publicación propuesta y QA de privacidad/preservación; nunca stage/commit."""
import argparse,ast,json,re,subprocess
from pathlib import Path
from preparar import sha,load,write,txt

def main():
    p=argparse.ArgumentParser()
    for x in ['repo','privado']:p.add_argument('--'+x,required=True)
    a=p.parse_args();root=Path(a.repo);private=Path(a.privado)
    base=root/'outputs/trazabilidad_integral_umas_sies_20261025';out=base/'h008_20261030'
    initial=load(private/'ESTADO_INICIAL.json');cfg=load(private/'CONFIG.json')
    git=lambda *args:subprocess.check_output(['git','-C',str(root),*args],text=True)
    extras=[root/'docs/MAPA_RESULTADOS_GOBERNADOS.md',root/'docs/MAPA_RESULTADOS_GOBERNADOS.json',base/'PLAN_FASES_HITOS.md',base/'PLAN_FASES_HITOS_v2_20261030.md']
    auxiliary=['QA_PUBLICACION_H008.json','LISTA_PUBLICACION_H008.json','LISTA_PUBLICACION_H008.md','MANIFEST_H008.json']
    files=sorted([f for f in out.iterdir() if f.is_file() and f.name not in auxiliary]+extras)
    assert all(f.suffix in ('.json','.md','.py','.mjs','.png') for f in files)
    assert not any(f.is_dir() for f in out.iterdir()),'Apartar únicamente cachés propios de H008 antes de listar'
    known=set()
    for slot in load(cfg['entradas']['slots']['ruta']):
        known.update([txt(slot['persona']),txt(slot['documento_original'])])
        for c in slot['contextos']:known.update([txt(c['persona']),txt(c['CODCLI'])])
    for item in load(private/'DETALLE_C1_PRIVADO.json'):
        for c in item['observaciones']:known.update([txt(c['persona']),txt(c['CODCLI'])])
    known={x for x in known if len(x)>=6}
    literal=re.compile(r'(?<![\w])(?:'+'|'.join(re.escape(x) for x in sorted(known,key=len,reverse=True))+r')(?![\w])')
    patterns={
        'documento_DV':re.compile(r'(?<![\w])\d{7,8}-[0-9Kk](?![\w])'),
        'documento_puntuado':re.compile(r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b'),
        'valor_individual':re.compile(r'(?i)"(?:mrun|rut|CODCLI|N_DOC|nombre_alumno|telefono|correo)"\s*:\s*"?\d+'),
        'correo':re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),
        'telefono':re.compile(r'(?<!\w)(?:\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)')}
    findings=[]
    def scan(paths):
        for f in paths:
            if f.suffix=='.png':continue
            text=f.read_text()
            if f.suffix=='.json':json.loads(text)
            if f.suffix=='.py':ast.parse(text)
            for i,line in enumerate(text.splitlines(),1):
                if literal.search(line):findings.append({'ruta':str(f.relative_to(root)),'linea':i,'tipo':'identificador_conocido'})
                for kind,pat in patterns.items():
                    if pat.search(line):findings.append({'ruta':str(f.relative_to(root)),'linea':i,'tipo':kind})
    scan(files)
    before=json.loads(git('show',initial['head']+':docs/MAPA_RESULTADOS_GOBERNADOS.json'))
    now=load(root/'docs/MAPA_RESULTADOS_GOBERNADOS.json')
    byid=lambda m:{x['id']:x for x in m['resultados']}
    oldmap=byid(before);newmap=byid(now)
    r25=dict(newmap['R25']);r25.pop('pendientes_H008',None)
    changed=git('diff','--name-only').splitlines();allowed={str(f.relative_to(root)) for f in extras}
    status=git('status','--porcelain').splitlines()
    check={
        'HEAD_intacto':git('rev-parse','HEAD').strip()==initial['head'],
        'stage_vacio':not git('diff','--cached','--name-only').strip(),
        '25_cambios_ajenos_status_intacto':all(s in status for s in initial['status'].splitlines()),
        '25_archivos_ajenos_hash_intacto':all(sha(root/f)==h for f,h in initial['ajenos'].items()),
        'solo_modificaciones_tracked_autorizadas':set(changed)<=allowed,
        'R01_R24_intactos':all(oldmap[k]==newmap[k] for k in oldmap if k!='R25'),
        'R25_solo_pendientes':r25==oldmap['R25'],
        'R26_candidata':newmap['R26']['resultado_clave'].startswith('CANDIDATA'),
        'v2_conservada':sha(extras[3])==__import__('hashlib').sha256(git('show',initial['head']+':'+str(extras[2].relative_to(root))).encode()).hexdigest(),
        'fuentes_intactas':all(sha(x['ruta'])==x['sha256'] for x in cfg['entradas'].values()),
        'sin_XLSX_ni_detalle_privado_en_lista':all(f.suffix!='.xlsx' and '.local/share' not in str(f) for f in files),
        'escaneo_sin_hallazgos':not findings,
        'archivos_menores_20MB':all(f.stat().st_size<=20*1024*1024 for f in files)}
    qa={'estado':'PASS' if all(check.values()) else 'FAIL','clase':'C: privacidad y preservación; no cierra QA nativo pendiente',
        'controles':check,'hallazgos_sin_valores':findings,'archivos_escaneados':len(files),
        'limite_privacidad':'Patrones documento/DV/contactos y cotejo con identificadores privados conocidos. Revisión de esquema: conteos, códigos de catálogo y metadatos; no columnas de nombres individuales. PNG agregado revisado visualmente. No es certificación universal de identificación por texto libre.',
        'commit':False,'push':False}
    write(out/auxiliary[0],qa)
    proposed=sorted(files+[out/x for x in auxiliary])
    message='H008 prepara V25 sobre v20, inventaría fotos y documenta propuestas y límites de QA'
    write(out/auxiliary[1],{'estado':'PROPUESTA_NO_PUBLICADA','mensaje_commit_preparado':message,'rutas':[str(f.relative_to(root)) for f in proposed],'excluye':'Libro V25, copias QA y detalle privado; 25 cambios ajenos; ningún stage, commit ni push ejecutado.'})
    (out/auxiliary[2]).write_text('# Lista exacta propuesta · no publicada\n\nMensaje preparado: '+message+'\n\n'+''.join('- `'+str(f.relative_to(root))+'`\n' for f in proposed)+'\nEl libro y los intermedios personales permanecen privados. No se incluyen cambios ajenos. El QA de publicación no sustituye los pendientes nativos y de reproducción integral.\n')
    scan([out/x for x in auxiliary[:3]])
    assert not findings,'Revisar hallazgos sin publicar; no se muestran valores'
    write(out/auxiliary[3],{'hito':'H008','base_commit':initial['head'],'estado':'CANDIDATA_CON_LIMITES','version_plan':3,
        'fuentes':'FUENTES_H008.json; FUENTES_FOTOS_H008.json','QA':'QA_H008.json; QA_PUBLICACION_H008.json',
        'salidas':{str(f.relative_to(root)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in proposed if f.name!=auxiliary[3]},
        'sin_hash_propio':'Evita autorreferencia; este manifiesto integra la lista exacta','sin_commit_push':True})
    print(json.dumps({'estado':qa['estado'],'controles':check,'rutas_propuestas':len(proposed),'hallazgos':len(findings)},ensure_ascii=False))
    assert all(check.values())
if __name__=='__main__':main()

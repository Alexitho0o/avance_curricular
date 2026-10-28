"""Lee fuentes por hash y entrega sólo agregados; no persiste vínculos RUT–MRUN."""
import collections,csv,hashlib,json,sys
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from metodo_mu2026 import diagnosticar_mrun,codigos_con_diferencia
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main():
    cat=read(ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json');source=read(OUT/'FUENTE_MRUN2026_Y_LIMPIEZA.json')
    mr=Path(source['fuente_consolidada']['ruta_consolidada']);assert sha(mr)==source['fuente_consolidada']['sha256']
    base=Path(next(x['ruta_consolidada'] for x in cat['catalogo'] if x['sha256']=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'))
    assert sha(base)=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
    gp=ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json';assert sha(gp)=='fe8837a760d4ed132505bf92138145e08adb3ce0a2486c9e3f26f08ca11babfc'
    w=openpyxl.load_workbook(base,read_only=True,data_only=True);it=w['BASE_RETENCION_MU'].iter_rows(values_only=True);h=next(it);mu=[dict(zip(h,r)) for r in it if str(r[0])=='2026'];w.close()
    assert len(mu)==4105 and collections.Counter(str(r['VIG']) for r in mu)=={'0':960,'1':3145}
    with mr.open(newline='') as f:mrun=list(csv.DictReader(f))
    focus=codigos_con_diferencia();r=diagnosticar_mrun(mrun,mu,read(gp),focus)
    assert r['registros_mrun_foco']==2973 and len(r['por_codigo'])==48
    table=read(OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.json')['comparacion_abril_48_codigos'];ref={x['codigo_sies']:x for x in table}
    for x in r['por_codigo']:
        a=ref[x['codigo_sies']];assert x['registros_mrun']==a['publicacion_sies']
        x.update(vig1_nuestra=a['vig1_nuestra'],publicacion_sies=a['publicacion_sies'],brecha=a['brecha_publicado_menos_vig1'],candidatas_abril=a['nuestras_vig0_vigentes_abril_misma_familia'])
        x['con_alguna_candidata_vig0']=x['vig0_candidata_unica']+x['varios_solo_vig0']+x['varios_mixtos_vig1_vig0']
        x['capacidad_descriptiva_positiva']=min(max(x['brecha'],0),x['con_alguna_candidata_vig0'])
        x['pendiente_positivo_sin_candidata_vig0']=max(x['brecha'],0)-x['capacidad_descriptiva_positiva']
        x['dictamen']='C/E compatible en perfiles con alguna candidata VIG0; no acredita identidad' if x['con_alguna_candidata_vig0'] else 'E sin candidata VIG0 en perfiles comparables; no refuta ausencia de cobertura o errores de datos'
    summary={k:sum(x[k] for x in r['por_codigo']) for k in ('registros_mrun','vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato','varios_solo_vig1','varios_solo_vig0','varios_mixtos_vig1_vig0','con_alguna_candidata_vig0','capacidad_descriptiva_positiva','pendiente_positivo_sin_candidata_vig0','unicos_con_fila_mu_compartida_por_varios_registros_mrun','unicos_con_version_distinta')}
    summary['brecha_positiva']=sum(max(x['brecha'],0) for x in r['por_codigo']);summary['brecha_neta']=sum(x['brecha'] for x in r['por_codigo'])
    summary['nota_capacidad']='Conteo descriptivo por registro MRUN y perfiles, sin restricción uno a uno; no es número de identidades confirmadas ni prueba de cuáles VIG0 aceptó SIES.'
    r['resumen']=summary
    paths=[base,mr,gp,ROOT/'docs/recuperacion_cruce_mrun_umas_20261016.md',ROOT/'data/recuperacion_cruce_mrun_umas/20261016/manifest.json',ROOT/'scripts/diagnosticar_candidatos_mrun_umas.py',OUT/'metodo_mu2026.py',ROOT/'manual_matrícula_unificada.txt']
    r['fuentes']=[{'ruta':str(p),'sha256':sha(p)} for p in paths]
    r['referencias_reglas']={'A':'docs/recuperacion_cruce_mrun_umas_20261016.md y esquema MRUN; GEN_ALU 1/2 y FEC_NAC_ALU AAAAMM, 190001 sin dato. Manual MU2026 sexo H hombre/M mujer.','B':'H2 y base MU142342 intactos por SHA-256; 3.425 registros MRUN2026, 4.105 matrículas MU.','C':'Bloqueos A/B/C reutilizados; candidatos por perfil y agregados por código.','D':'Cierres operativos Alexi28-10; no cambia bases ni tasas.','E':'Identidad, reciprocidad y causa de aceptación SIES no acreditadas; no usar diagnóstico como enlace personal.'}
    (OUT/'DIAGNOSTICO_BRECHA_MRUN2026.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    lines=['# Diagnóstico MRUN2026 frente a MU — brecha 226','','C/E: diagnóstico por perfiles, no prueba de identidad. Nunca se guardan pares RUT–MRUN.','','## Fuente y alcance [B/C]','','H2 íntegro de 24.386 filas; subconjunto2026 de3.425 (3.371 pregrado+54 postítulo), con cero diferencias por código frente a publicación. Foco exclusivo:48 códigos,2.973 registros MRUN. Base de candidatos:4.105 matrículas MU (3.145 VIG1+960 VIG0). No se utiliza versión como bloqueo.','','## Clasificación final [C/E]','','| Clase | Registros MRUN |','|---|---:|']
    for k in ('vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato'):lines.append(f"| {k} | {summary[k]} |")
    lines+=['',f"Entre los ambiguos: {summary['varios_solo_vig1']} sólo VIG1; {summary['varios_solo_vig0']} sólo VIG0; {summary['varios_mixtos_vig1_vig0']} mixtos.",f"Registros con alguna candidata VIG0: {summary['con_alguna_candidata_vig0']}. Capacidad descriptiva por código para brecha positiva: {summary['capacidad_descriptiva_positiva']}/228; sin candidatura VIG0 suficiente: {summary['pendiente_positivo_sin_candidata_vig0']}. {summary['nota_capacidad']}",f"Unicidades cuyo candidato también es compatible con otros registros MRUN: {summary['unicos_con_fila_mu_compartida_por_varios_registros_mrun']}. Unicidades con versión distinta: {summary['unicos_con_version_distinta']}. No se convierten en enlaces certificados.",'','## Reglas reutilizadas y adaptación de esquema','','Año+nacimiento AAAAMM+sexo (A); más familia ISCJ, V libre (B); tipo sólo con perfil gobernado unánime (C). birth se importa del script16-10 sin ejecutar su main. MRUN1=Hombre→MU H, MRUN2=Mujer→MU M; no se confunde con UMAS M/F. 190001 y sexos no comparables no generan candidatos. Sin nombre, aproximación ni método probabilístico.','','La MU ya contiene familia; para tipo se reúnen los perfiles gobernados de todos los grupos compatibles con esa familia, sin elegir CODCLI por semejanza. Si faltan perfiles o difieren, C conserva B. Esta adaptación conservadora no acredita tipo personal.','','## Comparación por código','','| Código | MRUN | VIG1 nuestra | Brecha | Único VIG1 | Único VIG0 | Varios | Sin candidato | Alguna candidata VIG0 | Pendiente positivo |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for x in r['por_codigo']:lines.append('| '+x['codigo_sies']+' | '+' | '.join(str(x[k]) for k in ('registros_mrun','vig1_nuestra','brecha','vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato','con_alguna_candidata_vig0','pendiente_positivo_sin_candidata_vig0'))+' |')
    lines+=['','## Dictamen','','La presencia de candidatos VIG0 permite evaluar compatibilidad con la hipótesis, no identificar cuáles registros SIES corresponden a nuestras nóminas. Las ambigüedades, candidatos compartidos y sin candidato permanecen E. Brecha neta226 y tasas originales intactas. El diagnóstico MRUN no reemplaza una descarga PES identificada por documento.','','Resultados A y B intermedios, aplicación de tipo y hashes: JSON adjunto.']
    (OUT/'DIAGNOSTICO_BRECHA_MRUN2026.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()

"""Documenta H010b desde agregados; no recalcula asignaciones ni indicadores."""
import argparse,json
from pathlib import Path
from construir import dump,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);ap.add_argument('--commit-reglas',required=True);a=ap.parse_args();R=a.repo.resolve();P=a.privado;O=R/'outputs/regla_t1_h010_20261030';load=lambda p:json.loads(Path(p).read_text())
 cov=load(O/'COBERTURA_H010B.json');period=load(O/'PERIODOS45_H010B.json');sim=load(O/'EFECTO_HIPOTETICO_PERIODOS45.json');q=load(O/'QA_RESOLUCION_H010B.json')
 def table(rows,fields):return '\n'.join(['| '+' | '.join(fields)+' |','|'+'---|'*len(fields)]+['| '+' | '.join(str(z.get(k,'')) for k in fields)+' |' for z in rows])
 levels=sorted({x['nivel_asignacion'] for v in cov.values() for t in ['antes','despues'] for x in v[t]});cr=[]
 for level in levels:
  row={'Nivel':level}
  for k,label in [('v7_3049','3049'),('V24_99_posiciones','99')]:
   for t in ['antes','despues']:row[label+' '+t]=next((z['n'] for z in cov[k][t] if z['nivel_asignacion']==level),0)
  cr.append(row)
 report=f'''
## H010b · cierre con D1–D3 (30-10-2026)

Lo anterior documenta la línea base H010. Esta sección es el resultado actualizado;
no reinterpreta sus asignaciones previas. **D:** decisiones de Alexi; **B/C:**
evidencia y aplicación; **E:** requisitos pendientes. v21 sigue CANDIDATA, v20 activo.

{table(cr,['Nivel','3049 antes','3049 despues','99 antes','99 despues'])}

Se agregan {cov['v7_3049']['nuevas']} asignaciones a las 3.049 observaciones históricas.
Entre las 99 posiciones se agregan {cov['V24_99_posiciones']['nuevas']}; E pasa de 38 a 0.
En todo v20 se agregan {cov['v20_completa']['nuevas']} asignaciones candidatas.
Los universos no se suman: las 99 son posiciones de seguimiento, no observaciones únicas.
No cambia el numerador ni denominador de H001/R19: **0,00 pp por conservación**.

### Residual E histórico final

{table(cov['v7_3049']['residual_E'],['motivo','n'])}

Fuente: `RESIDUAL_H010B.json`, con requisito exacto y conteos por año, período,
plan, sede y jornada. Los 604 de períodos 4/5 se separan de los 360 restantes.
Los 48 con T1 previo, sin posterior, no pueden rotularse NUNCA_INFORMADO:
requieren decisión explícita sobre ese arrastre anterior. No se extiende D1 por analogía.
Los 273 sin tipo/duración necesitan perfil gobernado; 28 carecen de VIGENCIA 1
compatible; 2 tienen varias; 1 mantiene ambigüedad anual; 2 no tienen código
compatible y 6 no tienen primer T1 inequívoco con las mismas dimensiones.

### Controles y alcance de D1–D3

`resolver_h010b.py` lee la salida privada congelada de H010. Sólo revisa E en
motivos que encajan en D1–D3; todas las asignaciones anteriores se conservan.
D2 también cubre residuales 2026 que antes tenían motivo T1 sin línea: por eso
su nivel final no se limita a los 767 del motivo original. Los cruces por motivo
anterior/nuevo quedan en `TRANSICIONES_H010B.json`.

Cada alta tiene perfil v2 compatible, código en oferta del año, sede y jornada
coherentes. D2 exige VIGENCIA 1 de 2026, no de 2027. D3 usa tipo/duración antes
de VIGENCIA 1. H002 aporta la familia del plan; no se elige por nombre. Un T1
posterior también se contrasta con la oferta del año del contexto. Todo queda
separado de DOCUMENTAL_T1 y de la regla MU2027. NUNCA_INFORMADO se limita al
mismo expediente/plan y fuentes disponibles; no afirma inexistencia en SIES.

### Períodos 4/5: investigación terminada, homologación no aplicada

Fuente: `PERIODOS45_H010B.json/.md`. De 604 contextos: 598 BIMESTRAL, 3 SEMESTRAL,
3 TRIMESTRAL (campo original REGIMEN; se informa como REGIMEN_FUENTE).
Hay {period['personas_historicas_unicas']} personas distintas; {period['personas_historicas_con_123']}
aparecen también en 1/2/3 del mismo año. Carreras, planes, años y coexistencia
están desglosados en el JSON, sin identificadores.

PROMEDIOS no contiene inicio/término de período. La FECHAMATRICULA de Datos
Alumnos no los reemplaza. El calendario trimestral 2026 catalogado define
T1/T2/T3 (páginas 2, 5, 7, 8 y 9), pero no define 4/5 ni años históricos.
**E:** falta calendario/definición UMAS por año y régimen; no se acredita verano.

Propuesta: conservar los períodos nativos; sólo con definición del mismo año,
someter a Alexi herencia de su T1 o primer T1 posterior, con tipo/duración y
oferta anual. Escenario condicionado a actividad del mismo año, **C/E no aplicado**:
{table(sim['por_nivel'],['nivel_asignacion','n'])}
La simulación prueba T1 del mismo expediente/plan/año y, si falta, D1–D3.
No acredita fechas ni transforma períodos. Ninguno de los 604 se asigna en H010b.

### QA y reproducción

`QA_H010B.json` integra pruebas, reproducción de hashes, preservación de v20,
R01–R04/R19, V25/V26, mapa R01–R28 y los 25 cambios ajenos. No se abrió Excel.
El detalle sólo reside en la carpeta privada; la base candidata es un derivado
nuevo que conserva tablas v20 y añade las asignaciones en una tabla separada.
`MANIFEST.json` y `LISTA_PUBLICACION.json` sustituyen sólo el cierre de publicación;
se conservan los manifiestos/lista/descriptor H010 anteriores.

Regla D1–D3: IPSS_IA_SKILLS_Y_REGLAS **1.3.13**, commit `{a.commit_reglas}`.
Publicación de H010/H010b autorizada en este prompt, condicionada a QA y privacidad.
Mensaje: `H010 asigna código de contexto por primer T1 informado; H010b aplica D1–D3 y documenta períodos 4/5`.
'''
 p=O/'INFORME_H010.md';s=p.read_text().split('\n## H010b ·')[0];p.write_text(s.rstrip()+'\n'+report)
 # Transiciones agregadas, mismas unidades de cobertura.
 before=load(P/'ASIGNACIONES_PRIVADAS.json');after=load(P/'ASIGNACIONES_H010B_PRIVADAS.json');from construir import aggregate
 transitions=[{'anio':b['anio'],'periodo':b['periodo'],'motivo_h010':b['motivo'],'nivel_h010b':z['nivel_asignacion'],'motivo_h010b':z['motivo']} for b,z in zip(before,after) if b['nivel_asignacion']=='E'];import sqlite3
 d7=load(R/'data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json');db=sqlite3.connect(Path(d7['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True);hist={z['observacion_id'] for t in db.execute('select payload from observaciones') if not (z:=json.loads(t[0])).get('codigo_interno_adoptado')};db.close()
 htrans=[{'motivo_h010':b['motivo'],'nivel_h010b':z['nivel_asignacion'],'motivo_h010b':z['motivo']} for b,z in zip(before,after) if b['observacion_id'] in hist and b['nivel_asignacion']=='E']
 dump(O/'TRANSICIONES_H010B.json',{'clase':'B/C','universo':'v20 completo y subconjunto histórico; no sumar entre universos','casos':aggregate(transitions,['anio','periodo','motivo_h010','nivel_h010b','motivo_h010b']),'historico_3049':aggregate(htrans,['motivo_h010','nivel_h010b','motivo_h010b'])})
 dp=R/'data/diccionario_sies_seguimiento/v21_20261030_candidata_h010/descriptor.json';d=load(O/'DESCRIPTOR_H010_ANTES.json');d['base_privada']={'ruta':str(P/'DICCIONARIO_V21_H010B_CANDIDATA.sqlite'),'sha256':q['base_privada_sha256']};d['actualizacion']='H010b D1–D3; CANDIDATA, períodos 4/5 sin asignar';d['componentes_sha256']['outputs/regla_t1_h010_20261030/resolver_h010b.py']=sha(O/'resolver_h010b.py');dump(dp,d)
 mp=R/'docs/MAPA_RESULTADOS_GOBERNADOS.json'
 if not (P/'MAPA_H010_ANTES.json').exists():(P/'MAPA_H010_ANTES.json').write_bytes(mp.read_bytes())
 m=load(mp);rr=next(x for x in m['resultados'] if x['id']=='R29');rr.update(resultado_clave='CANDIDATA v21 H010/H010b: 3.049 observaciones, 2.085 respaldadas y 964 E (604 períodos 4/5, 360 otros); 99 posiciones respaldadas, E 0. D1–D3 aplicadas sólo a residuales. Tasas 0,00 pp por conservación; no activación.',hoja_o_seccion='H010b: cobertura, residuales y períodos 4/5',commit='PUBLICACION_H010_H010B; base 6505cae',script_productor='outputs/regla_t1_h010_20261030/resolver_h010b.py',sha256=sha(p),limites='Períodos 4/5 sin homologar; sin T1 posterior con antecedente previo queda E. NUNCA_INFORMADO sólo ausencia en fuentes disponibles; D2 no convierte cohorte 2026 en 2027.')
 mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');md=R/'docs/MAPA_RESULTADOS_GOBERNADOS.md';line='| '+' | '.join([rr['id']+' · '+rr['pregunta'],rr['resultado_clave'],rr['archivo'],rr['script_productor'],rr['commit'],rr['sha256'],rr['clase'],rr['fecha_resultado'],rr['no_recalcular_salvo']])+' |';md.write_text('\n'.join(line if x.startswith('| R29 ·') else x for x in md.read_text().splitlines())+'\n')
 plan=R/'docs/ESPECIFICACION_H010.md';s=plan.read_text().split('\n## H010b ·')[0];plan.write_text(s.rstrip()+'''

## H010b · extensión autorizada, 30-10-2026

D1: T1 sin línea y actividad sin MU anual → primer T1 posterior del mismo expediente/plan; sin T1 localizado, código vigente anual compatible. D2: ingreso 2026 sin MU → código VIGENCIA 1 compatible del año 2026; nunca cohorte 2027. D3: cambios de carrera/plan/sede/jornada → tipo/duración y, sólo si hay empate, vigencia; ambigüedad E. No recalcular asignaciones previas.

Períodos 4/5: investigar régimen, coexistencia, fechas y documentación; no asignar. Parada: cada residual tiene motivo y requisito; no abrir otra iteración para forzar cobertura.

Reproducción sin abrir Excel:

```sh
python resolver_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
python investigar_periodos_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
python documentar_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010" --commit-reglas "$COMMIT_REGLAS"
python qa_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
```

Los scripts están en outputs/regla_t1_h010_20261030/. QA conserva fuentes, indicadores y 25 cambios ajenos. Publicar sólo LISTA_PUBLICACION.json si QA y privacidad pasan. v20 sigue activo; v21 candidata.
''')
if __name__=='__main__':main()

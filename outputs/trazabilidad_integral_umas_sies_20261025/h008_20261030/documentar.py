"""Documentación agregada de H008 desde evidencias existentes y su inventario."""
from pathlib import Path
import argparse,json,hashlib
from preparar import load,write,table,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--privado',required=True);p.add_argument('--salida',required=True);a=p.parse_args();r=Path(a.repo);o=Path(a.salida);priv=Path(a.privado)
    photos=load(o/'FUENTES_FOTOS_H008.json');byname={Path(x['ruta']).name:x for x in photos}
    p25=next(x for x in photos if 'T3_2025' in x['ruta']);p26=next(x for x in photos if '10246' in x['ruta']);p263=next(x for x in photos if '12159' in x['ruta']);p252=next(x for x in photos if 'T2_2025' in x['ruta'])
    combos=[]
    for coh,year,period,n,photo,state,why in [
        (2024,2025,2,282,p252,'parcial','225 filas, todas de ingreso 2025: no es una foto completa del padrón T1 2024.'),
        (2024,2025,3,261,p25,'hallada','Foto T3_2025 completa reutilizada, ahora visible como respaldo de seguimiento 2024→2025; no sustituye el proxy T3 2024 de R19.'),
        (2025,2025,2,451,p252,'parcial','225 filas de ingreso T2; cobertura literal T1 4/1150. No acredita el estado de quienes no están en ella.'),
        (2025,2025,3,0,p25,'hallada','La foto ya estaba en R19. No es hallazgo nuevo ni tiene C4.'),
        (2026,2026,2,420,p26,'hallada','14204 filas; padrón T1 completo localizado literalmente 1471/1471. Manifiesto congelado y hash coincidentes.'),
        (2026,2026,3,0,p263,'hallada','La foto ya estaba en R19. No es hallazgo nuevo ni tiene C4.')]:
        cov=next(x for x in photo['cobertura_documento_literal_T1'] if x['cohorte']==coh)
        combos.append({'cohorte':coh,'anio':year,'periodo_nativo':period,'C4':n,'estado':state,'filas':photo['filas'],'cobertura_literal':f"{cov['coincidencias']}/{cov['universo']}",'ruta':photo['ruta'],'sha256':photo['sha256'],'corte':f'Cierre período {period} de {year}; D Alexi 30-10-2026, sin exigir fecha exacta','causa':why,'clase':'B/C/D; limitaciones E'})
    write(o/'INVENTARIO_FOTOS_H008.json',{'combinaciones':combos,'C4':1414,'C4_con_foto_hallada':681,'C4_foto_parcial':733,'decision_corte':'D Alexi: no importa la fecha; las fotos son el cierre del 2 y 3','rutas_buscadas':['Escritorio','Descargas (incluye cierre/)','CARACTERIZACIÓN (incluye .local/)','avance_curricular/data','avance_curricular/outputs'],'no_aceptar_como_historia':'Las carpetas de análisis anual P1/P2/P3 con DATOSDEALUMNOS_11998 son copias de una extracción de octubre, no fotos distintas por trimestre.'})
    md=['# Inventario de fotos H008','D · Alexi, 30-10-2026: «no importa la fecha las fotos son el cierre del 2 y 3». Se registra corte académico, no se inventa día de extracción ni cierre.','B/C · Se buscaron archivos, incluidos los ignorados por Git, en Escritorio, Descargas, CARACTERIZACIÓN/.local, avance_curricular/data y outputs. El inventario de rutas de búsqueda queda privado; aquí solo fuentes pertinentes.',table(combos,['cohorte','anio','periodo_nativo','C4','estado','filas','cobertura_literal','causa']),
        'B/C · 681 de las 1414 posiciones C4 tienen ahora foto disponible; 733 quedan en dos combinaciones con foto parcial. Esto mide disponibilidad de fuente, no 681 matrículas vigentes. Las otras dos combinaciones tienen C4=0.',
        'C · Cobertura literal usa el documento completo normalizado; el complemento de foto aplica la llave corporal y año de ingreso heredados de R19, declarando su límite. No se adjudica expediente T1.',
        '## Fuentes y descartes']
    for x in photos:
        md+=['',f"- B · `{x['ruta']}`; hoja `{x['hoja']}`; {x['filas']} filas; SHA-256 `{x['sha256']}`. {x['corte']}."]
    md+=['','- B/C · El listado de ingreso T2-2026 contiene 528 filas y carece de estado académico individual: no sustituye la foto completa 10246. El listado T3-2026 de 557 filas es parcial frente al padrón; se conserva la foto 12159 de R19.',
        '- B/C · Foto Ret. Intertrimestral.xlsx es un derivado con una regla de mismo año y sin filtro de ingreso, distinta de R19. No se utiliza para redefinir sus tasas ni como nueva foto cruda.',
        '- E · No se localizó una foto completa T2-2025 en las ubicaciones examinadas. Se solicita una sola fuente que cubra ambas cohortes, no dos extracciones redundantes.']
    (o/'INVENTARIO_FOTOS_H008.md').write_text('\n\n'.join(md)+'\n')
    (o/'SOLICITUD_FOTOS_UMAS.md').write_text('''# Borrador de solicitud · NO ENVIADO

Solicitamos la foto completa del cierre del período nativo 2 de 2025, incluyendo expedientes de todos los años de ingreso y todos los estados al cierre. Se utilizará para localizar el padrón T1 de las cohortes 2024 y 2025; el listado disponible de 225 ingresos T2 no cubre ese universo.

D · Alexi confirmó que se trabaja con el cierre de T2/T3 y no exige una fecha exacta. Indicar en la entrega que corresponde al cierre académico 2025-2; si la foto disponible no representa ese cierre, informar su alcance sin reconstruirlo con el estado actual.

Campos mínimos: tipo de documento, documento y DV separados; identificador de expediente; código de carrera/plan; año y período de ingreso; año y período de matrícula; sede y jornada; estado académico y situación al cierre. No se requieren nombres, contactos, dirección, datos financieros ni notas.

Formato: XLSX o CSV UTF-8 con encabezados, una fila por expediente del corte, catálogo de valores de estado/situación adjunto si difiere del vigente. Entrega por canal institucional restringido; el detalle se mantendrá privado. Uso: cobertura y vigencia de la foto bajo R19, sin modificar H001 ni interpretar ausencia como deserción.

Decisión Alexi: aprobar envío / ajustar / no enviar: ____.
''')
    # No se recuenta MRUN: comparación de versiones y hashes conocidos.
    cat=load(r/'data/catalogo_fuentes/CATALOGO_FUENTES.json')['catalogo'];checks=[]
    for filename in ['Matricula_2007_2026_WEB_10_07_2026.csv','MRUN_MATRICULA_IPSS_162_2026_H2.csv']:
        e=next(x for x in cat if x['archivo']==filename);p=Path(e['ruta_consolidada']);h=sha(p);assert h==e['sha256'];checks.append({'archivo':filename,'ruta':str(p),'sha256':h,'igual_al_catalogo':True})
    write(o/'CONTROL_FUENTES_MRUN.json',{'clase':'B/C; R09 causa E','estado':'SIN_FUENTE_NUEVA_LOCALIZADA','fuentes':checks,'publicacion_fecha_nombre':'2026-07-10','MRUN_2026_version':'H2 ya utilizado por R09/H007','limite':'Fecha de copia/modificación local no es fecha de publicación. No se recalculan conteos ni se reabre R09.'})
    (o/'MRUN_H008.md').write_text('# MRUN 2026\n\nB/C · Sin fuente nueva localizada: publicación 10-07-2026 y MRUN H2 mantienen los hashes ya gobernados; R09 sigue CERRADA_DOCUMENTADA, causa E. Evidencia: CONTROL_FUENTES_MRUN.json.\n')
if __name__=='__main__':main()

"""Escribe sólo el protocolo futuro; no lee ni reconstruye cargas PES."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def preparar():
    manual=ROOT/'manual_matrícula_unificada.txt'
    plan={
        'estado':'PREPARADO_NO_EJECUTADO',
        'proceso':'Matrícula Unificada 2026; institución 162',
        'clase':'A manual; C diseño; E llave PES y recepción individual por acreditar',
        'manual':{'ruta':str(manual),'sha256':sha(manual),'pagina_15_lineas':'468–478','pagina_15':'Las cargas son acumulativas; actualizan registros al volver a cargarse correctamente (Terminado ok); el resultado exitoso es Finalizado.','pagina_16_lineas':'483–498','pagina_16':'Historial de Carga ordenado por fecha; campos Fecha Inicio, Fecha Fin, Resultado; acción ver el archivo cargado.'},
        'fuentes_requeridas':[
            {'fuente':'Export o captura del Historial de Carga MU2026 que descargará Alexi','campos':['identificador de carga, si existe','Fecha Inicio','Fecha Fin','Resultado','evidencia de eliminación/reinicio, si existe'],'validacion':'Transcribir capturas con revisión; conservar imagen original en privado, ruta y hash. Ordenar por el orden acreditado de aplicación; tiempos empatados o contradictorios quedan E.'},
            {'fuente':'ver el archivo cargado de cada carga Finalizado, descargado de PES por Alexi','metadatos':['vínculo a la fila del historial','ruta privada','SHA-256','filas','columnas','codificación','delimitador'],'validacion':'Cada archivo debe corresponder a su carga exitosa y tener esquema individual interpretable. Los nombres de envío no prueban aceptación.'}
        ],
        'fuentes_prohibidas_para_reconstruccion':['Nuestros archivos locales de envío','*_orig.zip','*_PARA_SUBIR.csv','CSV de errores','Consolidados o rectificaciones reconstruidos internamente'],
        'llaves_candidatas':[
            {'id':'L1','clase':'C/E sensibilidad','campos':['TIPO_DOC','N_DOC','DV','CODIGO_UNICO'],'nota':'Documento incluye tipo, número y DV; no cuerpo de RUT solo.'},
            {'id':'L2','clase':'C/E sensibilidad','campos':['TIPO_DOC','N_DOC','DV','COD_CAR'],'nota':'Llave gruesa: excluye sede, jornada y versión; puede sobrescribir registros de distintos contextos de la misma carrera.'}
        ],
        'normalizacion':[
            'Conservar originales y columnas derivadas; None se distingue de 0. Prohibido x or vacío para documento/DV.',
            'Conservar tipo documental y ceros iniciales textuales; DV 0 sigue siendo 0. Sin aproximaciones ni cruces por nombre.',
            'Validar institución I162 y coherencia de código completo con S/C/J/V. No inventar componentes ni resolver discrepancias por totales.'
        ],
        'antecedente_llaves_equivalentes':{'clase':'C','llave_1_original':['TIPO_DOC','N_DOC','DV','CODIGO_UNICO'],'llave_2_original':['TIPO_DOC','N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION'],'conclusion':'Con institución I162 fija, código completo coherente y componentes normalizados, las dos formulaciones originales son equivalentes. La segunda se reemplaza por documento + COD_CAR para ofrecer una sensibilidad distinta.'},
        'relacion_llaves_vigentes':'L1 conserva sede, jornada y versión dentro del código único; L2 agrupa por documento + COD_CAR y puede unir contextos distintos. Ambas son sensibilidad C/E, no llave normativa PES acreditada.',
        'hipotesis_sensibilidad':{'clase':'C/E','condicion':'Si L1 reproduce la publicación mejor que L2, y el linaje identifica registros antiguos no sobrescritos bajo L1 que L2 sustituye.','interpretacion':'Los registros antiguos no sobrescritos son una explicación candidata, no aceptación SIES ni demostración causal.','evaluacion_futura':'Comparar discrepancia absoluta total por código y cantidad de códigos coincidentes, en el mismo universo pregrado; mostrar también el neto y el foco de 48 códigos, sin elegir por compensación de diferencias. Si las métricas discrepan, informar el resultado mixto.','resultado':None},
        'algoritmo_futuro_no_ejecutado':[
            'Verificar hashes y relación archivo recibido ↔ fila del historial. Admitir sólo Finalizado; documentar errores y faltantes sin aplicarlos.',
            'Acreditar el orden de aplicación y cualquier eliminación/reinicio antes de acumular; no asumir que no existieron.',
            'Mantener dos estados en paralelo, indexados por L1 documento + código único y L2 documento + COD_CAR. Una llave repetida reemplaza el registro completo con el de la carga posterior; VIG 0 actualiza, no elimina físicamente.',
            'Duplicados incompatibles dentro de una carga o sin orden acreditado bloquean el grupo; no elegir primera ni última fila por conveniencia.',
            'Conservar linaje de cada llave: primera carga, última carga, cambios VIG, y si una llave antigua nunca volvió a ser sobrescrita.',
            'Conciliar ambos estados en privado y producir sólo agregados VIG1/VIG0 por código, incluidas altas antiguas no sobrescritas; separar registros de L1 que la llave gruesa L2 sustituye.',
            'Comparar con 3.371 pregrado publicados y 3.145 VIG1 nuestras, más los 48 códigos con diferencia; no ajustar bases ni tasas.'
        ],
        'controles_futuros':['Cobertura del historial y todos los archivos Finalizado','Identidad y componentes completos; DV 0 conservado','Orden acreditado, sin empates no resueltos','Reinicio/eliminación documentado o incidencia E explícita','Linaje de actualizaciones y llaves antiguas','Equivalencia de las dos formulaciones originales; L1 vigente y L2 gruesa no se fuerzan a coincidir','Comparación por código de discrepancia absoluta, códigos coincidentes y neto, con linaje de sobrescritura','Sumas de registros/matrículas/personas con unidades separadas','Salida sin identificadores'],
        'estado_reconstruido':None,'vig1_resultante':None,'llaves_antiguas_no_sobrescritas':None,
        'ejecucion_con_archivos_reales':False,
        'limitacion':'Este entregable es protocolo y esquema de sensibilidad; no implementa ni ejecuta aún una reconstrucción de PES.'
    }
    (OUT/'PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    lines=['# Preparación de reconstrucción acumulativa MU2026','','Estado: PREPARADO_NO_EJECUTADO. C/E: las llaves candidatas no están acreditadas como llave normativa PES.','','## Base oficial [A]','','Manual MU2026 p.15, líneas 468–478: cargas acumulativas, actualización al cargarse correctamente y resultado Finalizado. P.16, líneas 483–498: Historial de Carga ordenado por fecha y acción ver el archivo cargado.','',f"Manual: {manual}. SHA-256: `{plan['manual']['sha256']}`.",'','## Lo que descargará Alexi','','1. Export o captura del Historial de Carga MU2026, con fechas, resultados y evidencia disponible de reinicios/eliminaciones.','2. El archivo cargado de cada fila Finalizado, vinculado a esa fila y conservado con SHA-256 en privado.','','No se reconstruirá con nuestros envíos locales, archivos orig.zip, PARA_SUBIR ni reportes de errores.','','## Antecedente: las formulaciones originales eran equivalentes [C]','',plan['antecedente_llaves_equivalentes']['conclusion'],'','## Dos llaves vigentes de sensibilidad [C/E]','','| Llave | Campos |','|---|---|','| L1 | Tipo documental + número + DV + código único |','| L2, gruesa | Tipo documental + número + DV + COD_CAR; sin sede, jornada ni versión |','',plan['relacion_llaves_vigentes'],'','## Hipótesis que se evaluará, sin ejecutar [C/E]','',plan['hipotesis_sensibilidad']['condicion'],plan['hipotesis_sensibilidad']['interpretacion'],plan['hipotesis_sensibilidad']['evaluacion_futura'],'','## Procedimiento futuro, no ejecutado','']
    lines += [f'{i}. {s}' for i,s in enumerate(plan['algoritmo_futuro_no_ejecutado'],1)]
    lines+=['','Fuentes faltantes y controles se detallan en el JSON. No se informa aún VIG1 reconstruida ni número de llaves antiguas.']
    (OUT/'PREPARACION_CARGAS_ACUMULATIVAS_MU2026.md').write_text('\n'.join(lines)+'\n')
    print('Protocolo preparado. Reconstrucción PES no ejecutada; sin lectura de envíos locales.')

if __name__=='__main__':preparar()

"""F0 - Diagnostico de factibilidad de conciliacion RUT (U+) <-> MRUN (SIES).

Solo lectura. No ejecuta cruce real ni tecnica probabilistica. No exporta RUT
ni MRUN sin enmascarar (aqui no se exporta ninguno: solo estadisticas
agregadas). Ver gobernanza/trazabilidad_mrun/MANIFIESTO_TRAZABILIDAD_MRUN.md
y F0_DIAGNOSTICO_FACTIBILIDAD.md para la interpretacion completa.

Variables de bloqueo usadas: fecha de nacimiento (truncada a AAAAMM, unica
resolucion disponible en SIES), sexo (mapeo 1=M/2=F NO confirmado contra
manual oficial, ver hallazgo de gobernanza), ano de ingreso minimo por
persona, y carrera (via PUENTE_SIES_COMPILADO.tsv, solo combinaciones
RESOLUCION_STATUS == UNICO).
"""
import sys

import pandas as pd

P_UPLUS = (
    '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/'
    'Prompts IA/DATOSDEALUMNOS_11146.xlsx'
)
P_SIES = (
    '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/'
    'PNM2007_2026_LOCAL_DATA/PNM_PROF27_ANALISIS_SEGURO/FUENTE_GRANULAR/'
    'reporte_matricula_ip_san_sebastian_2007_2026_20260901.csv'
)
P_PUENTE = '/Users/alexi/Documents/GitHub/avance_curricular/control/catalogos/PUENTE_SIES_COMPILADO.tsv'

MAPA_GEN_SIES = {'1': 'M', '2': 'F'}  # heuristico, NO confirmado contra manual SIES/PES


def cargar_personas_uplus():
    up = pd.read_excel(P_UPLUS, dtype=str)
    puente = pd.read_csv(P_PUENTE, sep='\t', dtype=str)
    puente_unico = puente[puente['RESOLUCION_STATUS'] == 'UNICO'][['JORNADA', 'CODCARPR', 'CODIGO_UNICO_FINAL']]
    mapa_codigo_unico = dict(
        zip(puente_unico['JORNADA'].str.strip() + '|' + puente_unico['CODCARPR'].str.strip(),
            puente_unico['CODIGO_UNICO_FINAL'])
    )

    up['_rut'] = up['RUT'].str.strip()
    up['_sexo'] = up['SEXO'].str.strip().str.upper()
    up['_fecnac_ym'] = pd.to_datetime(up['FECHANACIMIENTO'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y%m')
    up['_anoingreso'] = pd.to_numeric(up['ANOINGRESO'], errors='coerce')
    up['_codigo_unico_sies'] = (up['JORNADA'].str.strip() + '|' + up['CODCARPR'].str.strip()).map(mapa_codigo_unico)

    # carrera "actual" = registro con mayor ANOINGRESO por RUT
    actual = up.sort_values('_anoingreso').groupby('_rut').tail(1).set_index('_rut')['_codigo_unico_sies']

    personas = up.groupby('_rut').agg(
        fecnac_ym=('_fecnac_ym', 'first'),
        sexo=('_sexo', 'first'),
        ano_ingreso_min=('_anoingreso', 'min'),
    ).reset_index()
    personas['codigo_unico_sies'] = personas['_rut'].map(actual)
    return personas, mapa_codigo_unico


def cargar_personas_sies():
    sies = pd.read_csv(P_SIES, dtype=str)
    sies['_mrun'] = sies['mrun'].str.strip()
    sies['_gen'] = sies['gen_alu'].str.strip()
    sies['_fecnac_ym'] = sies['fec_nac_alu'].str.strip()
    anio = pd.to_numeric(sies['anio_ing_carr_ori'], errors='coerce')
    anio = anio.where(anio != 9998)
    sies['_anio_ori'] = anio
    sies['_codigo_unico'] = sies['codigo_unico'].str.strip()

    codigos_por_mrun = sies.groupby('_mrun')['_codigo_unico'].apply(set)
    personas = sies.groupby('_mrun').agg(
        fecnac_ym=('_fecnac_ym', 'first'),
        gen=('_gen', 'first'),
        anio_ing_min=('_anio_ori', 'min'),
    ).reset_index()
    personas['sexo_mapeado'] = personas['gen'].map(MAPA_GEN_SIES)
    personas['codigos_unicos'] = personas['_mrun'].map(codigos_por_mrun)
    return personas


def main() -> int:
    personas_up, mapa_codigo_unico = cargar_personas_uplus()
    personas_sies = cargar_personas_sies()

    print(f'Personas unicas U+ (RUT): {len(personas_up)}')
    print(f'Personas unicas SIES (MRUN), IP San Sebastian 2007-2026: {len(personas_sies)}')
    print(f'Combinaciones JORNADA+CODCARPR con codigo SIES unico resuelto (bridge): {len(mapa_codigo_unico)}')
    cobertura = personas_up['codigo_unico_sies'].notna().mean()
    print(f'Personas U+ cuya carrera actual resuelve a un codigo SIES unico: {cobertura:.1%}')

    left = personas_up.dropna(subset=['fecnac_ym', 'sexo'])
    right = personas_sies.dropna(subset=['fecnac_ym', 'sexo_mapeado'])

    right_index = {}
    codigos_by_mrun = {}
    for _, row in right.iterrows():
        k = (row['fecnac_ym'], row['sexo_mapeado'], row['anio_ing_min'])
        right_index.setdefault(k, []).append(row['_mrun'])
        codigos_by_mrun[row['_mrun']] = row['codigos_unicos']

    def resumen(etiqueta, matches, total):
        n0 = sum(1 for m in matches if m == 0)
        n1 = sum(1 for m in matches if m == 1)
        n2 = sum(1 for m in matches if m >= 2)
        print(f'[{etiqueta}] N={total} sin_match={n0} ({n0/total:.1%}) '
              f'match_unico={n1} ({n1/total:.1%}) ambiguo_2+={n2} ({n2/total:.1%})')
        return dict(total=total, sin_match=n0, match_unico=n1, ambiguo=n2)

    matches_base = [len(right_index.get((r['fecnac_ym'], r['sexo'], r['ano_ingreso_min']), []))
                    for _, r in left.iterrows()]
    res_base = resumen('fecnac+sexo+ano_ingreso', matches_base, len(left))

    con_carrera = left.dropna(subset=['codigo_unico_sies'])
    matches_carrera = []
    for _, row in con_carrera.iterrows():
        k = (row['fecnac_ym'], row['sexo'], row['ano_ingreso_min'])
        candidatos = right_index.get(k, [])
        c = sum(1 for m in candidatos if row['codigo_unico_sies'] in codigos_by_mrun.get(m, set()))
        matches_carrera.append(c)
    res_carrera = resumen('fecnac+sexo+ano_ingreso+carrera (subset resuelto)', matches_carrera, len(con_carrera))

    return 0


if __name__ == "__main__":
    sys.exit(main())

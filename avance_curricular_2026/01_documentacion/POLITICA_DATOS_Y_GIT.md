# Política de Datos y Git - Avance Curricular SIES 2026

Proceso: Avance Curricular SIES 2026

Fecha de emisión: 2026-06-26T00:58:26.544655-04:00 America/Santiago

## Visibilidad del repositorio

- Remote observado: `https://github.com/Alexitho0o/avance_curricular.git`
- Verificación: VERIFICADO_API_GITHUB
- Visibilidad reportada: public
- Privado: NO

## Conservación solo local

Se conservan solo localmente las copias originales y derivados ubicados bajo:

- `avance_curricular_2026/00_fuentes_congeladas/`
- `avance_curricular_2026/10_resultados/`
- `avance_curricular_2026/11_archivos_subida/`

Estas rutas pueden contener RUT, pasaporte, nombres, apellidos, sexo, fecha de nacimiento y datos académicos.

## Elementos versionables

Pueden versionarse, previa revisión:

- scripts reproducibles;
- documentación metodológica sin muestras reales de estudiantes;
- contratos de datos;
- matrices normativas;
- inventarios sin registros personales;
- hashes, conteos y reportes agregados.

## Elementos no aptos para Git ni push

No se deben incorporar al historial Git:

- originales descargados desde PES o fuentes institucionales con datos personales;
- TSV derivados con datos personales;
- Excel institucional `PROMEDIOSDEALUMNOS_7804.xlsx`;
- salidas de control o PES con registros reales.

## Reproducción sin exposición

Para reproducir la fase inicial, ejecutar el script desde el repositorio local con las fuentes originales disponibles en `/Users/alexi/Downloads`. El script genera manifiestos, perfiles sin muestras reales, hashes y contratos. Los archivos con datos personales quedan ignorados por `.gitignore`.

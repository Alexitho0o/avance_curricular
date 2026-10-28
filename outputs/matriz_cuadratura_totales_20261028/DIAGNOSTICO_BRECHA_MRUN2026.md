# Diagnóstico MRUN2026 frente a MU — brecha 226

C/E: diagnóstico por perfiles, no prueba de identidad. Nunca se guardan pares RUT–MRUN.

## Fuente y alcance [B/C]

H2 íntegro de 24.386 filas; subconjunto2026 de3.425 (3.371 pregrado+54 postítulo), con cero diferencias por código frente a publicación. Foco exclusivo:48 códigos,2.973 registros MRUN. Base de candidatos:4.105 matrículas MU (3.145 VIG1+960 VIG0). No se utiliza versión como bloqueo.

## Clasificación final [C/E]

| Clase | Registros MRUN |
|---|---:|
| vig1_candidata_unica | 1916 |
| vig0_candidata_unica | 10 |
| varios_candidatos | 807 |
| sin_candidato | 240 |

Entre los ambiguos: 619 sólo VIG1; 0 sólo VIG0; 188 mixtos.
Registros con alguna candidata VIG0: 198. Capacidad descriptiva por código para brecha positiva: 105/228; sin candidatura VIG0 suficiente: 123. Conteo descriptivo por registro MRUN y perfiles, sin restricción uno a uno; no es número de identidades confirmadas ni prueba de cuáles VIG0 aceptó SIES.
Unicidades cuyo candidato también es compatible con otros registros MRUN: 68. Unicidades con versión distinta: 5. No se convierten en enlaces certificados.

## Reglas reutilizadas y adaptación de esquema

Año+nacimiento AAAAMM+sexo (A); más familia ISCJ, V libre (B); tipo sólo con perfil gobernado unánime (C). birth se importa del script16-10 sin ejecutar su main. MRUN1=Hombre→MU H, MRUN2=Mujer→MU M; no se confunde con UMAS M/F. 190001 y sexos no comparables no generan candidatos. Sin nombre, aproximación ni método probabilístico.

La MU ya contiene familia; para tipo se reúnen los perfiles gobernados de todos los grupos compatibles con esa familia, sin elegir CODCLI por semejanza. Si faltan perfiles o difieren, C conserva B. Esta adaptación conservadora no acredita tipo personal.

## Comparación por código

| Código | MRUN | VIG1 nuestra | Brecha | Único VIG1 | Único VIG0 | Varios | Sin candidato | Alguna candidata VIG0 | Pendiente positivo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| I162S2C10J4V1 | 17 | 16 | 1 | 16 | 0 | 0 | 1 | 0 | 1 |
| I162S2C111J4V1 | 30 | 24 | 6 | 20 | 0 | 3 | 7 | 1 | 5 |
| I162S2C112J4V1 | 66 | 56 | 10 | 52 | 0 | 5 | 9 | 2 | 8 |
| I162S2C113J4V1 | 33 | 26 | 7 | 24 | 1 | 2 | 6 | 1 | 6 |
| I162S2C114J2V1 | 94 | 74 | 20 | 68 | 0 | 8 | 18 | 2 | 18 |
| I162S2C115J2V1 | 27 | 23 | 4 | 23 | 0 | 0 | 4 | 0 | 4 |
| I162S2C116J4V1 | 24 | 23 | 1 | 22 | 0 | 1 | 1 | 1 | 0 |
| I162S2C118J4V1 | 64 | 62 | 2 | 56 | 1 | 6 | 1 | 3 | 0 |
| I162S2C124J4V1 | 25 | 24 | 1 | 23 | 0 | 1 | 1 | 1 | 0 |
| I162S2C125J4V1 | 13 | 11 | 2 | 9 | 0 | 1 | 3 | 1 | 1 |
| I162S2C1J1V2 | 34 | 33 | 1 | 28 | 0 | 3 | 3 | 0 | 1 |
| I162S2C1J2V4 | 32 | 29 | 3 | 24 | 0 | 4 | 4 | 0 | 3 |
| I162S2C1J4V2 | 239 | 232 | 7 | 111 | 1 | 122 | 5 | 22 | 0 |
| I162S2C3J4V2 | 153 | 152 | 1 | 71 | 0 | 80 | 2 | 6 | 0 |
| I162S2C3J4V3 | 113 | 112 | 1 | 39 | 0 | 72 | 2 | 6 | 0 |
| I162S2C46J1V1 | 35 | 34 | 1 | 27 | 0 | 6 | 2 | 0 | 1 |
| I162S2C46J2V1 | 41 | 39 | 2 | 31 | 0 | 7 | 3 | 2 | 0 |
| I162S2C46J4V1 | 78 | 77 | 1 | 40 | 0 | 38 | 0 | 10 | 0 |
| I162S2C46J4V3 | 256 | 242 | 14 | 131 | 0 | 114 | 11 | 19 | 0 |
| I162S2C47J2V1 | 27 | 25 | 2 | 20 | 0 | 4 | 3 | 0 | 2 |
| I162S2C57J1V1 | 28 | 24 | 4 | 22 | 0 | 2 | 4 | 0 | 4 |
| I162S2C57J2V1 | 25 | 22 | 3 | 20 | 1 | 2 | 2 | 1 | 2 |
| I162S2C57J4V1 | 257 | 255 | 2 | 120 | 0 | 128 | 9 | 40 | 0 |
| I162S2C6J2V2 | 7 | 6 | 1 | 6 | 0 | 0 | 1 | 0 | 1 |
| I162S2C6J4V2 | 45 | 46 | -1 | 41 | 1 | 3 | 0 | 1 | 0 |
| I162S2C76J1V1 | 7 | 6 | 1 | 6 | 1 | 0 | 0 | 1 | 0 |
| I162S2C76J2V1 | 25 | 18 | 7 | 19 | 0 | 0 | 6 | 0 | 7 |
| I162S2C76J4V1 | 132 | 120 | 12 | 80 | 0 | 39 | 13 | 17 | 0 |
| I162S2C77J1V1 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| I162S2C77J4V1 | 98 | 91 | 7 | 71 | 1 | 16 | 10 | 7 | 0 |
| I162S2C78J2V1 | 36 | 34 | 2 | 31 | 0 | 4 | 1 | 2 | 0 |
| I162S2C78J4V1 | 88 | 82 | 6 | 62 | 1 | 19 | 6 | 8 | 0 |
| I162S2C79J2V1 | 25 | 26 | -1 | 20 | 0 | 3 | 2 | 1 | 0 |
| I162S2C79J4V1 | 87 | 86 | 1 | 72 | 0 | 13 | 2 | 5 | 0 |
| I162S2C83J4V1 | 94 | 84 | 10 | 68 | 0 | 14 | 12 | 7 | 3 |
| I162S2C84J4V1 | 34 | 30 | 4 | 30 | 0 | 0 | 4 | 0 | 4 |
| I162S2C85J4V1 | 56 | 52 | 4 | 43 | 1 | 9 | 3 | 6 | 0 |
| I162S2C86J4V1 | 62 | 60 | 2 | 51 | 0 | 9 | 2 | 1 | 1 |
| I162S2C87J4V1 | 5 | 0 | 5 | 1 | 0 | 0 | 4 | 0 | 5 |
| I162S2C87J4V2 | 77 | 69 | 8 | 57 | 0 | 11 | 9 | 2 | 6 |
| I162S2C88J4V1 | 52 | 47 | 5 | 41 | 0 | 5 | 6 | 1 | 4 |
| I162S2C89J4V1 | 37 | 30 | 7 | 25 | 1 | 4 | 7 | 1 | 6 |
| I162S2C90J2V2 | 22 | 19 | 3 | 19 | 0 | 0 | 3 | 0 | 3 |
| I162S2C91J1V1 | 87 | 69 | 18 | 44 | 0 | 27 | 16 | 13 | 5 |
| I162S2C91J2V1 | 112 | 92 | 20 | 73 | 0 | 19 | 20 | 6 | 14 |
| I162S3C114J2V1 | 36 | 33 | 3 | 29 | 0 | 3 | 4 | 1 | 2 |
| I162S3C115J2V1 | 19 | 18 | 1 | 16 | 0 | 0 | 3 | 0 | 1 |
| I162S3C91J2V1 | 18 | 14 | 4 | 14 | 0 | 0 | 4 | 0 | 4 |

## Dictamen

La presencia de candidatos VIG0 permite evaluar compatibilidad con la hipótesis, no identificar cuáles registros SIES corresponden a nuestras nóminas. Las ambigüedades, candidatos compartidos y sin candidato permanecen E. Brecha neta226 y tasas originales intactas. El diagnóstico MRUN no reemplaza una descarga PES identificada por documento.

Resultados A y B intermedios, aplicación de tipo y hashes: JSON adjunto.

# Prueba inversa de la brecha MU2026 [C/E]

Se reutilizan los bloqueos A/B/C del 16-10. No se certifican identidades ni se guardan vínculos RUT–MRUN.

## Resultados

| Universo | Con candidato C | Sin candidato C |
|---|---:|---:|
| 2.747 VIG1 contra todo_IPSS | 2703 | 44 |
| 2.747 VIG1 contra solo_48_codigos | 2703 | 44 |

De los 240 MRUN sin candidato C: 224 encuentran perfil A en nuestra MU y 16 no. Con perfil A: 224 sólo otra familia, 0 misma y otra, 0 sólo la misma. VIG de candidatos: 77 sólo VIG1; 3 sólo VIG0; 144 mixtos.

Compatibilidad demográfica no demuestra reclasificación ni ausencia de matrícula. Los perfiles sin candidato pueden reflejar cobertura, datos no comparables o discrepancias de atributos. No se fuerza identidad ni versión.

Los soportes origen/destino del JSON no son sumables entre destinos: un registro puede tener varios perfiles candidatos.

## Inversa por código

| Código | VIG1 nuestra | Sin candidato C en todo IPSS | Sin candidato C en foco |
|---|---:|---:|---:|
| I162S2C10J4V1 | 16 | 0 | 0 |
| I162S2C111J4V1 | 24 | 1 | 1 |
| I162S2C112J4V1 | 56 | 0 | 0 |
| I162S2C113J4V1 | 26 | 0 | 0 |
| I162S2C114J2V1 | 74 | 1 | 1 |
| I162S2C115J2V1 | 23 | 0 | 0 |
| I162S2C116J4V1 | 23 | 0 | 0 |
| I162S2C118J4V1 | 62 | 0 | 0 |
| I162S2C124J4V1 | 24 | 0 | 0 |
| I162S2C125J4V1 | 11 | 1 | 1 |
| I162S2C1J1V2 | 33 | 2 | 2 |
| I162S2C1J2V4 | 29 | 1 | 1 |
| I162S2C1J4V2 | 232 | 2 | 2 |
| I162S2C3J4V2 | 152 | 3 | 3 |
| I162S2C3J4V3 | 112 | 0 | 0 |
| I162S2C46J1V1 | 34 | 1 | 1 |
| I162S2C46J2V1 | 39 | 1 | 1 |
| I162S2C46J4V1 | 77 | 0 | 0 |
| I162S2C46J4V3 | 242 | 1 | 1 |
| I162S2C47J2V1 | 25 | 1 | 1 |
| I162S2C57J1V1 | 24 | 0 | 0 |
| I162S2C57J2V1 | 22 | 0 | 0 |
| I162S2C57J4V1 | 255 | 1 | 1 |
| I162S2C6J2V2 | 6 | 0 | 0 |
| I162S2C6J4V2 | 46 | 3 | 3 |
| I162S2C76J1V1 | 6 | 0 | 0 |
| I162S2C76J2V1 | 18 | 0 | 0 |
| I162S2C76J4V1 | 120 | 3 | 3 |
| I162S2C77J1V1 | 0 | 0 | 0 |
| I162S2C77J4V1 | 91 | 4 | 4 |
| I162S2C78J2V1 | 34 | 0 | 0 |
| I162S2C78J4V1 | 82 | 2 | 2 |
| I162S2C79J2V1 | 26 | 3 | 3 |
| I162S2C79J4V1 | 86 | 1 | 1 |
| I162S2C83J4V1 | 84 | 1 | 1 |
| I162S2C84J4V1 | 30 | 0 | 0 |
| I162S2C85J4V1 | 52 | 0 | 0 |
| I162S2C86J4V1 | 60 | 1 | 1 |
| I162S2C87J4V1 | 0 | 0 | 0 |
| I162S2C87J4V2 | 69 | 2 | 2 |
| I162S2C88J4V1 | 47 | 2 | 2 |
| I162S2C89J4V1 | 30 | 1 | 1 |
| I162S2C90J2V2 | 19 | 0 | 0 |
| I162S2C91J1V1 | 69 | 0 | 0 |
| I162S2C91J2V1 | 92 | 2 | 2 |
| I162S3C114J2V1 | 33 | 1 | 1 |
| I162S3C115J2V1 | 18 | 2 | 2 |
| I162S3C91J2V1 | 14 | 0 | 0 |

QA: SQL independiente, cero diferencias. Desglose completo de los 240 y sus soportes por código/VIG en el JSON. Bases, tasas y denominadores intactos.

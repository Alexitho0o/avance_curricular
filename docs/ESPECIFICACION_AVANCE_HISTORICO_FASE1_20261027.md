# Avance histórico IPSS · Fase 1: recuperación y reproducción

## Alcance autorizado [D]

Solicitud de Alexi en este chat, 27-10-2026: ejecutar solo la fase 1 antes de crear
un Excel. Reutilizar Avance Curricular; mantener tres análisis complementarios:
avance SIES anual, seguimiento T1/T2/T3 y aprobaciones frente a la malla.
No modificar fuentes, bases, denominadores, motores, diccionario ni archivos
previos; sin commit ni push. Esta especificación no cambia reglas funcionales.

## Contexto y precedencia

- Institución 162, proceso Avance Curricular SIES 2026, datos académicos 2025.
- La ampliación histórica es interna [C/D]; no acredita envíos de otros años.
- Repositorio contenedor `avance_curricular`, rama `feature/ire-2026`.
- Consultar `agent.md`, `PROYECTO_IPSS.json`, instructivo del proceso y manifiestos.
- El agente MU2026 tiene alcance Matrícula Unificada: sus comandos productivos
  no son un procedimiento de recálculo de Avance Curricular. Se reutiliza su
  política de validación no destructiva; no se ejecutan cargas ni motores MU.
- A: instructivo; B: fuentes y resultados observados; C: implementación;
  D: decisiones internas; E: evidencia o reproducción pendiente.

## Hitos y aceptación

1. Localizar la cadena más avanzada respaldada, sus fuentes y hashes. Distinguir
   cierre técnico, prueba PES, carga completa y aceptación final. Los nombres de
   archivo no prueban aceptación. Git histórico sirve como evidencia, no como
   autorización para restaurar o activar motores antiguos.
2. Reproducir los controles y transformaciones ejecutables con fuentes legibles,
   sin escribir datos individuales. Comparar filas, llaves, unidades y tasas de
   alcance idéntico; registrar diferencias, sin compensarlas.
3. Crear informe, resultados agregados y manifiesto con fuentes, Git, script,
   huellas, reglas, controles, límites y punto de reanudación. No declarar
   reproducción desde RAW cuando solo se reprodujo una transformación posterior.

## Salidas

`outputs/avance_historico_fase1_20261027/`: script de auditoría, configuración,
resultados agregados, informe, evidencia documental sin identificadores y
manifiesto. Este directorio se justifica por la convención existente de salidas
versionadas del proyecto. No generar Excel ni copiar fuentes personales a Git.

## Control de preservación

Comprobar hashes de las fuentes antes/después, HEAD y cambios ajenos. La lectura
del histórico no implica sincronización actual con GitHub. Solo salidas agregadas
y código sin identificadores son candidatos a versionado posterior.

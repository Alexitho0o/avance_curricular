# F02: cierre interno y revisión IINF20241

**D/C:** se aplicó el cierre autorizado de IECIREOL20211, 2024/2 bimestral,
como I162S2C1J4V2 en una adjudicación separada. No se altera la base original
ni se declara envío SIES acreditado. Responsable: Alexi; ejecución: Codex.

| Observación | Código interno tras revisión | Estado | Clase |
|---|---|---|---|
| IECIREOL20211, 2024/2 bimestral | I162S2C1J4V2 | Cerrada internamente por autorización | B/C/D |
| IINF20241, 2024/T1 | Pendiente; candidato V2 | Falta atribución al expediente/período | B/C/E |
| IINF20241, 2024/T2 | Pendiente; candidato V2 | Falta atribución al expediente/período | B/C/E |
| IINF20241, 2024/T3 | Pendiente; candidato V2 | Plan confirmado por respaldo T3; versión pendiente | B/C/E |

## Qué aportan los cruces gobernados

**B/C:** IINF20241, carrera IINF, jornada 4, año 2024 reúne 403 observaciones
de 171 personas en el diagnóstico. Hay 330 observaciones atribuidas a V2
(132 personas), tres a V3 (una persona) y 70 pendientes. No se infiere una
equivalencia universal por mayoría. Se releyó la referencia MU del caso V3
y la de F02, corroborando identidad, año y código. El contraejemplo no prueba
que F02 sea V3: demuestra que el plan y jornada solos no distinguen versión.

**B:** la oferta 2024 contiene V2 regular de ocho semestres y V3 continuidad
de cuatro, esta última sin admisión nueva declarada. El catálogo de grupo
operativo 2026 propone V2 para IINF/RE/O; su maestro deja la equivalencia
del plan sin vigencia acreditada y no habilitada para resolver. No hay fila
IINF en las equivalencias manuales FCU2026 consultadas. No se retrotrae esa
relación operativa a 2024.

**B/C:** para F02, la fecha MU2024 coincide exclusivamente con el expediente
IECIREOL (22-abril), mientras IINF declara 24-abril. Los respaldos acreditan
IINF20241 por período, pero no añaden una versión SIES vinculada al nuevo
expediente. V2 se conserva como candidato para las tres observaciones; no se
confunde la corroboración anual de la persona con un enlace a ambos expedientes.

**E:** no se resolvió completamente F02. No se exige el día administrativo
como condición universal; falta la atribución de versión al nuevo expediente
en los tres períodos de 2024. El día del cambio queda como pendiente separado.

## Efecto y conservación

**C:** pendientes internos: 3.094 → 3.093 observaciones. Personas con algún
pendiente: 1.751 → 1.751, porque F02 conserva tres. Pendientes documentales:
3.213 observaciones y 1.838 personas, sin cambios. F02: cuatro → tres
observaciones pendientes; cinco observaciones de 2023 ya estaban resueltas.

**D:** denominadores, bases, libros, fuentes y motor anual conservados. El
universo aprobado permanece 5.901 personas / 6.622 expedientes / 24.774
observaciones; no se cambia el grano de expediente. No se recalculan tasas.

**C:** QA OK_CON_ADVERTENCIAS: una sola modificación interna autorizada al
aplicar la adjudicación en memoria, ninguna documental, fuentes intactas,
identificadores en detalle privado fuera de Git. DECISION.json conserva
responsable, fecha/hora, alcance y reversión. MANIFEST.json incluye rutas y
hashes. Esta entrega local no está publicada: sin commit/push.

Reanudación: cargar OBSERVACIONES_PRIVADAS.json con el hash de entrada y
superponer únicamente ADJUDICACION_INTERNA.json por observacion_id, comprobando
estado_antes. El script reproduce los resultados y conserva los diagnósticos
anteriores. No trasladar la decisión a otros expedientes ni a un motor productivo.

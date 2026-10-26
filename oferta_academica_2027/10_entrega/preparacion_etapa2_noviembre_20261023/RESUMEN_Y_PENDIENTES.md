# Preparacion Etapa 2 de noviembre: diplomados 2027

Proceso 2026, referencia 2027. Analisis al 23-10-2026. NO ES ARCHIVO DE CARGA.

## Resultado
29 programas de Docencia, 7 representados en Etapa 1 V06 y 22 candidatos nuevos o faltantes.
Los 7 se excluyen de la propuesta: codigos 53, 66, 68, 69, 70, 96 y 99.
Se conservan las equivalencias ya decididas para 68 y 99, aunque los nombres difieren.
Los 14 codigos con vigencia 3 permanecen sin cambios. No se convierten automaticamente
en 14 altas nuevas ni se reutilizan sus codigos. El universo se construye desde Docencia.
22 es cantidad de programas fuente, no numero definitivo de filas PES: sede, modalidad,
jornada y versiones todavia no estan informadas y pueden cambiar el detalle de registros.

## Pendientes academicos por cada candidato
17 campos sin dato directo: sede y nombre, modalidad, jornada, version, tipo de plan,
duracion de estudios/titulacion/total, regimen y duracion del regimen, certificacion final,
ano real de inicio, acreditacion del programa, requisito de ingreso, semestres reconocidos
y area actual. Son 374 ausencias de datos, no 374 rechazos observados en PES.
Caracteristicas del plan depende del tipo: NO APLICA para 1/3; describir si 2.
Confirmar duracion desde un semestre para clasificar como diplomado (global 3, nivel 5).
Confirmar nombres observados: filas 13, 20, 27, 29 y 31. No se corrigieron fuentes.
Gestion Estrategica y Gobernanza de Datos (fila 8) no se fusiona con Gobernanza de Datos (96).

## Datos disponibles y decisiones previas
El Excel contiene una sola cifra de 15 vacantes por programa, no un reparto semestral.
La instruccion anterior 15+15 produjo 30 vacantes anuales por diploma V06. Ratificar alcance
a los 22 candidatos; no inferir semestres desde periodos 2027-00/01/02/03.
La fuente conserva importes en Matricula y Arancel=0. Usuario confirmo para V06 que esos
importes son ARANCEL y la matricula queda en 0. Ratificar alcance a nuevos, sin modificar fuente.
Titulacion y certificado son 0 informados, no faltantes. Moneda CLP debe conservar trazabilidad.
No se genera total de vacantes de carga ni importes finales mientras estos alcances esten pendientes.

## Reglas que evitan pedir informacion innecesaria
COD_CARRERA vacio, sin codigo institucional ni encabezados en el futuro CSV (p.31).
VERSION obligatoria del 1 al 9 (p.36): no confundir con el codigo de carrera.
Diez areas de destino en 0 para postitulos (pp.9-10).
AI:AP vacios para postitulos (pp.40-41), incluso ENLACE_INFO_PROGRAMA: los enlaces
ausentes en Docencia no bloquean esta carga. Los existentes se conservan como referencia.
No trasladar las exigencias de pregrado ni las reglas de la Etapa 2 de agosto.

## Preparacion y cierre
Ventana: 02 a 13 de noviembre de 2026 (p.29). Carga ID 17469 (p.30).
48 columnas A:AV verificadas contra Anexo 2, pp.35-41. Falta incorporar estructura vigente
descargada de PES para verificar serializacion final; p.30 dice CSV delimitado por comas.
No asumir automaticamente el delimitador de Etapa 1 ni usar estructura de agosto.
Falta reporte 6048 para conciliacion contra oferta efectivamente validada en PES;
la base actual es V06 aceptada segun confirmacion del usuario, no consulta directa a PES.
No se localizaron archivos con 6048 o 17469 en los nombres del subproyecto ni Descargas
(busqueda dirigida; no prueba de inexistencia bajo otros nombres).
Al completar datos, validar combinaciones modalidad/jornada (p.56), niveles y duraciones
(p.57), nombres y estructura. Confirmar Finalizado y luego conciliar reporte 6049 (p.33).
No se generaron CSV, no se cambio vigencia ni se reabrieron archivos congelados para escritura.

## Reanudacion
Recibir antecedentes academicos de los 22 candidatos, resolver denominaciones y confirmar
alcance de criterios de vacantes e importes; incorporar 6048 y estructura 17469; repetir
conciliacion y validacion antes de generar la carga. No copiar valores de programas parecidos.

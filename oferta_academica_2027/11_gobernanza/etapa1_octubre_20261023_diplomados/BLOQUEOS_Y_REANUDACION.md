# Revision de entrega de diplomados: carga pendiente

23-10-2026. Oferta Academica 2027, segundo proceso, Etapa 1, ID 17467.
Base: V04, 161 registros, 48 campos, fechas corregidas y sin salto final.
Entrega: Oferta Diplomados 2027 - SIES vf.xlsx, Hoja2, encabezado fila 4.

El Excel contiene 29 programas, 15 vacantes por programa y no contiene codigos
SIES, sede, modalidad, jornada, version ni vigencia. El rechazo PES afecta a
21 diplomados. Hay 3 coincidencias de nombre tras comparar sin tildes/caja,
2 candidatos por la presencia/ausencia de EN y 16 sin correspondencia por
estos criterios. Estas comparaciones no renombraron datos ni autorizaron joins.
Los 24 programas restantes del Excel no se declaran nuevos automaticamente.

Bloqueos para generar carga:
1. Confirmar si la nueva entrega sustituye o complementa la oferta y aportar
   identidad SIES o correspondencia autorizada. La ausencia en Excel no prueba
   que un programa deba cambiar de vigencia; se requieren estados confirmados.
2. Definir vacantes por semestre. Periodos 2027-00 (12), 2027-01 (8),
   2027-02 (7), 2027-03 (2); no existe equivalencia semestral en el libro.

Importes observados: matricula 400000 (10 programas), 600000 (2), 990000 (17).
Titulacion, certificado y arancel son cero en los 29 registros. No intercambiar
matricula con arancel. Total institucional informado: 435 cupos; no sumarlos
a los 5.461 de la base sin resolver identidad y cobertura de etapas.

El archivo de error del 20-10-2026 18:06:40 no se encuentra actualmente en
Descargas, Escritorio ni el subproyecto. Sus mensajes se conocen por la lectura
registrada en esta conversacion; no se reconstruye ni presenta como original.

El rechazo PES establece 0 en tres cobros si no corresponden, y rechaza
vigencia 1 con ambas vacantes cero. No se inventan vacantes ni estados para
sortear la validacion. No se genero nuevo CSV de carga ni se modifico V04.

Reanudacion: recibir correspondencias/vigencias y distribucion semestral,
aplicar unicamente datos autorizados a la base, generar diff por celda,
validar estructura y reglas, conservar UTF-8, punto y coma y ausencia de
salto final; guardar copia en Escritorio. Aceptacion final pendiente de PES.
Respaldo local reproducible. No commit, push ni carga a PES.

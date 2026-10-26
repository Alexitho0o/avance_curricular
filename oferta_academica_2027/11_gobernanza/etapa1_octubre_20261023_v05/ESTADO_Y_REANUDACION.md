# Version V05 para carga PES, pendiente de aceptacion

23-10-2026. Oferta Academica 2027, proceso 2026, Etapa 1 octubre, ID 17467.
Base V04, no el Excel de edicion manual que fue entregado en blanco.
Vigencia 3 autorizada: 40,63,64,65,67,71,95,97,98,101,102,103,104,105.
La decision final sobre 40 sustituye su correspondencia previamente propuesta.
Vigencia 1 conservada: 53,66,68,69,70,96,99. No se cambian nombres ni claves.
Cinco cruces nominales y dos por confirmacion conversacional (68 y 99).
Para 99 se usa la fila 9 de Docencia: IA Aplicada para Gestion Publica y Local,
matricula $400.000. Los otros seis vigentes tienen matricula $990.000.
Titulacion, certificado y arancel: 0, tal como los entrega Docencia.
No se intercambia matricula con arancel y no se incorporan enlaces de diplomados.

Vacantes: 15 primer semestre y 15 segundo por instruccion explicita del usuario;
son 30 anuales por programa, aunque el Excel fuente informa un solo total de 15.
No se dedujo equivalencia entre periodos Excel y semestres SIES.
Los 14 no vigentes conservan 0 vacantes y los campos financieros vacios de SIES.
No se imputa 0 o -1 a esos importes. Los campos DFE vacios no prueban ausencia
de proteccion; PES confirmara la posibilidad de baja.

Validado: 161x48, orden manual pp.21-28, claves unicas, fechas DD/MM/AAAA,
pregrado integro, combinaciones modalidad/jornada y niveles, duraciones,
vacantes positivas y financieros completos para vigencia 1; sin linea final.
CSV UTF-8 sin BOM, punto y coma, sin encabezados, ninguna fila agregada/borrada.
Las condiciones observadas en los errores previos ya no aparecen para vigencia 1.
Esto no garantiza ausencia de otras validaciones de PES ni su aceptacion final.

Usar V05 para cargar; no esta aceptada ni congelada. Conservar el resultado de
PES y conciliar contra reporte 6048 antes de cerrar. No se envio a PES.
Respaldo local reproducible, sin commit ni push. Originales y V04 intactos.

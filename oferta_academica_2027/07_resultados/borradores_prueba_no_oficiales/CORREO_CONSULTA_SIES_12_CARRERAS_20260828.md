Para: consultas.sies@mineduc.cl
Asunto: Consulta – Rechazo "ya existe en la Oferta Vigente Validada" al cargar nuevas versiones de programas en Etapa 2 (Oferta Académica Nueva TP Adscritas) – Proceso Oferta Académica 2027

Estimados/as,

Junto con saludar, escribimos para consultar sobre un problema que hemos encontrado al intentar cargar la Oferta Académica Nueva TP Adscritas (Etapa 2, carga ID 17451) del Proceso Oferta Académica 2027.

Al intentar cargar 12 registros correspondientes a nuevas versiones de 5 carreras ya existentes en nuestra Oferta Vigente Validada, el sistema rechaza los 12 con el mensaje:

"La Carrera o Programa que está ingresando como nueva, ya existe en la Oferta Vigente Validada."

Entendemos que este mensaje corresponde a la validación descrita en el Anexo 4 del instructivo (pág. 63). Revisamos también el Anexo 5 ("Sobre modificación de código unificado"), que describe que un cambio de modalidad, duración, tipo de carrera o nivel de programa modifica la VERSION y, por lo tanto, el Código Unificado, y que el procedimiento correcto es "operar en la plataforma colocando el programa original como vigencia 2 y el nuevo como vigencia 1", sin requerir oficio.

Antes de escribir, hicimos las siguientes verificaciones para acotar el problema:

Probamos incrementar en 1 el VERSION de los 12 registros (dejando todo lo demás igual) y el error persistió idéntico en los 12 casos. Esto nos indica que la validación de "ya existe" no considera el campo VERSION.

Revisamos, para cada uno de los 12 registros, cuál es el registro exacto de nuestra Oferta Vigente Validada (reporte 5912) que coincide en sede + carrera + modalidad + jornada + tipo de plan + nivel + título (es decir, todo excepto VERSION). En 5 de los 12 casos, el registro coincidente en el 5912 tiene VIGENCIA_CARRERA=1 (vigente, con estudiantes nuevos). En los otros 7 casos, el registro coincidente YA tiene VIGENCIA_CARRERA=2 (vigente sin estudiantes nuevos, es decir, ya cerrado). El sistema rechaza igual los 12, sin distinguir si la versión coincidente está abierta o cerrada.

Todos los programas involucrados ya cuentan con COD_CARRERA asignado en la Oferta Vigente Validada (no son carreras nuevas desde cero).

Para descartar dudas adicionales, aislamos los 4 registros que sí cumplen íntegramente las condiciones del Anexo 5 para declarar una versión nueva (cambio real de régimen/duración de régimen/año de inicio, y versión anterior ya en vigencia=2) y los volvimos a cargar solos. Fueron rechazados igual, con el mismo mensaje. Esto nos indica que el rechazo no depende de VERSION, ni de VIGENCIA_CARRERA de ningún registro existente, ni de si hay o no un cambio estructural real: rechaza cualquier combinación sede+carrera+modalidad+jornada+tipo_plan+nivel+título que haya existido alguna vez para nuestra institución, independientemente de su estado actual.

DETALLE DE LOS 12 REGISTROS

Todos en Sede Casa Central (Santiago), Código IES 162:

| Carrera | Mod. | Jor. | Tipo Plan | COD_CARRERA (5912) | VERSION que intentamos ingresar (Etapa 2) | Registro coincidente en Oferta Vigente Validada (5912) |
|---|---|---|---|---|---|---|
| Ingeniería en Administración de Empresas | 3 | 4 | 3 | 76 | VERSION 3 | VERSION 2, vigencia=2 |
| Ingeniería en Administración de Empresas | 3 | 4 | 1 | 76 | VERSION 2 | VERSION 1, vigencia=1 |
| Ingeniería en Administración de Empresas | 1 | 2 | 1 | 76 | VERSION 2 | VERSION 1, vigencia=2 |
| Ingeniería en Logística | 3 | 4 | 3 | 77 | VERSION 3 | VERSION 2, vigencia=2 |
| Ingeniería en Logística | 3 | 4 | 1 | 77 | VERSION 1 | VERSION 1, vigencia=1 |
| Ingeniería en Ciberseguridad | 3 | 4 | 3 | 46 | VERSION 4 | VERSION 1, vigencia=2 |
| Ingeniería en Ciberseguridad | 3 | 4 | 1 | 46 | VERSION 2 | VERSION 3, vigencia=1 |
| Ingeniería en Ciberseguridad | 1 | 2 | 1 | 46 | VERSION 2 | VERSION 1, vigencia=2 |
| Ingeniería en Informática | 3 | 4 | 3 | 1 | VERSION 4 | VERSION 3, vigencia=2 |
| Ingeniería en Informática | 3 | 4 | 1 | 1 | VERSION 3 | VERSION 2, vigencia=1 |
| Ingeniería en Conectividad y Redes | 3 | 4 | 3 | 3 | VERSION 4 | VERSION 3, vigencia=2 |
| Ingeniería en Conectividad y Redes | 3 | 4 | 1 | 3 | VERSION 3 | VERSION 2, vigencia=1 |

Modalidad 1 = Presencial, 3 = No Presencial. Jornada 2 = Vespertina, 4 = A Distancia. Tipo Plan 1 = Regular (8 semestres en nuestro caso), 3 = Regular de Continuidad (4 semestres en nuestro caso).

Se adjuntan dos archivos CSV con estos 12 registros tal como se intentan cargar (una versión con fila de encabezado, para facilitar la lectura, y otra sin encabezado, en el formato exacto que exige la carga de Etapa 2: 48 columnas, delimitador punto y coma).

CONSULTAS

1) Para los 7 casos en que el registro coincidente en el 5912 YA está en vigencia=2 (cerrado) — es decir, no hay ningún conflicto de vigencia activa — ¿por qué el sistema igual rechaza el ingreso como "ya existe"? ¿Existe una vía distinta (por ejemplo, a través de la opción Historial, o mediante la Etapa 3) para declarar una versión nueva de un programa cuya versión anterior ya está cerrada?

2) ¿Es necesario un oficio formal para resolver estos 12 casos, o basta con esta consulta, considerando que el Anexo 5 indica que no se requiere oficio para cambios de modalidad, duración, tipo de carrera o nivel de programa?

Quedamos atentos a sus indicaciones para proceder correctamente. Agradecemos de antemano su orientación.

Saludos cordiales,

[Nombre]
[Cargo]
[Institución – Código IES 162]
[Teléfono / correo de contacto]

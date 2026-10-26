# Entorno y dependencias

El complemento contiene instrucciones y recursos; no instala servicios, Python, Power BI ni motores de Office. Comprueba las capacidades de la sesión. Leer esta referencia no activa otras habilidades.

- Resuelve recursos respecto de la carpeta real del SKILL.md o script, nunca desde el directorio corriente. Si es un enlace simbólico local, resuelve su destino primero. Los enlaces a habilidades hermanas corresponden al mismo complemento.
- Usa adjuntos y carpetas disponibles para el encargo. Una ruta del Mac o enlace a un servicio no implica acceso desde ChatGPT web. Solicita solo el recurso indispensable para la operación dependiente.
- Guarda resultados en el directorio de salida de la sesión. Entrega bitácoras/scripts para retomar si no hay carpeta persistente. «Commit» de archivos no equivale a commit/push Git.
- Los nombres históricos `xlsx`, `pptx`, `docx`, `pdf-reading`, `file-reading`, `Read`, `Write`, `AskUserQuestion`, `present_files` o puentes de dispositivo son capacidades, no APIs instaladas por este paquete. Resuélvelos mediante las herramientas/skills que realmente exponga la sesión.
- Scripts: Python 3.10+ y openpyxl para lectura y el conversor CSV; pandas/scipy para contraste de encuestas; python-docx/python-pptx/pdfplumber o equivalentes según formato. No modificar runtimes de terceros.
- Para autoría Office aplica el flujo documentado del host. Las recetas openpyxl son alternativas, no permiso para saltarse una herramienta requerida. En documentos con objetos sensibles conserva OOXML y verifica gráficos, imágenes, validaciones, relaciones y estilos.
- Fórmulas escritas o valores guardados no demuestran recálculo. Ejecuta un motor compatible disponible (capacidad nativa, Excel o LibreOffice), registra cuál, revisa errores y contrasta cálculos independientes. Un motor alternativo sustituye LibreOffice solo si conserva objetos/fórmulas y pasa los mismos controles. Sin recálculo/render, la entrega debe declarar validación pendiente.
- Los gates y verificadores incluidos cubren controles específicos, no certifican documentos completos. Los gates léxicos requieren además lectura semántica de sujeto, relación, negación, alcance y causalidad.

| Dependencia | Se necesita para | Alternativa |
|---|---|---|
| SIES/Mineduc, mifuturo.cl | Cotejar cifras IPSS | Archivo oficial adjunto con origen/fecha; declarar cotejo web pendiente si no puede hacerse |
| LimeSurvey IPSS | Inspección/configuración viva | Exportaciones/capturas; no hay conexión automática ni envío de correos |
| Buk | Organigrama de personal | Exportación/capturas, sin exigir acceso vivo |
| Repositorio PNM y sus auditores/glosarios/theme | Edición PBIR/TMDL | Copia autorizada o archivos relevantes; no inventar bindings si faltan |
| Power BI Desktop/Service | Render, DAX en contexto e interacción | Parche y pruebas estructurales con prueba de aplicación pendiente |
| Plantilla IPSS | PPT ejecutivo IPSS | Copia empaquetada en la habilidad IPSS; una plantilla explícita del usuario tiene prioridad |

No empaquetar credenciales, bases personales ni el repositorio institucional. La asesoría sobre campañas no autoriza enviar mensajes. No declarar una conexión, instalación o prueba de aplicación que no se haya ejecutado.

## Diccionario personal de seguimiento IPSS

Consultar [el servicio común UMAS–SIES](diccionario-sies-seguimiento.md). Las skills comparten el puntero del proyecto; no mantienen otra tabla de equivalencias. El complemento no obtiene acceso automático a la base privada ni sustituye el QA de una edición.

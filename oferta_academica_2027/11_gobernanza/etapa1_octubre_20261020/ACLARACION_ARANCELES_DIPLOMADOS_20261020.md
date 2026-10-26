# Aclaracion de la revision de aranceles de diplomados

Fecha: 20-10-2026. Oferta Academica 2027, segundo proceso, Etapa 1.
Esta nota corrige la interpretacion del bloqueo financiero consignada en
ESTADO_Y_REANUDACION.md y MANIFIESTO_PREPARACION.json. No modifica el CSV.

## Evidencia revisada

Fuente: Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf, octubre 2026,
conservado en 00_fuentes_originales/etapa1_octubre_20261020/.

- Pagina 4: Etapa 1 valida vigencia; Etapa 3 define aranceles.
- Pagina 42, primer parrafo del Anexo 3: el objetivo de Etapa 3 es informar
  arancel anual, matricula anual, costo de titulacion y certificado o diploma.
  Periodo: 23-11-2026 al 04-12-2026.
- Pagina 44: la columna Postitulo o Diplomado enumera ACREDITACION,
  FORMATO_VALOR, VALOR_MATRICULA_ANUAL, COSTO_TITULACION,
  VALOR_CERTIFICADO_DIPLOMA y ARANCEL_ANUAL como campos a llenar en Etapa 3.
- Pagina 45: los datos solicitados en esa etapa no pueden ir vacios.
- Paginas 27-28: la estructura de Etapa 1 tambien califica los cuatro campos
  financieros como Obligatorio / Modificable para el grupo de postitulos.

## Correccion de la conclusion anterior

La definicion de los valores de diplomados corresponde expresamente a Etapa 3.
Fue demasiado categórico tratar los 84 vacios de la precarga oficial como un
rechazo seguro de PES o exigir completarlos ahora sin considerar el Anexo 3.
Se reclasifican como discrepancia documental pendiente de confirmar en PES/SIES,
no como error de Docencia ni rechazo observado. La etiqueta Obligatorio de
Etapa 1 no permite afirmar, a la inversa, que existe una exencion expresa.

Docencia confirmo sin cambios mediante el usuario. Se preservan los valores
originales de los 21 diplomados: no se imputan 0, -1 ni montos historicos.
El CSV sigue siendo una proyeccion exacta de la precarga, no una carga aceptada.
No se ha ejecutado una prueba de carga ni se conoce una respuesta de PES.

## Pendientes separados

Las 88 fechas con guiones requieren ajuste tecnico de formato conforme a la
pagina 26; no constituyen una decision academica nueva. Sigue pendiente comprobar
separador y estructura vigente de ID 17467. Esta nota no libera la carga ni
afirma que dichos controles ya se hayan completado.

# Manifiesto de gobernanza - FCU_ACTUALIZACION_MANUAL_2027

## Proceso

FCU_ACTUALIZACION_MANUAL_2027

## Alcance

Comparación del Manual de Aplicación FCU 2027 contra el Manual FCU 2026 previamente gobernado; dictamen de ajustes requeridos de formulario y mapeo PES, y libro de control trazable de cada cambio declarado.

## Declaración explícita

El Manual FCU 2027 declara 17 cambios respecto del Manual FCU 2026. La estructura del CSV PES pasa de 195 campos declarados en 2026 a 172 campos declarados en 2027; las posiciones del CSV 2026 no son reutilizables para la carga 2027.

## Evidencias copiadas

| archivo |
| --- |
| Manual_de_Aplicacion_FCU_2027.txt |
| Control_trazable_actualizacion_FCU_2027.xlsx |
| Matriz_codigos_LimeSurvey_acciones_FCU_2027.xlsx (derivado operativo; códigos candidatos por conciliar) |

## Evidencias faltantes

Sin faltantes críticos declarados en el dictamen vigente.

## Hash principal

9b88255dc3467bf684fd8d248b91c919dd4e156a99856d6fede48b3dba74e350

## Dictamen

ACTUALIZACION_FCU_2027_REQUIERE_AJUSTE_DE_FORMULARIO_Y_MAPEO_PES

## Riesgos

Medio: no implementar la carga PES 2027 sin verificar previamente cada campo contra el Manual 2027 y el libro de control, dado el cambio de 195 a 172 campos declarados.

## Reglas de uso

- No modificar originales.
- Usar evidencias copiadas solo como respaldo documental.
- Verificar hashes antes de usar como evidencia formal.
- No reutilizar el archivo CSV ni el orden posicional de campos de 2026 para la carga 2027.

## Próxima acción

Implementar y verificar la carga PES 2027 contra el Manual 2027 y el libro de control antes de ejecutar una carga PES.

## Versionamiento Git/nube

Git: versionar `docs/`, `tablas/`, `json/`, `hashes/` y `validaciones/`. Nube: respaldar evidencias pesadas/sensibles y auditorías Excel si la política documental lo exige.

La matriz operativa adicional está en `evidencias/Matriz_codigos_LimeSurvey_acciones_FCU_2027.xlsx`, SHA-256 `87613b9e545bf78c3e49c08bb50635063ba6b4c8fc61d3062b4cd7ee282f1ed1`. Es un derivado estructural sin respuestas individuales; debe validarse frente a una exportación vigente de LimeSurvey antes de editar preguntas.

FASE 7 TERMINADA: SÍ.

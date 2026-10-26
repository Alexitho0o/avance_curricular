# Seguimiento por CODCLI de las 14 carreras discordantes T2-2026

Solicitud: explicar las diferencias frente a las 66 renuncias del resumen original
sin cambiar bases, denominadores ni el libro V16. Proceso: retención intertrimestral
interna IPSS162. Universo fijo: las 528 matrículas / 527 personas del listado T2-2026.

## Método C

1. Verificar hashes contra la revisión del 23-oct-2026 y reproducir sus 14 carreras.
2. Buscar CODCLI exacto en los respaldos 10246, 11998 y 12159. Controlar unicidad,
   RUT, CODCARPR, año y período. Comparar estado y situación de la misma matrícula.
3. Separar persistencias, diferencias entre respaldos y CODCLI no localizados.
   Revisar estos últimos por RUT exacto sin trasladarles el estado de otro CODCLI.
4. Conciliar por carrera: renuncias originales, estado/situación en cada respaldo,
   transiciones y diferencia residual. Conservar vacíos originales; el cero usado
   en sumas reproduce la fórmula del resumen, no declara una regla académica.
5. Distinguir B observado, C implementación/cálculo y E atribución no acreditada.
   La igualdad de totales o de cantidades en una situación no prueba pertenencia a
   la nómina original. No deducir día de cambio de las fechas de ejecución.

## Entrega y resguardos

Informe y tablas agregadas nuevos en outputs, con fuentes, hashes y QA. Código en
scripts conforme a la convención operativa del subproyecto. Identificadores solo en
memoria; no exportar registros individuales. No crear una nueva versión de Excel,
no modificar reglas de VIG, no hacer commit/push. Se conserva la revisión anterior.
QA: reproducción 528/527/66, diferencias 14/19, uniones únicas y concordantes,
sumas por carrera y transiciones, comparación independiente, fuentes y V16 intactas.

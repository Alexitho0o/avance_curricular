# H002 · Techo alcanzado con las fuentes disponibles

**D · Alexi, 30-10-2026. Estado: TECHO_ALCANZADO; detener iteraciones con las mismas fuentes.**
Este cierre documental complementa CIERRE_H002L, sin modificar la tabla ni la regla activa.

## Evidencia reutilizada (B/C/E)

H002m, commit `a0bb8f10b4143402b7dfc818c25506b74ead1ada`:

- Cierra **0 de 34** opciones de revisión manual; permanecen **78 tipos E** de los 102 revisados.
- Sensibilidad 2025 sin los patrones agregados también observados en SIES: **99,586207 %**, expresado
  como **99,6 %** a un decimal. Tiene denominador propio (2.175); no sustituye el principal (2.313).
- El acierto principal 2025 es **93,644617 %**. La sensibilidad no acredita errores individuales
  ni autoriza excluir personas del indicador. En 2026 alcanza **94,384106 %** sin patrones,
  frente a **91,829897 %** principal: no se ha logrado la meta de 98 %.
- El catálogo v3 y los hallazgos H002m siguen **CANDIDATOS**, sin activación. Los 37 códigos
  nuevos mantienen su condición de cierre con MU2027.

Fuentes fijadas (sin ejecutar otra vez):

- `outputs/regla_operativa_mu_v3_20261029/RESULTADOS.json` · SHA-256 `0b1dbf93917b065d53a0cc708d8fef69be7f21165199f6fbae590d68487a7031`.
- `data/paridad_codigo_sies/regla_operativa_mu_v3/METRICAS_TOTALES.json` · SHA-256 `45dc9027dc304574cab5e9cabf199ad115911e22ce17985d21381d1c2861ab59`.
- `outputs/regla_operativa_mu_v3_20261029/INFORME.md` · SHA-256 `f0f0f693d278f84c64a569e783a5077c0be1644d4eac9a867682291a7ea82396`.
- `outputs/regla_operativa_mu_v3_20261029/QA_FINAL.json` · SHA-256 `a51a065ebec913b16b2c30ff8f8843d305452cb7dd82f802865e40943470ac5a`.

## Únicas fuentes nuevas que permiten reabrir

1. **MU 2027**, para matrícula y código del nuevo proceso.
2. **Oferta 2027 aceptada en PES**, con evidencia de aceptación; la V06 preparada no la sustituye.
3. **Precarga AC 2027**, acreditando proceso y matrícula de referencia 2026.
4. **Registro histórico UMAS por año**, con cobertura y corte comparables.

La llegada de una fuente sólo reabre la pregunta que realmente puede responder: verificar origen,
año, estructura, hash y cobertura; consultar primero el [mapa](../../../docs/MAPA_RESULTADOS_GOBERNADOS.md).
No ampliar la búsqueda sobre las mismas fuentes ni volver a cuadrar Datos Alumnos actual contra
historia 2007–2021. Cada nuevo hito debe declarar meta medible y criterio de parada; dos iteraciones
seguidas sin mejora obligan a detenerse y documentar el techo. No se declara artificialmente que
H002j y H002m tuvieron idéntico acierto: el techo actual se registra por esta decisión expresa D,
con las métricas y límites publicados.

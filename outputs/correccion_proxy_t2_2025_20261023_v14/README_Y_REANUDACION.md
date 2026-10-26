# Proxy T2-2025 corregido por identidad completa

B/C · En la población T1-2025 original hay 1150 personas: 1130 R y20 P. El cruce exacto con PROMEDIOS, ANO2025/PERIODO2, encuentra actividad en694 personas:680 R y14 P. De ellas,600 R y11 P tienen al menos una fila con ESTADO_ACADEMICO=VIGENTE. Resultado:611/1150=53,13043478%, frente a600/1150=52,17391304%; diferencia0,95652174 puntos porcentuales.

C · Se verifican RUT+DV completos. Para los20 P, MU deja el DV vacío; la relación se toma exclusivamente del respaldo IPSS_Procesamiento.xlsx, hoja2025_carga, J RUT / BU N_DOC / BV DV. La identidad de PROMEDIOS coincide por RUT+DIG. No se utiliza nombre ni se inventa el DV. Esta correspondencia comprobada no autoriza generalizar el procedimiento a cualquier documento P. Cero colisiones entre R yP y cero duplicados en1150. Los36 grupos por códigoT1 suman611.

B/C · El600 anterior estaba pegado en26!E1852. El constructor recuperado, preservado en evidencia/add_promedios_sheet_original.py, inserta una lista de seis resultados precalculados; no contiene el algoritmo que produjo600. El QA anterior lo usaba otra vez como valor esperado. Las fórmulas de división no eran la causa: recibían un numerador que no concilia con el cruce uniforme de la población completa.

E · No se recuperó una nómina original de600 ni el algoritmo que la produjo. Por ello no se afirma que existió un filtro explícito para excluir P ni que se identificó la instrucción original causante. Se demuestra que el recálculo uniforme obtiene611 y que la diferencia numérica equivale a11 P que cumplen el criterio. El resultado corregido se sustenta en esa reconstrucción verificable, no en atribuir una intención al script anterior.

D/C · La autorización del usuario permite corregir el cruce sin cambiar denominadores. V14 actualiza solo26!D1852/E1852/F1852 y las referencias de18,28,52 y53. Flujo: conteos por códigoT1 en53 → suma26!E1852 → resumen18!E8 →52!E8; las tasas dividen por los1150 conservados. Los controles28 leen las salidas y contrastan el recálculo independiente; no alimentan el cálculo.

C · Se conservaron las otras49 hojas,13 gráficos,35 tablas, formatos, denominadores, fuentes y códigosSIES. No se añadieron integrantes ni asignaciones de versión. No se cambió la tasa anual, la fotoT3 ni los otros períodos. El constructorV13 queda como historia reproducible; esta corrección usa los scriptsV14 y su manifiesto propios.

E · Continúa siendo un proxy de actividad del período más estado académico del extracto. No acredita por sí solo vigencia histórica de matrícula al cierre. Las secciones por sector/tipo/carrera que requieren foto de cierre permanecen pendientes. La fila1853 del proxy2025-T3 no se modifica en este alcance; su diferencia previa permanece pendiente y no alimenta la fotoT3 publicada en18.

## Reproducción y QA

C · Ejecutar `scripts/recalcular_proxy_t2_2025_v14_20261023.py --output-dir <carpeta nueva>`, conservando las fuentes y hashes fijados. Produce únicamente RESULTADO_AGREGADO.json. Preparar las modificaciones con `scripts/ensamblar_proxy_t2_2025_v14_20261023.py prepare <carpeta>`, recalcular mediante `scripts/editar_proxy_t2_2025_v14_20261023.mjs <carpeta>` con Artifact Tool y finalizar con el ensamblador en fasefinish. La evidencia de presentación original debe estar en su ruta persistente declarada; nunca ejecutar el constructorrecuperado para producirV14.

C · EDICION.json fija129 celdas a verificar (90 cambios de contenido y39 actualizaciones de caché), RESULTADO_AGREGADO.json conserva el cálculo por36 códigos, DIFF_CELDAS.json muestra antes/después y QA_CORRECCION.json registra los controles. El libro del Escritorio es idéntico al del proyecto. No se exportaron identificadores nuevos ni archivos individuales.

E · Se recalculó con Artifact Tool y se contrastó con los conteos independientes. No se probó apertura en Excel nativo. Un control de igualdad con tolerancia extremadamente pequeña no evaluó correctamente en Artifact pese a valores iguales; se sustituyó por comparación a diez decimales y se verificó externamente a1e-12. Las tasas mantienen toda su precisión.

B · Rama feature/ire-2026; HEAD antes/después80ca13a5a249a1a2bd53a699f5f73689b1f53040. Sin commit ni push. Los cambios previos del repositorio no se incorporaron a ninguna operaciónGit.

## Checkpoint

C · Corrección local terminada para proxy2025-T2;611/1150. E · Pendientes: mecanismo original600, acreditación de vigencia histórica y diferencia del proxy2025-T3 fuera de este alcance. No reabrir ni alterar los denominadores ni el diccionarioSIES para explicar esta diferencia.

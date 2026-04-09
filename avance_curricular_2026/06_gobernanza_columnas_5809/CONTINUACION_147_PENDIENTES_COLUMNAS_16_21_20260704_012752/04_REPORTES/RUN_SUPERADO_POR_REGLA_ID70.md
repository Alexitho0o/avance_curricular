# Run superado por auditoria ID 70

Esta corrida no debe usarse como resultado vigente.

Motivo: durante la auditoria posterior se detecto que ID_FILA_5809 = 70 fue calculado usando un derivado previo que contenia CODIGO_UNICO_5809, pero no una equivalencia institucional documentada para decidir entre los CODCARR observados AUDT | ICDA.

Accion: se endurecio la regla del script para mantener ID 70 pendiente salvo CODCARR unico o equivalencia documentada explicita, y se relanzo la ejecucion en una carpeta posterior.

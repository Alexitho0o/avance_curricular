# Riesgos y controles

| Riesgo | Nivel | Control |
|---|---|---|
| HEAD actual no coincide con HEAD informado | Alto | No usar HEAD actual como base automatica; documentar y pedir autorizacion. |
| Commit local ahead mezcla otros subproyectos | Alto | No hacer cherry-pick completo; reconstruir rutas selectivas. |
| Rama backup divergida | Medio | Crear rama limpia desde base confirmada en fase posterior. |
| CSV/TSV publicables ignorados | Medio | Excepciones especificas en `.gitignore` o alternativa autorizada, nunca debilitar regla global. |
| PII en fuentes o auditorias completas | Alto | No versionar raw, normalized ni auditorias detalladas con personas. |
| Release parcialmente trackeada en HEAD actual | Medio | Validar 29 archivos filesystem y decidir incorporacion completa solo en rama limpia. |
| Referencias remotas no actualizadas | Medio | Requerir autorizacion para fetch en hito posterior. |

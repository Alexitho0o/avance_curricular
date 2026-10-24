"""Clasifica evidencia académica sin promover reglas de versión."""
def estado_contexto(codigos, ambiguos, contradicciones):
    if contradicciones:return 'CONTRADICCION_ENTRE_EVIDENCIAS'
    if len(codigos)>1:return 'MULTIPLES_DESTINOS'
    if len(codigos)==1:return 'DESTINO_UNICO_CON_EVIDENCIA_AMBIGUA' if ambiguos else 'DESTINO_UNICO_OBSERVADO'
    if ambiguos:return 'SOLO_EVIDENCIA_AMBIGUA'
    return 'SIN_EVIDENCIA'


def comparar_evidencias(documentales, inferidos):
    return bool(documentales and inferidos and not (set(documentales)&set(inferidos)))

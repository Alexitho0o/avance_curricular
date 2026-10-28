"""Lectores diagnósticos UMAS. No cambia reglas de carga, planes ni indicadores."""
import collections,datetime,itertools,os,re,unicodedata

def texto(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip()

def clave(x):
    s=''.join(c for c in unicodedata.normalize('NFD',texto(x).upper()) if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]','',s)

def dv_modulo11(body):
    s=texto(body)
    if not s.isdigit():return None
    n=11-sum(int(d)*(2+i%6) for i,d in enumerate(reversed(s)))%11
    return '0' if n==11 else 'K' if n==10 else str(n)

def rut_validado(raw,dv=None,*,formato='auto'):
    """Control de formato, sin corregir la fuente ni inventar DV ausentes."""
    s=texto(raw).upper().replace('.','').replace(' ','')
    if not s:return {'estado':'VACIO','cuerpo':None,'dv':None,'formato':'vacio'}
    if formato=='cuerpo':return {'estado':'SIN_DV' if s.isdigit() else 'NO_COMPARABLE','cuerpo':s,'dv':None,'formato':'cuerpo_sin_dv'}
    if dv is not None and texto(dv)!='':body,check,kind=s,texto(dv).upper(),'columnas_separadas'
    elif '-' in s:
        parts=s.rsplit('-',1);body,check,kind=parts[0],parts[1],'guion'
    elif re.fullmatch(r'\d+[0-9K]',s):body,check,kind=s[:-1],s[-1],'dv_pegado_candidato'
    else:return {'estado':'NO_COMPARABLE','cuerpo':None,'dv':None,'formato':'no_run_o_formato_invalido'}
    valid=bool(body.isdigit() and re.fullmatch('[0-9K]',check) and dv_modulo11(body)==check)
    return {'estado':'VALIDO' if valid else 'DV_NO_VALIDADO','cuerpo':body,'dv':check,'formato':kind}

def patron_tokens_privados(tokens):
    """Regex exacta comprimida por prefijos; no reduce el alcance del escaneo."""
    def expression(values):
        if len(values)==1:return re.escape(values[0])
        prefix=os.path.commonprefix((values[0],values[-1]))
        if prefix:return re.escape(prefix)+expression([v[len(prefix):] for v in values])
        terminal=values[0]==''
        branches=[re.escape(ch)+expression([v[1:] for v in group]) for ch,group in itertools.groupby((v for v in values if v),key=lambda v:v[0])]
        body=branches[0] if len(branches)==1 else '(?:'+'|'.join(branches)+')'
        return '(?:'+body+')?' if terminal else body
    values=sorted({t for t in tokens if len(t)>=6})
    if not values:return re.compile(r'(?!)')
    return re.compile(r'(?<![A-Za-z0-9])(?:'+expression(values)+r')(?![A-Za-z0-9])')

def cabeceras_unicas(headers,permanencia=False):
    counts=collections.Counter(texto(h) for h in headers if texto(h));seen=collections.Counter();out=[]
    for i,h in enumerate(headers,1):
        s=texto(h) if texto(h) else 'COLUMNA_'+str(i).zfill(3)
        if counts[s]>1:
            if permanencia:
                # Bloques delimitados por las cabeceras Fecha...Academia/Finanzas.
                anchor_fin=next((j for j,v in enumerate(headers,1) if 'FINANZAS' in clave(v) and 'FECHA' in clave(v)),None)
                s+='_' + ('ACADEMIA' if anchor_fin is not None and i<anchor_fin else 'FINANZAS')
            else:seen[s]+=1;s+='_'+str(seen[s])
        out.append(s)
    if len(set(out))!=len(out):raise ValueError('No se lograron cabeceras unívocas')
    return out

def etiqueta_inscripcion(value):
    m=re.fullmatch(r'(\d{4})-(\d+)\|(SI TOMO RAMOS|NO TOMO RAMOS)',texto(value).upper())
    if not m:return None
    return int(m[1]),int(m[2]),m[3]=='SI TOMO RAMOS'

def periodo_umas(value):
    m=re.fullmatch(r'(\d{4})-(\d+)',texto(value))
    return (m[1],m[2]) if m else None

def comparacion_univoca(values,target):
    vals={v for v in values if v not in ('',None)}
    if not target or not vals:return 'sin_dato'
    if len(vals)>1:return 'ambiguos'
    return 'concordantes' if next(iter(vals))==target else 'diferentes'

ANALITICAS={
 'CODCARPR','CODCARR','CODIGOCARRERA','CARRERAALUM','CODIGOCARRERAACTUAL','NOMBREL','NOMBRECARRERA','CARRERA','CARRERAACTUAL',
 'ANO','ANIO','ANOMATRICULA','ANOINGRESO','ANOINGRESO','ANOEGRESOENSENANZAMEDIA','PERIODO','PERIODOMATRICULA','PERIODOINGRESO','ANOPERIODOINGRESO','ANOPERIODOMATRICULA',
 'JORNADA','SEDE','CODSEDE','REGIMEN','REGIMENCARRERAALUMNO','ESTADOACADEMICO','ESTADOALUMNO','SITUACION','CATALUMNO','ESTADO','DESCRIPCIONESTADO','CONVALIDADO','NIVEL',
 'PLANDEESTUDIO','CODPESTUD','RAMOEQUIV','CODRAMO','CODSECC','ASIGNATURA','NOTAFINAL','EXAMEN','NOTAENSENANZAMEDIA',
 'TOTALRAMOSMALLA','CANTRAMOSAPROB','CANTRAMOSREPROB','AVANCEMALLA','NASGCERRADAS','NASGABIERTAS','NSOLEMNESRENDIDAS','SOLEMNE1','SOLEMNE2','SOLEMNE3',
 'REPROB','REPROBPORINASIS','NTO','NOTOMAASIGNATURAS','CANTASIGINSCRITAS','PORCASISTENCIAREAL','RASISTENCIA','RRIESGONOTA',
 'INSCRIBEASIGNATURASENT1','INSCRIBEASIGNATURASENT2','INSCRIBEASIGNATURASENT3','SEXO','NACIONALIDAD','TIPODOC','TIPODOCUMENTO','TIPOCOMUNICACION',
 'FECHAEXTRACCION'
}

def sensibilidad(header,family):
    k=clave(header)
    if family=='PERMANENCIA' and k=='NOMBRE':return 'analítica' # nombre de sede, no alumno
    if any(t in k for t in ('RUT','CODCLI','DOCUMENTO','DIG','DV','NOMBRE','PATERNO','MATERNO','APELLIDO','MAIL','FONO','DIRECCION','COMENTARIO','OBSERVACION','GESTION','MOROS','FINANZ','CUOTA','MONTO','ECONOM','RESPONSABLE','EMPRESA','RENTA','CIVIL','HIJOS','EMERGENCIA','COLEGIO','NACIMIENTO')):
        if k in ANALITICAS:return 'analítica'
        return 'privada'
    return 'analítica' if k in ANALITICAS else 'excluida'

def semantica(header,family,contract):
    k=clave(header)
    if k=='RUT' and family=='PERMANENCIA':return 'Cuerpo numérico del documento sin DV en el corte27-10-2026, corroborado por CODCLI contra DatosAlumnos. No separar el último carácter como DV ni inventarlo.','B/C','persona'
    if k=='CODCLI':return 'Expediente/matrícula UMAS; no extraer año o período desde su patrón.','B/C','expediente'
    if k=='NIVEL':return ('Nivel de la asignatura en el plan; no prueba avance completado.' if family=='PROMEDIOS' else 'Nivel administrativo observado del estudiante; no es avance aprobado.'),'B/C','asignatura' if family=='PROMEDIOS' else 'expediente'
    if k=='ESTADO' and family=='PROMEDIOS':return 'Estado de la asignatura/resultado; distinto de ESTADO_ACADEMICO.','B/C','asignatura'
    if k in ('ESTADOACADEMICO','ESTADOALUMNO'):return 'Estado del estudiante en el extracto; no acredita secuencia histórica ni VIG SIES.','B/C','expediente-fotografía'
    if k in ('CODCARPR','CODCARR','CARRERAALUM'):return 'Código interno de carrera observado en este contexto; no es código único SIES.','B/C','carrera-expediente'
    if k=='CODIGOCARRERAACTUAL':return 'Carrera actual reportada; conservar separada de CARRERA_ALUM y comprobar concordancia.','B/E','expediente-fotografía'
    if k=='NOMBRE' and family=='PERMANENCIA':return 'Nombre de sede observado junto con COD_SEDE.','B','sede'
    if k=='FECHAEXTRACCION':return 'Fecha declarada de la fotografía; no fecha de cambio de cada estado.','B','extracto'
    if k in ('PLANDEESTUDIO','CODPESTUD'):return 'Código de plan declarado; no se deduce desde año, nivel o nombre de carrera.','B','plan'
    if k.startswith('INSCRIBEASIGNATURASENT'):return 'Contenedor de etiqueta AAAA-P|SI/NO TOMO RAMOS; el período se lee del valor, no del nombre de columna.','B/C','expediente-período-etiquetado'
    if k in ('ANOPERIODOINGRESO','ANOPERIODOMATRICULA'):return 'Etiqueta año-período UMAS; separar sintácticamente y conservar período literal sin convertir a semestre.','B/C','expediente-período'
    if k=='TOTALRAMOSMALLA':return 'Total de ramos declarado para el expediente; falta plan para atribuirlo a una malla formal.','B/E','expediente-plan-no-informado'
    if k=='LISTARAMOSPEND':return 'Lista textual de ramos pendientes; analizar corte de longitud, no usar como malla completa.','B/E','expediente'
    reported={
        'ANO':'Año declarado en la fila del reporte; conservar excepciones distintas del año de la fotografía.',
        'ANOINGRESO':'Año de ingreso reportado del expediente; no equivale a primer ingreso institucional.',
        'FECHAMAT':'Fecha de matrícula declarada; no está acreditado si es primera matrícula o renovación.',
        'CATALUMNO':'Categoría/situación del alumno reportada; no asigna VIG SIES por sí sola.',
        'CODSEDE':'Código de sede UMAS reportado, separado del nombre y del código SIES.',
        'NOMBRECARRERA':'Nombre descriptivo de la carrera del expediente; no usar como llave de identidad.',
        'CARRERAACTUAL':'Nombre de la carrera actual reportada; no sustituye carrera original del CODCLI.',
        'REGIMENCARRERAALUMNO':'Régimen de la carrera reportado; no autoriza conversión automática de períodos.',
        'REPROB':'Porcentaje de reprobación exportado; denominador y ventana del cálculo no acreditados.',
        'REPROBPORINASIS':'Porcentaje de reprobación por inasistencia exportado; fórmula y ventana pendientes.',
        'NASGCERRADAS':'Cantidad reportada de asignaturas cerradas; no acredita aprobación ni cierre de todos los niveles.',
        'NASGABIERTAS':'Cantidad reportada de asignaturas abiertas; alcance temporal del conteo pendiente.',
        'NSOLEMNESRENDIDAS':'Cantidad reportada de evaluaciones solemnes rendidas; ventana y forma de conteo pendientes.',
        'SOLEMNE1':'Indicador Solemne1 exportado; unidad y fórmula pendientes, no asumir que sea una nota.',
        'SOLEMNE2':'Indicador Solemne2 exportado; unidad y fórmula pendientes, no asumir que sea una nota.',
        'SOLEMNE3':'Indicador Solemne3 exportado; unidad y fórmula pendientes, no asumir que sea una nota.',
        'P1':'Campo P1 sin definición acreditada; no interpretarlo como primer período por su nombre.',
        'NASIGNATURACONASISTENCIAMENORA70':'Número reportado de asignaturas con asistencia menor al70%; corte y denominador pendientes.',
        'RRIESGONOTA':'Indicador de riesgo por notas exportado; umbrales y fórmula no acreditados.',
        'RASISTENCIA':'Indicador de riesgo por asistencia exportado; umbrales y fórmula no acreditados.',
        'NOTOMAASIGNATURAS':'Marca reportada de no tomar asignaturas; no prueba deserción ni ausencia histórica.',
        'ESIGUAL':'Comparador auxiliar del archivo; operandos y fórmula no acreditados.',
        'CANTRAMOSAPROB':'Cantidad de ramos aprobados reportada; validar si deduplica intentos y reconoce equivalencias.',
        'CANTRAMOSREPROB':'Cantidad de ramos reprobados reportada; validar intentos versus asignaturas distintas.',
        'AVANCEMALLA':'Porcentaje de avance exportado; no se redefine su fórmula ni se acredita el plan con este campo solo.',
        'FECHASITUACIONACADEMICA':'Fecha reportada de situación académica; no acredita por sí sola un historial de transiciones.',
        'CANTASIGINSCRITAS':'Cantidad de asignaturas inscritas exportada; ventana temporal y deduplicación pendientes.',
        'PORCASISTENCIAREAL':'Porcentaje de asistencia exportado; sesiones consideradas y fórmula pendientes.',
        'REGIMEN':'Régimen académico reportado; períodos internos se conservan sin homologación universal a semestre.',
        'CODSECC':'Código de sección reportado; no implica jornada por sí mismo.',
        'CODRAMO':'Código de asignatura cursada; no equivale automáticamente al ramo homologado.',
        'RAMOEQUIV':'Código de equivalencia de ramo reportado; requiere gobierno de equivalencias para fusionar conteos.',
        'ASIGNATURA':'Nombre de la asignatura de la fila académica; distinto de nombre de persona.',
        'CARRERA':'Nombre de carrera en PROMEDIOS; usar CODCARR como código y mantener ambos separados.',
        'NOTAFINAL':'Nota final reportada para la inscripción; no se infiere aprobación desde una nueva regla de umbral.',
        'EXAMEN':'Campo de examen reportado, separado de NOTA_FINAL; fórmula de ponderación pendiente.',
        'DESCRIPCIONESTADO':'Descripción del resultado de asignatura; no es estado académico de la persona.',
        'CONVALIDADO':'Marca de reconocimiento/convalidación reportada; su inclusión anual/acumulada depende del proceso.',
        'TIPOCOMUNICACION':'Clasificación del evento de gestión, no estado académico ni evidencia de permanencia.'
    }
    if k in reported:return reported[k],'B/E','asignatura/inscripción' if family=='PROMEDIOS' else 'campo del reporte; alcance por confirmar'
    if k in contract:return contract[k]['interpretacion_vigente'],'B/C','según contrato exploratorio 20261021'
    return 'Campo observado '+header+'; semántica temporal o fórmula no acreditada salvo referencia explícita.','E','pendiente'

"""Presentation model for the annual workbook; never changes period eligibility."""
import json
import re

PERCENT = '[=0]0%;[=1]0%;0.0%'
NAMES = ['Panel ejecutivo', 'Cobertura', 'Explorador preguntas',
         'Panel financiamiento', 'Panel rendimiento', 'Panel sectorial']


def quoted(value):
    return '"' + str(value).replace('"', '""') + '"'


def panels(model, tables, spec, ref, col, criterion):
    """Keep calculation tables in place and add linked, independently testable views."""
    lookup = {t['name']: t for t in tables}
    records = model['records']
    participation = lookup['Participación']
    segments = {(r[0], r[1]): i for i, r in enumerate(participation['rows'], 7)}
    sectors = sorted({r[2] for r in records})
    careers = sorted({r[5] for r in records})
    end = max(7, len(records) + 6)
    base = lambda c: ref('Base anual', c, 7, end)

    def metric(dimension, value, column):
        row = segments.get((dimension, value))
        return ref('Participación', column, row) if row else ('"No aplica"' if column==6 else '0')

    def dashboard(name, title, note):
        return dict(spec(name, [], [], note), dashboard=True, title=title,
                    cells={}, merges=[], styles=[], charts=[], heatmaps=[],
                    selectors=[], preview='A1:L38', last_row=38)

    def cell(d, address, value=None, formula=None, role=None):
        first = address.split(':')[0]
        if ':' in address:
            d['merges'].append(address)
        if formula is not None:
            d['formulas'][first] = formula if formula.startswith('=') else '=' + formula
        else:
            d['cells'][first] = value
        if role:
            d['styles'].append([address, role])

    def kpi(d, column, label, formula, fmt='integer'):
        c = col(column)
        cell(d, f'{c}6:{col(column+2)}6', label, role='kpi_label')
        cell(d, f'{c}7:{col(column+2)}8', formula=formula, role='kpi')
        d['styles'].append([f'{c}7:{col(column+2)}8', fmt])

    def heading(d, row, title):
        cell(d, f'A{row}:L{row}', title, role='section')

    def chart(d, title, labels, series, start='A11', stop='F25', fmt='integer', stacked=False):
        d['charts'].append(dict(title=title, labels=labels, series=series,
                                start=start, end=stop, format=fmt, stacked=stacked))

    def grid(d, start, headers, widths, rows):
        """Merge only presentation columns; detail/source tables remain native tables."""
        positions = []
        current = 0
        for header, width in zip(headers, widths):
            positions.append(current)
            cell(d, f'{col(current)}{start}:{col(current+width-1)}{start}', header, role='header')
            current += width
        for n, values in enumerate(rows, start+1):
            for c, width, value in zip(positions, widths, values):
                address = f'{col(c)}{n}:{col(c+width-1)}{n}'
                if isinstance(value, str) and value.startswith('='):
                    cell(d, address, formula=value, role='body' if n % 2 else 'stripe')
                else:
                    cell(d, address, value, role='body' if n % 2 else 'stripe')
        d['last_row'] = max(d['last_row'], start + len(rows) + 2)
        return positions

    executive = dashboard(NAMES[0], 'Caracterización estudiantil',
        'Personas únicas en la selección. Los períodos y sectores pueden solaparse; no sumar sus personas.')
    for c, title, formula, fmt in [
        (0, 'Personas únicas', "'Resumen'!B8", 'integer'),
        (3, 'Respuestas completas', "'Resumen'!B9", 'integer'),
        (6, 'Participación completa', "'Resumen'!B12", 'percent'),
        (9, 'Sin respuesta', "'Resumen'!B11", 'integer')]:
        kpi(executive, c, title, formula, fmt)
    period_rows = []
    for p in ('P1', 'P2', 'P3'):
        n = metric('Período', p, 2)
        period_rows.append([p, '='+n, *['='+metric('Período', p, c) for c in (3,4,5)],
                            f'=IF({n}=0,"No aplica",{metric("Período",p,3)}/{n})'])
    heading(executive, 27, 'Participación por período')
    grid(executive, 28, ['Período','Personas','Completas','Incompletas','Sin respuesta','Participación'], [2]*6, period_rows)
    executive['styles'].append(['K29:L31','percent'])
    # Dedicated chart ranges are ratios of the same person-state counts, not summed percentages.
    for r, p in enumerate(('P1', 'P2', 'P3'), 42):
        cell(executive, f'A{r}', p)
        n = metric('Período', p, 2)
        for c, source in enumerate((3,4,5), 1):
            cell(executive, f'{col(c)}{r}', formula=f'IF({n}=0,"",{metric("Período",p,source)}/{n})')
    chart(executive, 'Estado de respuesta por período', 'A42:A44',
          [('Completa','B42:B44','#008577'),('Incompleta','C42:C44','#D69B23'),
           ('Sin respuesta','D42:D44','#A8B2BD')], fmt='percent', stacked=True)
    for r, s in enumerate(sectors, 47):
        cell(executive, f'A{r}', s)
        cell(executive, f'B{r}', formula=metric('Sector', s, 6))
    if sectors:
        chart(executive, 'Participación por sector', f'A47:A{46+len(sectors)}',
              [('Participación',f'B47:B{46+len(sectors)}','#247BA0')], 'G11','L25','percent')
    cell(executive, 'A34:F35', formula='="Matrículas en la selección: "&TEXT(\'Resumen\'!B7,"#,##0")', role='note')
    cell(executive, 'G34:L35', formula='="Respuestas incompletas: "&TEXT(\'Resumen\'!B10,"#,##0")', role='note')
    executive['last_row'] = max(50, 47+len(sectors))

    coverage = dashboard(NAMES[1], 'Participación y cobertura',
        'Brecha = personas sin respuesta completa. Ranking por cantidad, con denominador y tasa visibles.')
    for c, label, formula, fmt in [(0,'Personas únicas',"'Resumen'!B8",'integer'),
        (3,'Completas',"'Resumen'!B9",'integer'),(6,'Por completar',"'Resumen'!B10+'Resumen'!B11",'integer'),
        (9,'Participación',"'Resumen'!B12",'percent')]:
        kpi(coverage,c,label,formula,fmt)
    heading(coverage,10,'Participación por sector y período')
    heatrows=[]
    for s in sectors:
        values=[s]
        for p in ('P1','P2','P3'):
            values.append('='+metric('Sector período', json.dumps([p,s],ensure_ascii=False),6))
        heatrows.append(values)
    grid(coverage,11,['Sector','P1','P2','P3'],[6,2,2,2],heatrows)
    for c in ('G','I','K'):
        coverage['heatmaps'].append(f'{c}12:{c}{11+len(sectors)}') if sectors else None
    coverage['styles'].append([f'G12:L{max(12,11+len(sectors))}','percent'])
    # Tie-broken rank updates with filters. Every career remains in the detail beneath it.
    rank_start=7
    ranking=spec('Ranking carreras',['Carrera','Personas','Por completar','Participación','Orden'],
                 [[career,None,None,None,None] for career in careers],
                 'Orden dinámico por cantidad pendiente; desempate por orden estable de carrera. Responde a Filtros.',[65,18,18,18,18])
    ranking['percent_columns']=[3]
    for i, career in enumerate(careers, rank_start):
        ranking['formulas'].update({f'B{i}':'='+metric('Carrera',career,2),
            f'C{i}':f'=B{i}-{metric("Carrera",career,3)}',
            f'D{i}':'='+metric('Carrera',career,6),
            f'E{i}':f'=COUNTIF($C${rank_start}:$C${rank_start+len(careers)-1},">"&C{i})+COUNTIF($C${rank_start}:C{i},C{i})'})
    top=min(8,len(careers))
    if top:
        chart(coverage,'Carreras con más respuestas por completar',f'A34:A{33+top}',
              [('Pendientes',f'I34:I{33+top}','#D69B23')], 'A17','L29')
    heading(coverage,31,'Carreras: personas, brecha y tasa')
    rows=[]
    for i in range(len(careers)):
        pos=f'MATCH({i+1},{ref("Ranking carreras",4,rank_start,rank_start+len(careers)-1)},0)'
        rows.append([f'=INDEX({ref("Ranking carreras",c,rank_start,rank_start+len(careers)-1)},{pos})' for c in range(4)])
    grid(coverage,33,['Carrera','Personas','Por completar','Participación'],[6,2,2,2],rows)
    coverage['styles'].append([f'K34:L{max(34,33+len(rows))}','percent'])
    cell(coverage,'A32:L32','Una persona por carrera; los segmentos pueden solaparse. No sumar carreras.',role='note')

    # One option registry across periods, retaining literal codes and full source labels.
    options={}
    question_meta={}
    for table_name in ('Preguntas','Financiamiento'):
        for r,row in enumerate(lookup[table_name]['rows'],7):
            parent=row[2].split('[')[0]
            key=(parent,row[2],row[4])
            item=options.setdefault(key,dict(parent=parent,code=row[2],choice=row[4],label=row[3],group=row[1],sources={}))
            item['sources'][row[0]]=(table_name,r)
            question_meta.setdefault(parent,(row[1],row[3].split('[')[0].strip()))
    # Keep each question contiguous so a selector needs one lookup, not one
    # full-registry search per displayed value. Preserve order within question.
    parent_order={parent:i for i,parent in enumerate(question_meta)}
    options=dict(sorted(options.items(),key=lambda item:parent_order[item[0][0]]))
    option_rows=[]
    option_formulas={}
    available={}
    for item in options.values():
        for period,source in item['sources'].items():
            available.setdefault((item['code'],period),source)
    for key,item in options.items():
        r=len(option_rows)+7
        label=item['label'] if item['choice']=='Seleccionada' else item['choice']
        # The original full wording remains in Preguntas/Financiamiento. Panels
        # repeat only the literal subquestion, with its code beside it.
        if item['choice']=='Seleccionada':
            match=re.search(r'\[([^\[\]]+)\]\s*$',label)
            if match:
                label=match.group(1)
        option_rows.append([item['parent'],item['code'],label,item['group']]+[None]*12)
        for p in range(1,4):
            source=item['sources'].get(f'P{p}')
            fallback=available.get((item['code'],f'P{p}'))
            for offset,sc in enumerate((5,6,7,8)):
                address=f'{col(4+(p-1)*4+offset)}{r}'
                if source:
                    option_formulas[address]='='+ref(source[0],sc,source[1])
                elif fallback:
                    base_ref=ref(fallback[0],6,fallback[1])
                    option_formulas[address]=('=0' if offset==0 else
                        f'=IF({ref(fallback[0],7,fallback[1])}="Tipo no verificado","Tipo no verificado",IF({base_ref}=0,"No aplica",0))' if offset==2 else '='+ref(fallback[0],sc,fallback[1]))
                else:
                    option_formulas[address]='="No disponible"'
    option_table=spec('Opciones panel',['Pregunta','Código literal','Opción / subpregunta','Grupo']+
                      [f'{name} P{p}' for p in range(1,4) for name in ('N','Base válida','Porcentaje','Sin válida')],option_rows,
                      'Respuestas completas por período. No es un total anual de personas. Sin válida no distingue salto de omisión.',[18,24,70,45]+[18]*12)
    option_table['formulas']=option_formulas
    option_table['percent_columns']=[6,10,14]
    groups=list(dict.fromkeys(meta[0] for meta in question_meta.values()))
    ordered_questions=sorted(question_meta.items(),key=lambda item:groups.index(item[1][0]))
    starts={}
    sizes={}
    for i,row in enumerate(option_rows,1):
        starts.setdefault(row[0],i)
        sizes[row[0]]=sizes.get(row[0],0)+1
    question_list=spec('Selector preguntas',['Código','Grupo','Enunciado','Inicio opciones','Cantidad opciones'],
                       [[p,*meta,starts[p],sizes[p]] for p,meta in ordered_questions],
                       'Selección de preguntas cerradas disponibles. Textos libres conservados en Respuestas abiertas.',[20,48,100,18,18])
    qend=max(7,len(question_list['rows'])+6)
    oend=max(7,len(option_rows)+6)

    explorer=dashboard(NAMES[2],'Preguntas y condiciones',
        'Solo respuestas completas del universo. Sin válida incluye vacíos y saltos; no se interpreta automáticamente como No aplica.')
    first=ordered_questions[0][0] if ordered_questions else 'Sin preguntas cerradas'
    cell(explorer,'A6:B6','Grupo',role='kpi_label')
    cell(explorer,'C6:H6',groups[0] if groups else 'Sin grupo',role='input')
    cell(explorer,'I6','Código',role='kpi_label')
    cell(explorer,'J6:L6',first,role='input')
    explorer['selectors'].append(dict(cell='C6',values=groups or ['Sin grupo']))
    explorer['selectors'].append(dict(cell='J6',source=f'OFFSET(\'Selector preguntas\'!$A$7,MATCH($C$6,\'Selector preguntas\'!$B$7:$B${qend},0)-1,0,COUNTIF(\'Selector preguntas\'!$B$7:$B${qend},$C$6),1)'))
    same_group=f'COUNTIFS(\'Selector preguntas\'!$A$7:$A${qend},$J$6,\'Selector preguntas\'!$B$7:$B${qend},$C$6)=1'
    cell(explorer,'A7:L9',formula=f'IF({same_group},INDEX(\'Selector preguntas\'!$C$7:$C${qend},MATCH(J6,\'Selector preguntas\'!$A$7:$A${qend},0)),"Seleccione un código del grupo elegido")',role='question')
    # A compact registry lets dependent options refresh without dynamic-array spill functions.
    max_options=max(list(sizes.values()) or [1])
    for i,row in enumerate(option_rows,7):
        option_table['rows'][i-7].append(None)
        ordinal=i-6-starts[row[0]]+1
        option_formulas[f'Q{i}']=f'IF(AND(A{i}=\'Explorador preguntas\'!$J$6,D{i}=\'Explorador preguntas\'!$C$6),{ordinal},0)'
        option_formulas[f'Q{i}']='='+option_formulas[f'Q{i}']
    option_table['headers'].append('Orden opción seleccionada')
    selector_index=spec('Índices panel',['Ordinal','Posición opción','Cantidad seleccionada','Inicio seleccionado'],
                        [[i,None,None,None] for i in range(1,max_options+1)],
                        'Índices compartidos del explorador. No editar; se recalculan con grupo y código.',[18,22,24,24])
    match=f'MATCH(\'Explorador preguntas\'!$J$6,\'Selector preguntas\'!$A$7:$A${qend},0)'
    valid=f'COUNTIFS(\'Selector preguntas\'!$A$7:$A${qend},\'Explorador preguntas\'!$J$6,\'Selector preguntas\'!$B$7:$B${qend},\'Explorador preguntas\'!$C$6)=1'
    selector_index['formulas']['C7']=f'=IF({valid},INDEX(\'Selector preguntas\'!$E$7:$E${qend},{match}),0)'
    selector_index['formulas']['D7']=f'=IF(C7>0,INDEX(\'Selector preguntas\'!$D$7:$D${qend},{match}),0)'
    for i in range(1,max_options+1):
        selector_index['formulas'][f'B{i+6}']=f'=IF(A{i+6}<=$C$7,$D$7+A{i+6}-1,0)'
    cell(explorer,'A26:L27','Gráfico: primeras 10 opciones en orden del instrumento. Todas las opciones y sus bases se conservan debajo. Porcentajes por período; no sumar personas entre períodos.',role='note')
    heading(explorer,29,'Detalle de la pregunta seleccionada')
    rows=[]
    for i in range(1,max_options+1):
        r=30+i
        pos=ref('Índices panel',1,i+6)
        present=f'{pos}>0'
        values=[]
        for c in (1,2,4,6,8,10,12,14):
            values.append(f'=IF({present},INDEX({ref("Opciones panel",c,7,oend)},{pos}),"")')
        rows.append(values)
    grid(explorer,30,['Código','Opción / subpregunta','N P1','% P1','N P2','% P2','N P3','% P3'],[2,4,1,1,1,1,1,1],rows)
    for c in ('H','J','L'):
        explorer['styles'].append([f'{c}31:{c}{30+max_options}','percent'])
    chart(explorer,'Distribución de respuestas por período',f'C31:C{30+min(10,max_options)}',
          [(f'P{p}',f'{c}31:{c}{30+min(10,max_options)}',color) for p,c,color in [(1,'H','#247BA0'),(2,'J','#008577'),(3,'L','#BD7B21')]],'A11','L25','percent')
    # Base and missing counts belong to each literal item (matrix rows can have different bases).
    heading(explorer,33+max_options,'Bases y respuestas sin valor válido por opción')
    diagnostic=[]
    for i in range(1,max_options+1):
        pos=ref('Índices panel',1,i+6)
        present=f'{pos}>0'
        diagnostic.append([f'=IF({present},INDEX({ref("Opciones panel",c,7,oend)},{pos}),"")' for c in (1,5,7,9,11,13,15)])
    grid(explorer,34+max_options,['Código','Base P1','Sin válida P1','Base P2','Sin válida P2','Base P3','Sin válida P3'],[3,1,2,1,2,1,2],diagnostic)

    finance=dashboard(NAMES[3],'Financiamiento de estudios',
        'Selección múltiple: porcentajes por base válida de cada período; pueden sumar más de 100%. No sumar bases de alternativas.')
    finance_items=[]
    for i,(_,item) in enumerate(options.items(),7):
        if any(source[0]=='Financiamiento' for source in item['sources'].values()):
            finance_items.append(i)
    cell(finance,'A6:L8','Alternativas declaradas en respuestas completas. Comparación P1, P2 y P3 con la misma selección institucional.',role='question')
    heading(finance,29,'Alternativas y porcentaje de selección')
    frows=[]
    for i in finance_items:
        frows.append(['='+ref('Opciones panel',c,i) for c in (1,2,4,6,8,10,12,14)])
    grid(finance,30,['Código','Alternativa','N P1','% P1','N P2','% P2','N P3','% P3'],[2,4,1,1,1,1,1,1],frows)
    for c in ('H','J','L'):
        finance['styles'].append([f'{c}31:{c}{max(31,30+len(frows))}','percent'])
    if frows:
        chart(finance,'Selección de alternativas por período',f'C31:C{30+len(frows)}',
              [(f'P{p}',f'{c}31:{c}{30+len(frows)}',color) for p,c,color in [(1,'H','#247BA0'),(2,'J','#008577'),(3,'L','#BD7B21')]],'A10','L27','percent')
    else:
        cell(finance,'A12:L15','No hay alternativas de financiamiento identificadas. Revisar el inventario; no se inventan opciones.',role='note')
    cell(finance,'A28:L28','Bases y códigos completos: hoja Financiamiento.',role='note')

    performance=dashboard(NAMES[4],'Rendimiento académico',
        'Promedio de promedios por matrícula con notas válidas del año. Cobertura = matrículas con notas / matrículas seleccionadas.')
    grade_n=f'SUM({base(22)})'
    no_grades='Sin notas disponibles al corte'
    mean=f'IF({grade_n}=0,"{no_grades}",SUM({base(21)})/{grade_n})'
    kpi(performance,0,'Promedio de notas',mean,'decimal')
    kpi(performance,3,'Matrículas con notas',grade_n)
    kpi(performance,6,'Cobertura de notas',f'IF(\'Resumen\'!B7=0,"No aplica",{grade_n}/\'Resumen\'!B7)','percent')
    kpi(performance,9,'Sin notas',f"'Resumen'!B7-{grade_n}")
    heading(performance,27,'Cobertura y promedio por sector')
    prows=[]
    for s in sectors:
        criteria=f'{base(2)},{criterion(quoted(s))}'
        n=f'SUMIFS({base(22)},{criteria})'
        total=f'SUMIFS({base(17)},{criteria})'
        prows.append([s,'='+total,'='+n,f'=IF({n}=0,"{no_grades}",SUMIFS({base(21)},{criteria})/{n})',f'=IF({total}=0,"No aplica",{n}/{total})'])
    grid(performance,28,['Sector','Matrículas','Con notas','Promedio','Cobertura'],[4,2,2,2,2],prows)
    performance['styles'] += [[f'I29:J{max(29,28+len(sectors))}','decimal'],[f'K29:L{max(29,28+len(sectors))}','percent']]
    if sectors:
        chart(performance,'Promedio por sector (escala 1 a 7)',f'A29:A{28+len(sectors)}',
              [('Promedio',f'I29:I{28+len(sectors)}','#247BA0')],'A11','F25','decimal')
        chart(performance,'Cobertura de notas por sector',f'A29:A{28+len(sectors)}',
              [('Cobertura',f'K29:K{28+len(sectors)}','#008577')],'G11','L25','percent')
    heading(performance,34,'Detalle por período, sector y nivel académico')
    rows=[]
    for i,row in enumerate(lookup['Rendimiento']['rows'],7):
        rows.append(['='+ref('Rendimiento',c,i) for c in range(5)])
    grid(performance,35,['Período','Sector','Nivel','Con notas','Promedio'],[1,4,3,2,2],rows)
    performance['styles'].append([f'K36:L{max(36,35+len(rows))}','decimal'])
    distribution_start=39+len(rows)
    heading(performance,distribution_start,'Distribución de promedios por matrícula')
    bins=[('Menor a 4,0','<4',None),('4,0 a menos de 5,0','>=4','<5'),
          ('5,0 a menos de 6,0','>=5','<6'),('6,0 a 7,0','>=6','<=7')]
    distribution=[]
    for label,lower,upper in bins:
        criteria=f'{base(11)},{quoted(lower)}'+(f',{base(11)},{quoted(upper)}' if upper else '')
        distribution.append([label,f'=SUMIFS({base(22)},{criteria})'])
    grid(performance,distribution_start+1,['Tramo de promedio','Matrículas con notas'],[8,4],distribution)
    chart(performance,'Distribución de promedios (matrículas)',
          f'A{distribution_start+2}:A{distribution_start+5}',
          [('Matrículas',f'I{distribution_start+2}:I{distribution_start+5}','#247BA0')],
          f'A{distribution_start+7}',f'L{distribution_start+20}')
    performance['last_row']=distribution_start+21
    performance['extra_previews']=[dict(name='distribucion',range=f'A{distribution_start}:L{distribution_start+21}')]

    sector=dashboard(NAMES[5],'Análisis sectorial',
        'El sector local se intersecta con los filtros comunes. No amplía el universo seleccionado; matrículas y personas se distinguen.')
    cell(sector,'A6:C6','Sector a examinar',role='kpi_label')
    cell(sector,'D6:I6',sectors[0] if sectors else 'Sin registros',role='input')
    sector['selectors'].append(dict(cell='D6',values=sectors or ['Sin registros']))
    pend=max(7,len(participation['rows'])+6)
    def sector_metric(c):
        return f'SUMIFS({ref("Participación",c,7,pend)},{ref("Participación",0,7,pend)},"Sector",{ref("Participación",1,7,pend)},{criterion("$D$6")})'
    cell(sector,'A7:F9',formula='="Personas únicas: "&TEXT('+sector_metric(2)+',"#,##0")',role='question')
    cell(sector,'G7:L9',formula='="Completas: "&TEXT('+sector_metric(3)+',"#,##0")',role='question')
    for r,p in enumerate(('P1','P2','P3'),42):
        cell(sector,f'A{r}',p)
        for c,index in [('B',2),('C',3)]:
            terms=[f'IF($D$6={quoted(s)},{metric("Sector período",json.dumps([p,s],ensure_ascii=False),index)},0)' for s in sectors]
            cell(sector,f'{c}{r}',formula='+'.join(terms) or '0')
        cell(sector,f'D{r}',formula=f'IF(B{r}=0,"No aplica",C{r}/B{r})')
    chart(sector,'Participación del sector por período','A42:A44',[('Participación','D42:D44','#008577')],'A11','F25','percent')
    modes=sorted({r[3] for r in records})
    for r,mode in enumerate(modes,47):
        cell(sector,f'A{r}',mode)
        cell(sector,f'B{r}',formula=f'SUMIFS({base(17)},{base(2)},{criterion("$D$6")},{base(3)},{criterion(quoted(mode))})')
    if modes:
        chart(sector,'Matrículas por modalidad',f'A47:A{46+len(modes)}',[('Matrículas',f'B47:B{46+len(modes)}','#247BA0')],'G11','L25')
    heading(sector,27,'Carreras del sector: personas y participación')
    career_pairs=sorted({(r[2],r[5]) for r in records})
    sector_careers=spec('Carreras sector',['Sector','Carrera','Personas','Completas','Sin respuesta','Participación','Orden local'],
                       [[s,c]+[None]*5 for s,c in career_pairs],
                       'Personas únicas por sector y carrera, intersectadas con Filtros. El selector local no amplía la base.',[35,65,18,18,18,18,18])
    sector_careers['percent_columns']=[5]
    for i,(s,c) in enumerate(career_pairs,7):
        for dest,source in [('C',2),('D',3),('E',5),('F',6)]:
            sector_careers['formulas'][f'{dest}{i}']='='+metric('Sector carrera',json.dumps([s,c],ensure_ascii=False),source)
        sector_careers['formulas'][f'G{i}']=f'=IF(A{i}=\'Panel sectorial\'!$D$6,COUNTIF($A$7:A{i},A{i}),0)'
    max_careers=max([sum(s==sector for sector,_ in career_pairs) for s in sectors] or [1])
    career_end=max(7,len(career_pairs)+6)
    srows=[]
    for i in range(1,max_careers+1):
        pos=f'MATCH({i},{ref("Carreras sector",6,7,career_end)},0)'
        available=f'COUNTIF({ref("Carreras sector",0,7,career_end)},$D$6)>={i}'
        srows.append([f'=IF({available},INDEX({ref("Carreras sector",c,7,career_end)},{pos}),"")' for c in range(1,6)])
    # Helper rows start after all visible detail rows.
    shift=max(70,32+len(srows))
    for address in list(sector['cells']):
        number=int(''.join(filter(str.isdigit,address)))
        if number>=42:
            sector['cells'][address.rstrip('0123456789')+str(number+shift)]=sector['cells'].pop(address)
    for address in list(sector['formulas']):
        number=int(''.join(filter(str.isdigit,address)))
        if number>=42:
            formula=sector['formulas'].pop(address)
            formula=re.sub(r'\b([BCD])(4[2-4])\b',lambda m:m[1]+str(int(m[2])+shift),formula)
            sector['formulas'][address.rstrip('0123456789')+str(number+shift)]=formula
    for ch in sector['charts']:
        move=lambda value:re.sub(r'\d+',lambda m:str(int(m[0])+shift),value)
        ch['labels']=move(ch['labels'])
        ch['series']=[(name,move(address),color) for name,address,color in ch['series']]
    grid(sector,28,['Carrera','Personas','Completas','Sin respuesta','Participación'],[4,2,2,2,2],srows)
    sector['styles'].append([f'K29:L{max(29,28+len(srows))}','percent'])
    sector['last_row']=shift+47+len(modes)

    result=[executive,coverage,explorer,finance,performance,sector]
    for d in result:
        d['last_row']=max(d['last_row'], max([int(''.join(filter(str.isdigit,a))) for a in list(d['cells'])+list(d['formulas'])] or [38]))
    return result, [ranking,option_table,question_list,selector_index,sector_careers]


def expected_cells(model, selection=None):
    """Independent controls from records, not from the presentation formulas."""
    selection=selection or {}
    rows=[r for r in model['records'] if all(r[int(d)+1] in values for d,values in selection.items())]
    sectors=sorted({r[2] for r in model['records']})
    careers=sorted({r[5] for r in model['records']})
    def people(items):
        identities={r[7] for r in items}
        complete={r[7] for r in items if r[9]=='SI'}
        partial={r[7] for r in items if r[9]=='INCOMPLETO'}-complete
        return len(identities),len(complete),len(partial),len(identities-complete-partial)
    def rate(counts):
        return counts[1]/counts[0] if counts[0] else 'No aplica'
    controls=[]
    for p in (1,2,3):
        counts=people([r for r in rows if r[1]==f'P{p}'])
        controls.extend(('Panel ejecutivo',f'{c}{28+p}',value) for c,value in zip(('C','E','G','I','K'),[*counts,rate(counts)]))
    for i,s in enumerate(sectors):
        for p,c in [(1,'G'),(2,'I'),(3,'K')]:
            counts=people([r for r in rows if r[1]==f'P{p}' and r[2]==s])
            controls.append(('Cobertura',f'{c}{12+i}',rate(counts)))
    counts_by_career={c:people([r for r in rows if r[5]==c]) for c in careers}
    ordered=sorted(careers,key=lambda c:(-(counts_by_career[c][0]-counts_by_career[c][1]),c))
    for i,c in enumerate(ordered,34):
        n,complete,partial,missing=counts_by_career[c]
        controls.extend([('Cobertura',f'A{i}',c),('Cobertura',f'G{i}',n),
                         ('Cobertura',f'I{i}',n-complete),('Cobertura',f'K{i}',complete/n if n else 'No aplica')])
    grades=[r[11] for r in rows if r[11] is not None]
    distribution_row=41+len({(r[1],r[2],r[12]) for r in model['records']})
    bins=[sum(v<4 for v in grades),sum(4<=v<5 for v in grades),
          sum(5<=v<6 for v in grades),sum(6<=v<=7 for v in grades)]
    controls.extend(('Panel rendimiento',f'I{distribution_row+i}',value) for i,value in enumerate(bins))
    controls.extend([('Panel rendimiento','A7',sum(grades)/len(grades) if grades else 'Sin notas disponibles al corte'),
                     ('Panel rendimiento','D7',len(grades)),
                     ('Panel rendimiento','G7',len(grades)/len(rows) if rows else 'No aplica'),
                     ('Panel rendimiento','J7',len(rows)-len(grades))])
    for i,s in enumerate(sectors,29):
        selected=[r for r in rows if r[2]==s]
        grades=[r[11] for r in selected if r[11] is not None]
        controls.extend([('Panel rendimiento',f'E{i}',len(selected)),('Panel rendimiento',f'G{i}',len(grades)),
            ('Panel rendimiento',f'I{i}',sum(grades)/len(grades) if grades else 'Sin notas disponibles al corte'),
            ('Panel rendimiento',f'K{i}',len(grades)/len(selected) if selected else 'No aplica')])
    if sectors:
        for i,c in enumerate(sorted({r[5] for r in model['records'] if r[2]==sectors[0]}),29):
            counts=people([r for r in rows if r[2]==sectors[0] and r[5]==c])
            controls.extend([('Panel sectorial',f'E{i}',counts[0]),('Panel sectorial',f'G{i}',counts[1]),
                             ('Panel sectorial',f'I{i}',counts[3]),('Panel sectorial',f'K{i}',rate(counts))])
    return controls

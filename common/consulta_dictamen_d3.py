"""Consulta común de dictámenes D3, preservando íntegramente la respuesta C2."""
import copy,hashlib,json
from pathlib import Path
from common.diccionario_c2 import DiccionarioC2
DESCRIPTOR='data/validacion_d3/20261016/descriptor.json'
SHA_DESCRIPTOR='a891727123c4d23b09e5dfc1535d6d5600efce955acc1d5bfa4c8565f3f37893'

class ConsultaD3:
    def __init__(self, root=None):
        self.root=Path(root or Path(__file__).resolve().parents[1]).resolve()
        def read(name,digest):
            p=(self.root/name).resolve()
            if not p.is_relative_to(self.root):raise ValueError('Ruta externa rechazada')
            raw=p.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Integridad D3 rechazada: '+name)
            return raw
        descriptor=json.loads(read(DESCRIPTOR,SHA_DESCRIPTOR))
        components={name:read(name,digest) for name,digest in descriptor['archivos_sha256'].items()}
        engine=read('common/reglas_dictamen_d3.py',descriptor['motor_sha256'])
        scope={};exec(compile(engine,'common/reglas_dictamen_d3.py','exec'),scope);self.control=scope['control_variante']
        package=json.loads(components['data/validacion_d3/20261016/dictamenes.json'])
        self.contexts={r['contexto']:r for r in package['contextos']}
        self.bykey={r['clave']:r for r in package['contextos']}
        self.codes={r['id']:r for r in package['codigos_sies']}
        self.plans={r['id']:r for r in package['planes_umas']}
        self.cilog=package['incidencias_cilog']
        self.c2=DiccionarioC2(self.root)
        self.trace={'edicion':'D3_20261016','descriptor_sha256':SHA_DESCRIPTOR}

    def consultar(self, entrada, modelo):
        result=self.c2.consultar(entrada,modelo)
        key=self.c2.motor.clave(entrada,'K0')
        c=self.bykey.get(key)
        out={'c2':result,'dictamen_d3':copy.deepcopy(c),'control_variante':self.control(result['resultado']['estado']),
             'regla_control_variante':'D3-09','codigo_asignado':None,'habilitada_para_resolver':False,'trazabilidad_d3':dict(self.trace)}
        if c and c['contexto'] in self.cilog['contextos']:out['incidencia_agregada_cilog']=copy.deepcopy(self.cilog)
        return out

    def consultar_elemento(self, tipo, identificador):
        if not isinstance(identificador,str) or not identificador:raise ValueError('Identificador académico obligatorio')
        tables={'CONTEXTO':self.contexts,'CODIGO_SIES':self.codes,'PLAN_UMAS':self.plans}
        if tipo not in tables:raise ValueError('Tipo de consulta desconocido')
        r=tables[tipo].get(identificador)
        out={'tipo':tipo,'id':identificador,'resultado':copy.deepcopy(r),'estado':'ELEMENTO_LOCALIZADO' if r else 'SIN_ELEMENTO_EN_EDICION','trazabilidad_d3':dict(self.trace),'habilitada_para_resolver':False}
        if tipo=='CONTEXTO' and identificador in self.cilog['contextos']:out['incidencia_agregada_cilog']=copy.deepcopy(self.cilog)
        return out

    def consultar_lote(self, queries):
        if not isinstance(queries,list):raise ValueError('Lote debe ser lista')
        results=[]
        for q in queries:
            if not isinstance(q,dict):raise ValueError('Consulta debe ser objeto')
            if set(q)=={'modelo','entrada'}:results.append(self.consultar(q['entrada'],q['modelo']))
            elif set(q)=={'tipo','id'}:results.append(self.consultar_elemento(q['tipo'],q['id']))
            else:raise ValueError('Contrato: modelo/entrada o tipo/id; no recibe identificadores personales')
        return results

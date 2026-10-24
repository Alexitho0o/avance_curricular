"""Consulta académica B5 compartida por los módulos; no asigna identidades."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

DESCRIPTOR='data/consumo_comun_c2/20261016/descriptor.json'
SHA_DESCRIPTOR='fb83093e85483471417606fae13258002975e5adf3229000e6fe8444ffa520bf'

class DiccionarioC2:
    """Carga una edición íntegra y devuelve únicamente evidencia observada."""
    def __init__(self, root=None):
        self.root=Path(root or Path(__file__).resolve().parents[1]).resolve()
        def read(name, digest):
            path=(self.root/name).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError('Ruta fuera del repositorio')
            data=path.read_bytes()
            if hashlib.sha256(data).hexdigest()!=digest:
                raise ValueError('Integridad rechazada: '+name)
            return data
        descriptor=json.loads(read(DESCRIPTOR,SHA_DESCRIPTOR))
        contents={name:read(name,digest) for name,digest in descriptor['componentes_sha256'].items()}
        # Ejecutar exactamente los bytes verificados, sin depender de un módulo cacheado.
        self.motor=importlib.util.module_from_spec(importlib.util.spec_from_loader('_motor_b5_c2',loader=None))
        exec(compile(contents[descriptor['motor']],descriptor['motor'],'exec'),self.motor.__dict__)
        self.registro=json.loads(contents[descriptor['registro']])
        self.index={(r['modelo'],r['clave']):r for r in self.registro}
        if len(self.index)!=len(self.registro):raise ValueError('Claves duplicadas')
        self.traza={'edicion':descriptor['edicion'],'descriptor_sha256':SHA_DESCRIPTOR,
                    'registro_sha256':descriptor['componentes_sha256'][descriptor['registro']]}

    def consultar(self, entrada, modelo):
        if modelo not in self.motor.EXTRAS:raise ValueError('Modelo desconocido')
        if not isinstance(entrada,dict):raise ValueError('Entrada debe ser objeto académico')
        allowed=set(self.motor.BASE+self.motor.EXTRAS[modelo])
        if set(entrada)-allowed:raise ValueError('Campos ajenos al contrato del modelo')
        for field,value in entrada.items():
            if value is None or value=='' or value==[]:continue
            if field in ('anio','primera_observacion'):
                if type(value) is not int:raise ValueError('Año debe ser entero: '+field)
            elif field=='planes':
                if not isinstance(value,list) or not all(isinstance(v,str) and v for v in value):
                    raise ValueError('Planes debe ser lista de códigos')
                if value!=sorted(set(value)):raise ValueError('Planes deben ser únicos y ordenados')
            elif not isinstance(value,str):raise ValueError('Campo literal debe ser texto: '+field)
        result=copy.deepcopy(self.motor.consultar(self.registro,entrada,modelo))
        row=self.index.get((modelo,self.motor.clave(entrada,modelo)))
        return {'resultado':result,'evidencia':copy.deepcopy(row),'trazabilidad':dict(self.traza)}

    def consultar_lote(self, consultas):
        if not isinstance(consultas,list):raise ValueError('Lote debe ser lista')
        output=[]
        for q in consultas:
            if not isinstance(q,dict) or set(q)!={'modelo','entrada'}:
                raise ValueError('Cada consulta exige modelo y entrada')
            output.append(self.consultar(q['entrada'],q['modelo']))
        return output

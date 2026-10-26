"""Lector CFB de solo lectura para mensajes de respaldo; no ejecuta adjuntos."""
from pathlib import Path
import struct
class CFB:
 def __init__(self,p):
  self.b=Path(p).read_bytes();assert self.b[:8]==bytes.fromhex('d0cf11e0a1b11ae1');self.ss=1<<struct.unpack_from('<H',self.b,30)[0];self.ms=1<<struct.unpack_from('<H',self.b,32)[0]
  fatids=list(struct.unpack_from('<109I',self.b,76));n=struct.unpack_from('<I',self.b,44)[0];d=struct.unpack_from('<I',self.b,68)[0]
  while d<0xfffffffa:
   sec=self.sector(d);nums=struct.unpack('<%dI'%(self.ss//4),sec);fatids+=list(nums[:-1]);d=nums[-1]
  self.fat=[]
  for s in fatids[:n]:self.fat+=list(struct.unpack('<%dI'%(self.ss//4),self.sector(s)))
  dirs=self.chain(struct.unpack_from('<I',self.b,48)[0],self.fat,self.sector);self.entries=[]
  for i in range(0,len(dirs),128):
   raw=dirs[i:i+128];length=struct.unpack_from('<H',raw,64)[0];typ=raw[66]
   if typ: self.entries.append({'name':raw[:max(length-2,0)].decode('utf-16le',errors='replace'),'typ':typ,'start':struct.unpack_from('<I',raw,116)[0],'size':struct.unpack_from('<Q',raw,120)[0]})
  root=next(x for x in self.entries if x['typ']==5);self.mini=self.chain(root['start'],self.fat,self.sector)[:root['size']]
  mf=self.chain(struct.unpack_from('<I',self.b,60)[0],self.fat,self.sector);self.mf=list(struct.unpack('<%dI'%(len(mf)//4),mf)) if mf else []
 def sector(self,s):return self.b[(s+1)*self.ss:(s+2)*self.ss]
 def chain(self,s,fat,get):
  out=b'';seen=set()
  while s<0xfffffffa:
   assert s not in seen;seen.add(s);out+=get(s);s=fat[s]
  return out
 def stream(self,entry):
  if entry['size']<4096:return self.chain(entry['start'],self.mf,lambda s:self.mini[s*self.ms:(s+1)*self.ms])[:entry['size']]
  return self.chain(entry['start'],self.fat,self.sector)[:entry['size']]
 def texts(self):
  out={}
  for e in self.entries:
   if e['typ']==2 and e['name'] in ['__substg1.0_1000001F','__substg1.0_1000001E','__substg1.0_0037001F','__substg1.0_0037001E','__substg1.0_007D001F','__substg1.0_007D001E']:
    out[e['name']]=self.stream(e).decode('utf-16le' if e['name'].endswith('001F') else 'cp1252',errors='replace')
  return out
if __name__=='__main__':
 import json,re
 paths=json.loads(Path('/tmp/e04_antecedentes_inventario.json').read_text())['paths']
 for p in paths:
  if Path(p).suffix=='.msg' and ('/Matricula/' in p or '/2025/Oferta academica/' in p):
   txt=CFB(p).texts();body=next((t for k,t in txt.items() if k.startswith('__substg1.0_1000')),'');print(Path(p).name,'longitud',len(body));lines=body.splitlines()
   for i,line in enumerate(lines,1):
    if any(s in line.upper() for s in ['VERSI','IINF','INFORMÁTICA','INFORMATICA','PRECARGA','16 DE ABRIL','16-04-2025','PLAN DE ESTUDIO']):
     line=re.sub(r'\b[0-9.]{7,12}-[0-9Kk]\b','[identificador]',line);print(i,line[:400])

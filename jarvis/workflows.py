"""Restricted, deterministic tabular workflows. Paths require caller authorization."""
import csv
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import uuid
import zipfile
from concurrent.futures import CancelledError
from contextlib import contextmanager

MAX_BYTES = 25 * 1024 * 1024
MAX_ROWS = 100000


def validate(definition):
    if not isinstance(definition, dict) or set(definition) - {'schema_version','steps','formula_policy'}:
        raise ValueError('Unknown workflow fields')
    if type(definition.get('schema_version')) is not int or definition['schema_version'] != 1:
        raise ValueError('Expected schema_version 1')
    if definition.get('formula_policy', 'escape') not in ('escape','reject'):
        raise ValueError('Formula policy must be escape or reject')
    steps = definition.get('steps')
    if not isinstance(steps,list) or len(steps)>100: raise ValueError('Expected at most 100 steps')
    for step in steps:
        if not isinstance(step,dict): raise ValueError('Invalid step')
        op=step.get('op')
        if op=='rename':
            mapping=step.get('mapping')
            if set(step)!={'op','mapping'} or not isinstance(mapping,dict) or not mapping:
                raise ValueError('rename requires mapping')
            _names(list(mapping)); _names(list(mapping.values()))
        elif op in ('select','strip','upper','lower','drop_blank','drop_duplicates','sort'):
            if set(step)-({'op','columns','descending'} if op=='sort' else {'op','columns'}):
                raise ValueError('Unknown step field')
            _names(step.get('columns'))
            if 'descending' in step and type(step['descending']) is not bool: raise ValueError('descending must be boolean')
        else: raise ValueError('Unsupported operation')
    return json.loads(json.dumps(definition))


def _names(names):
    if not isinstance(names,list) or not names or len(names)>1024 or any(not isinstance(x,str) or not x or len(x)>256 for x in names) or len(set(names))!=len(names):
        raise ValueError('Columns must be unique, nonempty strings')


def _path(value):
    path=Path(value)
    if not path.is_absolute() or '..' in path.parts or str(path).startswith(('\\\\','//')):
        raise ValueError('An absolute local path without traversal is required')
    for part in (path,*path.parents):
        if part.is_symlink() or (hasattr(part,'is_junction') and part.is_junction()):
            raise ValueError('Symlinks and junctions are not permitted')
    # Reject NTFS alternate data streams and Win32 device names.
    for part in path.parts[1:]:
        if ':' in part or part.rstrip(' .')!=part or part.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(10)],*[f'LPT{i}' for i in range(10)]}:
            raise ValueError('Unsafe Windows path')
    return path.resolve()


def _check(cancel):
    if cancel is not None and cancel.is_set(): raise CancelledError('Cancelled')


def _read(path,cancel=None):
    if path.stat().st_size>MAX_BYTES: raise ValueError('Input exceeds 25 MiB limit')
    if path.suffix.lower()=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.reader(f); headers=next(reader,[]); _names(headers)
            rows=[]
            for row in reader:
                _check(cancel)
                if len(row)!=len(headers): raise ValueError('Inconsistent CSV row width')
                rows.append(row)
                if len(rows)>MAX_ROWS: raise ValueError('Input exceeds 100000 rows')
    elif path.suffix.lower()=='.xlsx':
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist())>100*1024*1024: raise ValueError('Workbook expanded size exceeds limit')
        from openpyxl import load_workbook
        book=load_workbook(path,read_only=True,data_only=False,keep_links=False)
        try:
            reader=book.active.iter_rows(values_only=True); headers=list(next(reader,())); _names(headers)
            rows=[]
            for row in reader:
                _check(cancel); rows.append(list(row))
                if len(rows)>MAX_ROWS: raise ValueError('Input exceeds 100000 rows')
        finally: book.close()
    else: raise ValueError('Only .csv and .xlsx supported')
    return headers,rows


def _transform(headers,rows,definition,cancel=None):
    headers=list(headers); rows=[list(r) for r in rows]
    for step in definition['steps']:
        _check(cancel); op=step['op']
        names=list(step['mapping']) if op=='rename' else step['columns']
        if any(n not in headers for n in names): raise ValueError('Workflow references missing columns')
        indices=[headers.index(n) for n in names]
        if op=='rename':
            headers=[step['mapping'].get(h,h) for h in headers]; _names(headers)
        elif op=='select': headers=names; rows=[[r[i] for i in indices] for r in rows]
        elif op in ('strip','upper','lower'):
            for row in rows:
                _check(cancel)
                for i in indices:
                    if row[i] is None: continue
                    if not isinstance(row[i],str): raise ValueError('String operation on non-text cell')
                    row[i]=getattr(row[i],op)()
        elif op=='drop_blank': rows=[r for r in rows if all(r[i] is not None and str(r[i]).strip() for i in indices)]
        elif op=='drop_duplicates':
            seen=set(); unique=[]
            for row in rows:
                _check(cancel); key=tuple((type(row[i]).__name__,row[i]) for i in indices)
                if key not in seen: seen.add(key); unique.append(row)
            rows=unique
        elif op=='sort':
            # Explicit type check avoids numeric/string comparison or silent coercion.
            for i in indices:
                if len({type(r[i]) for r in rows if r[i] is not None})>1: raise ValueError('Mixed types cannot be sorted')
            rows.sort(key=lambda r:tuple((r[i] is not None,r[i]) for i in indices),reverse=step.get('descending',False))
    return headers,rows


def _publish(temp,destination):
    # Hard-link publication is atomic and never replaces an existing name, on NTFS and POSIX.
    os.link(temp,destination)


def execute(definition,input_path,output_path,cancel=None):
    definition=validate(definition); src=_path(input_path); dst=_path(output_path)
    if src==dst: raise ValueError('Output must differ from original')
    if dst.exists(): raise FileExistsError(str(dst))
    if dst.suffix.lower() not in ('.csv','.xlsx'): raise ValueError('Output must be CSV or XLSX')
    _check(cancel)
    headers,rows=_read(src,cancel); headers,rows=_transform(headers,rows,definition,cancel)
    escaped=0
    def safe(value):
        nonlocal escaped
        if isinstance(value,str) and value.lstrip(' \t\r\n').startswith(('=','+','-','@')):
            if definition.get('formula_policy','escape')=='reject': raise ValueError('Potential spreadsheet formula rejected')
            escaped+=1; return "'"+value
        return value
    headers=[safe(h) for h in headers]; rows=[[safe(v) for v in row] for row in rows]
    fd,temp=tempfile.mkstemp(prefix='.jarvis-',suffix=dst.suffix,dir=dst.parent); os.close(fd)
    try:
        if dst.suffix.lower()=='.csv':
            with open(temp,'w',encoding='utf-8',newline='') as f:
                writer=csv.writer(f,lineterminator='\n'); writer.writerow(headers)
                for row in rows: _check(cancel); writer.writerow(row)
                f.flush(); os.fsync(f.fileno())
        else:
            from openpyxl import Workbook
            book=Workbook(write_only=True); sheet=book.create_sheet('Data'); sheet.append(headers)
            for row in rows: _check(cancel); sheet.append(row)
            book.save(temp); book.close()
        _check(cancel); _path(dst); _publish(temp,dst)
    finally:
        Path(temp).unlink(missing_ok=True)
    return {'output_path':str(dst),'rows':len(rows),'columns':headers,'escaped_cells':escaped}


def infer_csv(input_path,expected_path):
    ih,ir=_read(_path(input_path)); oh,orr=_read(_path(expected_path))
    if not ir or len(ir)!=len(orr): raise ValueError('Inference requires nonempty examples with equal row counts')
    if any(isinstance(v,str) and v.lstrip(' \t\r\n').startswith(('=','+','-','@')) for row in [oh,*orr] for v in row):
        raise ValueError('Expected output contains spreadsheet formula prefixes that safe export must escape')
    candidates=[]
    for out_index,name in enumerate(oh):
        matches=[]
        for in_index,source in enumerate(ih):
            # Prefer same-name columns; different names require unique matching evidence.
            if name in ih and source!=name: continue
            for ops in ((),('strip',),('upper',),('lower',),('strip','upper'),('strip','lower')):
                values=[r[in_index] for r in ir]
                if any(not isinstance(v,str) for v in values): continue
                effective=True
                for op in ops:
                    after=[getattr(v,op)() for v in values]
                    if after==values: effective=False
                    values=after
                if effective and values==[r[out_index] for r in orr]: matches.append((source,ops))
        if len(matches)!=1: raise ValueError('Examples are ambiguous or outside supported inference; specify rules explicitly')
        candidates.append(matches[0])
    if len({x[0] for x in candidates})!=len(candidates): raise ValueError('One source maps to multiple outputs')
    steps=[]
    for source,ops in candidates:
        steps.extend({'op':op,'columns':[source]} for op in ops)
    selected=[x[0] for x in candidates]
    if selected!=ih: steps.append({'op':'select','columns':selected})
    mapping={source:name for (source,_),name in zip(candidates,oh) if source!=name}
    if mapping: steps.append({'op':'rename','mapping':mapping})
    definition={'schema_version':1,'steps':steps}
    if _transform(ih,ir,definition)!=(oh,orr): raise ValueError('Candidate failed exact validation')
    return definition


class SkillLibrary:
    def __init__(self,profile_dir):
        Path(profile_dir).mkdir(parents=True,exist_ok=True); self.path=Path(profile_dir)/'workflows.sqlite3'
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS skills (id TEXT PRIMARY KEY, name TEXT, description TEXT, definition TEXT, version INTEGER, enabled INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS versions (id TEXT, version INTEGER, name TEXT, description TEXT, definition TEXT, PRIMARY KEY(id,version))')

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10); db.row_factory=sqlite3.Row
        try:
            with db: yield db
        finally: db.close()

    @staticmethod
    def _decode(row):
        result=dict(row); result['definition']=json.loads(result['definition'])
        if 'enabled' in result: result['enabled']=bool(result['enabled'])
        return result

    def list(self):
        with self._db() as db: return [self._decode(r) for r in db.execute('SELECT * FROM skills ORDER BY name')]

    def get(self,skill_id):
        with self._db() as db: row=db.execute('SELECT * FROM skills WHERE id=?',(skill_id,)).fetchone()
        if row is None: raise KeyError(skill_id)
        return self._decode(row)

    def save(self,name,description,definition,skill_id=None):
        return self._save(name,description,definition,skill_id,True)

    def _save(self,name,description,definition,skill_id,enabled):
        definition=validate(definition)
        if not isinstance(name,str) or not name.strip() or len(name)>200 or not isinstance(description,str) or len(description)>10000: raise ValueError('Invalid skill metadata')
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT version FROM skills WHERE id=?',(skill_id,)).fetchone() if skill_id else None
            if skill_id and old is None: raise KeyError(skill_id)
            version=old[0]+1 if old else 1; sid=skill_id or uuid.uuid4().hex
            payload=json.dumps(definition)
            db.execute('INSERT OR REPLACE INTO skills VALUES(?,?,?,?,?,?)',(sid,name,description,payload,version,0 if old else int(enabled)))
            db.execute('INSERT INTO versions VALUES(?,?,?,?,?)',(sid,version,name,description,payload))
        return self.get(sid)

    def delete(self,skill_id):
        with self._db() as db:
            db.execute('DELETE FROM skills WHERE id=?',(skill_id,)); db.execute('DELETE FROM versions WHERE id=?',(skill_id,))

    def set_enabled(self,skill_id,enabled):
        if type(enabled) is not bool: raise ValueError('enabled must be boolean')
        self.get(skill_id)
        with self._db() as db: db.execute('UPDATE skills SET enabled=? WHERE id=?',(int(enabled),skill_id))

    def versions(self,skill_id):
        with self._db() as db: return [self._decode(r) for r in db.execute('SELECT * FROM versions WHERE id=? ORDER BY version',(skill_id,))]

    def rollback(self,skill_id,version):
        matches=[v for v in self.versions(skill_id) if v['version']==version]
        if not matches: raise KeyError(version)
        v=matches[0]; return self.save(v['name'],v['description'],v['definition'],skill_id)

    def export_skill(self,skill_id,path):
        skill=self.get(skill_id); out={k:skill[k] for k in ('name','description','definition')}
        destination=_path(path)
        with destination.open('x',encoding='utf-8') as f: json.dump(out,f,indent=2)

    def import_skill(self,path):
        path=_path(path)
        if path.stat().st_size>1024*1024: raise ValueError('Skill package too large')
        try: data=json.loads(path.read_text(encoding='utf-8'))
        except (UnicodeError,json.JSONDecodeError) as e: raise ValueError('Invalid JSON skill package') from e
        if not isinstance(data,dict) or set(data)!={'name','description','definition'}: raise ValueError('Invalid skill package fields')
        return self._save(data['name'],data['description'],data['definition'],None,False)

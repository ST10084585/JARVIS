import json
import threading
import time
from datetime import datetime, timedelta, timezone

import pytest

from jarvis.workflows import SkillLibrary, execute, infer_csv, CancelledError
from jarvis.jobs import JobManager, Scheduler


def definition(*steps):
    return {"schema_version": 1, "steps": list(steps)}


def test_safe_transforms_and_collision(tmp_path):
    src = tmp_path / 'in.csv'; dst = tmp_path / 'out.csv'
    src.write_text('Name,Other\n b ,x\n a ,y\n a ,y\n', encoding='utf-8')
    d = definition({'op':'strip','columns':['Name']}, {'op':'upper','columns':['Name']},
                   {'op':'drop_duplicates','columns':['Name']}, {'op':'sort','columns':['Name']},
                   {'op':'select','columns':['Name']}, {'op':'rename','mapping':{'Name':'Person'}})
    result = execute(d, src, dst)
    assert dst.read_text() == 'Person\nA\nB\n'
    assert result['rows'] == 2
    with pytest.raises(FileExistsError): execute(d, src, dst)
    with pytest.raises(ValueError): execute(d, src, src)
    assert src.read_text().startswith('Name,Other')


def test_cancel_and_formula_protection(tmp_path):
    src = tmp_path / 'a.csv'; dst = tmp_path / 'b.csv'
    src.write_text('Name\n=SUM(1)\n')
    cancel = threading.Event(); cancel.set()
    with pytest.raises(CancelledError): execute(definition(), src, dst, cancel)
    assert not dst.exists()
    assert execute(definition(), src, dst)['escaped_cells'] == 1
    assert "'=SUM(1)" in dst.read_text()
    dst.unlink()
    with pytest.raises(ValueError): execute({**definition(), 'formula_policy':'reject'}, src, dst)
    assert not dst.exists()


@pytest.mark.parametrize('bad', [ {'steps':[{'op':'shell','command':'calc'}]},
    {'schema_version':1,'steps':[], 'output_path':'../escape'},
    {'schema_version':1,'steps':[{'op':'sort','columns':'name'}]},
    {'schema_version':True,'steps':[]}, {'schema_version':1,'steps':[], 'formula_policy':'allow'}])
def test_bad_imports_rejected(tmp_path, bad):
    p=tmp_path/'bad.json'; p.write_text(json.dumps({'name':'bad','description':'','definition':bad}))
    with pytest.raises(ValueError): SkillLibrary(tmp_path/'profile').import_skill(p)


def test_skill_versions_import_disabled(tmp_path):
    lib=SkillLibrary(tmp_path/'profile')
    item=lib.save('Formatter','description',definition())
    lib.save('Formatter','v2',definition({'op':'strip','columns':['Name']}),item['id'])
    assert len(lib.versions(item['id']))==2
    assert lib.rollback(item['id'],1)['definition']==definition()
    lib.export_skill(item['id'],tmp_path/'skill.json')
    imported=lib.import_skill(tmp_path/'skill.json')
    assert not imported['enabled']
    lib.set_enabled(imported['id'],True)
    assert SkillLibrary(tmp_path/'profile').get(imported['id'])['enabled']
    lib.delete(imported['id'])
    with pytest.raises(KeyError): lib.get(imported['id'])


def test_parent_path_rejected(tmp_path):
    src=tmp_path/'a.csv'; src.write_text('A\nx\n')
    with pytest.raises(ValueError): execute(definition(),src,tmp_path/'..'/'escape.csv')


def test_inference_exact_and_ambiguous(tmp_path):
    src=tmp_path/'a.csv'; expected=tmp_path/'b.csv'
    src.write_text('Name\n alice \nBob\n'); expected.write_text('Name\nALICE\nBOB\n')
    inferred=infer_csv(src,expected)
    execute(inferred,src,tmp_path/'out.csv')
    assert (tmp_path/'out.csv').read_text()==expected.read_text()
    src.write_text('A,B\nx,x\ny,y\n'); expected.write_text('Renamed\nx\ny\n')
    with pytest.raises(ValueError): infer_csv(src,expected)


def wait_job(jobs,jid):
    end=time.monotonic()+5
    while time.monotonic()<end:
        row=next(x for x in jobs.list() if x['id']==jid)
        if row['status'] not in ('queued','running'): return row
        time.sleep(.02)
    raise AssertionError('Job did not finish')


def test_jobs_pause_cancel_and_persistence(tmp_path):
    jobs=JobManager(tmp_path); jobs.pause()
    jid=jobs.submit('cancel me',lambda c,p: {'wrong':True})
    jobs.cancel(jid); jobs.resume()
    assert wait_job(jobs,jid)['status']=='cancelled'
    jid=jobs.submit('good',lambda c,p: {'answer':42})
    assert wait_job(jobs,jid)['result']=={'answer':42}
    jobs.shutdown()
    restarted=JobManager(tmp_path)
    assert next(x for x in restarted.list() if x['id']==jid)['result']=={'answer':42}
    restarted.shutdown()


def test_scheduler_coalesces_and_persists(tmp_path):
    jobs=JobManager(tmp_path)
    s=Scheduler(tmp_path,jobs)
    s.add('Water', (datetime.now(timezone.utc)-timedelta(hours=2)).isoformat(),60)
    s.tick(); s.tick()
    assert len(s.notifications)==1
    restarted=Scheduler(tmp_path,jobs); restarted.tick()
    assert restarted.notifications==[]
    with pytest.raises(ValueError): s.add('Unsafe',datetime.now(timezone.utc).isoformat(),skill_id='skill')
    jobs.shutdown()


def test_excel_types_and_safe_output(tmp_path):
    from openpyxl import Workbook, load_workbook
    src=tmp_path/'input.xlsx'; out=tmp_path/'out.xlsx'
    book=Workbook(); book.active.append(['Name','Count']); book.active.append(['=1+1',12]); book.save(src); book.close()
    with pytest.raises(ValueError): execute(definition({'op':'upper','columns':['Count']}),src,out)
    assert not out.exists()
    execute(definition(),src,out)
    book=load_workbook(out,data_only=False)
    assert book.active['A2'].value=="'=1+1"
    assert book.active['A2'].data_type=='s'
    assert book.active['B2'].value==12
    book.close()


def test_running_job_cooperative_cancel(tmp_path):
    jobs=JobManager(tmp_path); started=threading.Event()
    def run(cancel,progress):
        started.set(); cancel.wait(3)
        if cancel.is_set(): raise CancelledError()
    jid=jobs.submit('long',run)
    assert started.wait(5)
    jobs.cancel(jid)
    assert wait_job(jobs,jid)['status']=='cancelled'
    jobs.shutdown()


def test_import_never_transiently_enabled(tmp_path):
    lib=SkillLibrary(tmp_path/'profile'); package=tmp_path/'safe.json'
    package.write_text(json.dumps({'name':'imported','description':'','definition':definition()}))
    # Intercept review mutator to prove import does not briefly create enabled skills.
    lib.set_enabled=lambda *args: (_ for _ in ()).throw(AssertionError('Import must insert disabled atomically'))
    imported=lib.import_skill(package)
    assert not imported['enabled']


def test_inference_rejects_export_that_would_change_expected(tmp_path):
    src=tmp_path/'in.csv'; expected=tmp_path/'expected.csv'
    src.write_text('A\n=1+1\n'); expected.write_text('A\n=1+1\n')
    with pytest.raises(ValueError): infer_csv(src,expected)


def test_concurrent_outputs_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    src=tmp_path/'in.csv'; out=tmp_path/'out.csv'; src.write_text('A\none\n')
    barrier=threading.Barrier(2)
    def run():
        barrier.wait()
        try: execute(definition(),src,out); return 'created'
        except FileExistsError: return 'exists'
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(run); second=pool.submit(run)
        assert sorted([first.result(),second.result()])==['created','exists']
    assert out.read_text()=='A\none\n'
    assert list(tmp_path.glob('.jarvis-*'))==[]


def test_interrupted_job_never_replays(tmp_path):
    import sqlite3
    jobs=JobManager(tmp_path); jobs.shutdown()
    with sqlite3.connect(tmp_path/'jobs.sqlite3') as db:
        db.execute("INSERT INTO jobs VALUES('crashed','old','running',20,NULL,NULL,1)")
    restarted=JobManager(tmp_path)
    assert restarted.list()[0]['status']=='interrupted'
    restarted.shutdown()

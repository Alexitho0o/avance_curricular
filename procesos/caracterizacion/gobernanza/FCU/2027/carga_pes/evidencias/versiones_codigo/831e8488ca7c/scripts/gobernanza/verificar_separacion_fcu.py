"""Read-only checks for the frozen 2026 reference and the independent 2027 process."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'gobernanza/FCU/2027/carga_pes/json/REFERENCIA_2026_CONGELADA.json'
PROTECTED_ROOTS = [ROOT / 'gobernanza/FCU/2026', ROOT / 'outputs/fcu_2026_p1_cierre',
                   ROOT / 'docs/cierre_fcu_2026_p1', ROOT / 'archive/backups_caracterizacion_20260505']


def verify_frozen_reference(baseline=BASELINE, root=ROOT):
    data = json.loads(Path(baseline).read_text())
    issues = []
    for item in data['files']:
        path = Path(root) / item['path']
        if not path.is_file():
            issues.append({'path':item['path'], 'issue':'FROZEN_REFERENCE_MISSING'})
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            issues.append({'path':item['path'], 'issue':'FROZEN_REFERENCE_CHANGED'})
    return {'ok':not issues,'checked_files':len(data['files']),'issues':issues,
            'baseline_sha256':hashlib.sha256(Path(baseline).read_bytes()).hexdigest()}


def assert_2027_output_path(path, protected_roots=PROTECTED_ROOTS, protected_files=None):
    output = Path(path).resolve()
    for root in protected_roots:
        root = Path(root).resolve()
        if output == root or root in output.parents:
            raise ValueError('FCU 2027 cannot write inside a frozen 2026 process')
    if protected_files is None:
        data = json.loads(BASELINE.read_text())
        protected_files = [ROOT / item['path'] for item in data['files']]
    if output in {Path(p).resolve() for p in protected_files}:
        raise ValueError('FCU 2027 cannot overwrite a frozen reference file')
    return output


def assert_frozen_reference(baseline=BASELINE):
    result = verify_frozen_reference(baseline)
    if not result['ok']:
        raise ValueError('Frozen 2026 reference changed or missing; do not silently reset the baseline')
    return result


def assert_private_output_path(path, root=ROOT):
    output, root = Path(path).resolve(), Path(root).resolve()
    if output == root or root in output.parents:
        probe = output / 'FCU_2027_BORRADOR_privacy_probe.csv'
        ignored = subprocess.run(['git','check-ignore','--quiet','--',str(probe)],cwd=root,check=False)
        if ignored.returncode != 0:
            raise ValueError('Student-level outputs must use an ignored local directory or an external workspace, not publishable governance folders')
    return output


if __name__ == '__main__':
    result = verify_frozen_reference()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['ok'] else 1)

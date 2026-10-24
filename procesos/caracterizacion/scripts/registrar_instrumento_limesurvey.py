"""Archive a generated instrument with portable paths and verifiable SHA-256 hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from exportar_instrumento_limesurvey import ROOT, check_frozen_reference, check_profile, parse_exports, workbook_tables

ARCHIVE = ROOT / 'gobernanza/instrumentos_limesurvey'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_package(package):
    package = Path(package)
    manifest = json.loads((package / 'manifest.json').read_text())
    actual = {str(p.relative_to(package)) for p in package.rglob('*') if p.is_file()}
    if actual != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Contenido del paquete distinto del manifiesto.')
    for relative, digest in manifest['files'].items():
        path = (package / relative).resolve()
        if package.resolve() not in path.parents or sha256(path) != digest:
            raise ValueError('Hash de paquete incorrecto: ' + relative)
    payload = json.loads((package / 'inventory.json').read_text())
    if payload['tables'] != workbook_tables(payload['instrument']):
        raise ValueError('Tablas no corresponden al modelo del instrumento.')
    instrument = payload['instrument']
    questions = [q for g in instrument['groups'] for q in g['questions']]
    counts = {'groups': len(instrument['groups']), 'questions': len(questions),
              'subquestions': sum(len(q['subquestions']) for q in questions),
              'explicit_options': sum(len(q['options']) for q in questions)}
    if counts != manifest['counts']:
        raise ValueError('Totales del manifiesto no corresponden al instrumento.')
    parsed = parse_exports([package / s['path'] for s in instrument['sources']], instrument['language'])
    if parsed['groups'] != instrument['groups']:
        raise ValueError('Modelo no corresponde a los XML originales.')
    return manifest


def register_package(evidence, workbook, archive=ARCHIVE):
    check_frozen_reference()
    evidence, workbook, archive = Path(evidence), Path(workbook), Path(archive)
    original = json.loads((evidence / 'manifest.json').read_text())
    payload = json.loads((evidence / 'inventory.json').read_text())
    instrument = payload['instrument']
    profile = (instrument['year'], instrument['period'], instrument['survey_id'])
    if profile != (original['year'], original['period'], original['survey_id']):
        raise ValueError('Perfil del modelo no corresponde al manifiesto.')
    check_profile(profile[2], profile[0], profile[1])
    registry_path = archive / 'REGISTRO.json'
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else {
        'instruments': [{'year': 2026, 'period': 1, 'survey_id': None, 'status': 'PENDIENTE_FUENTES', 'versions': []}]}
    entry = next((e for e in registry['instruments'] if (e['year'], e['period']) == profile[:2]), None)
    if entry and entry.get('survey_id') and entry['survey_id'] != profile[2]:
        raise ValueError('Otra encuesta ya registrada para este ano/periodo.')
    if sha256(workbook) != original['sha256']:
        raise ValueError('El Excel no corresponde a la entrega original.')
    digest = hashlib.sha256(''.join(sorted(s['sha256'] for s in instrument['sources'])).encode()).hexdigest()[:12]
    destination = archive / str(profile[0]) / f'P{profile[1]}' / f'{profile[2]}_{original["date"]}_{digest}'
    if destination.exists():
        prior = verify_package(destination)
        if prior['output_sha256'] != original['sha256']:
            raise ValueError('La version ya existe con otro Excel. No sobrescribir.')
        return destination
    archive.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.registro_', dir=archive) as temp:
        temp = Path(temp)
        (temp / 'fuentes').mkdir()
        for source in instrument['sources']:
            source_path = evidence / 'fuentes' / source['filename']
            if sha256(source_path) != source['sha256']:
                raise ValueError('Fuente diferente de la utilizada en el inventario.')
            target = temp / 'fuentes' / source['filename']
            shutil.copy2(source_path, target)
            source.clear()
            source.update(filename=target.name, path='fuentes/' + target.name, sha256=sha256(target))
        (temp / 'inventory.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        (temp / 'excel').mkdir()
        shutil.copy2(workbook, temp / 'excel' / workbook.name)
        (temp / 'versiones_codigo').mkdir()
        for script_path, digest_code in original['scripts'].items():
            source = evidence / 'versiones_codigo' / Path(script_path).name
            if sha256(source) != digest_code:
                raise ValueError('Version del generador distinta de la utilizada.')
            shutil.copy2(source, temp / 'versiones_codigo' / source.name)
        for name in ['previews', 'export_inspect.ndjson']:
            source = evidence / name
            if source.is_dir():
                shutil.copytree(source, temp / name)
            elif source.exists():
                shutil.copy2(source, temp / name)
        manifest = {'year': profile[0], 'period': profile[1], 'survey_id': profile[2],
                    'recorded_on': original['date'], 'counts': original['counts'],
                    'output': 'excel/' + workbook.name, 'output_sha256': original['sha256'],
                    'status': 'INVENTARIO_ARCHIVADO',
                    'scope': 'Definiciones del instrumento, no respuestas ni datos de estudiantes. No modifica cierre FCU 2026.',
                    'reproduction': 'Ejecutar exportar_instrumento_limesurvey.py con --archivos fuentes/*.lsg y el ano/periodo registrado. El modelo portable permite construir el Excel directamente con el builder MJS archivado y Artifact Tool. Igualdad de contenido no implica identidad binaria de XLSX regenerados.',
                    'files': {str(p.relative_to(temp)): sha256(p) for p in sorted(temp.rglob('*')) if p.is_file()}}
        (temp / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        verify_package(temp)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temp), destination)
    if entry is None:
        entry = {'year': profile[0], 'period': profile[1], 'survey_id': profile[2], 'versions': []}
        registry['instruments'].append(entry)
    entry.update(survey_id=profile[2], status='INVENTARIO_ARCHIVADO')
    version = str(destination.relative_to(archive))
    if version not in entry['versions']:
        entry['versions'].append(version)
    registry['instruments'].sort(key=lambda e: (e['year'], e['period']))
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    check_frozen_reference()
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidencia', type=Path)
    parser.add_argument('--excel', type=Path)
    parser.add_argument('--verificar', type=Path)
    args = parser.parse_args()
    if args.verificar:
        print(json.dumps(verify_package(args.verificar), ensure_ascii=False, indent=2))
    elif args.evidencia and args.excel:
        print(register_package(args.evidencia, args.excel))
    else:
        parser.error('Usar --evidencia + --excel, o --verificar.')


if __name__ == '__main__':
    main()

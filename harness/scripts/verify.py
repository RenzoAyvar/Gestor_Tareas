#!/usr/bin/env python3
"""Harness verificable sin librerías externas: SPEC -> backend -> frontend -> reporte."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = ROOT / 'specs/001-login'
REQUIRED = ['spec.md', 'contract.md', 'plan.md', 'tasks.md', 'traceability.json']


def check_spec():
    failures = []
    for f in REQUIRED:
        if not (SPEC_DIR / f).is_file():
            failures.append(f'Falta especificación: {f}')
    if failures:
        return failures
    contents = (SPEC_DIR / 'spec.md').read_text(encoding='utf-8')
    try:
        traceability = json.loads((SPEC_DIR / 'traceability.json').read_text(encoding='utf-8'))
    except (ValueError, OSError) as exc:
        return [f'Trazabilidad no válida: {exc}']
    for i in range(1, 8):
        key = f'AC-{i:03d}'
        if key not in contents:
            failures.append(f'{key} no está en spec.md')
        refs = traceability.get(key, [])
        if not isinstance(refs, list) or len(refs) < 1:
            failures.append(f'{key} sin referencia de test')
            continue
        for ref in refs:
            file = ref.split('::', 1)[0]
            if not (ROOT / file).is_file():
                failures.append(f'{key} apunta a archivo inexistente: {file}')
    return failures


def run_command(command, cwd):
    start = time.monotonic()
    try:
        code = subprocess.run(command, cwd=cwd, check=False).returncode
        return {'command': ' '.join(command), 'exit_code': code, 'seconds': round(time.monotonic()-start, 2)}
    except FileNotFoundError as exc:
        return {'command': ' '.join(command), 'exit_code': 127, 'blocked': str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scope', choices=('spec', 'frontend', 'backend', 'all'), default='all')
    args = parser.parse_args()
    results = {'scope': args.scope, 'checks': []}
    failures = check_spec()
    results['checks'].append({'name': 'SPEC + trazabilidad', 'ok': not failures, 'details': failures})
    if failures:
        print('G0 falló:', *failures, sep='\n- ')
    if args.scope in ('backend', 'all'):
        results['checks'].append({'name': 'backend pytest', **run_command([sys.executable, '-m', 'pytest', '-q'], ROOT/'backend')})
    if args.scope in ('frontend', 'all'):
        results['checks'].append({'name': 'frontend vitest', **run_command(['npm', 'run', 'test'], ROOT/'frontend')})
        results['checks'].append({'name': 'frontend build', **run_command(['npm', 'run', 'build'], ROOT/'frontend')})
    success = all(c.get('ok', c.get('exit_code') == 0) for c in results['checks'])
    results['status'] = 'APROBADO' if success else 'RECHAZADO/BLOQUEADO'
    report = ROOT / 'harness/reports/last-run.json'
    report.parent.mkdir(exist_ok=True, parents=True)
    report.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    for check in results['checks']:
        print(check['name'], ':', 'OK' if check.get('ok', check.get('exit_code') == 0) else 'FAIL/BLOCKED')
    print('Harness:', results['status'], '|', report.relative_to(ROOT))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())

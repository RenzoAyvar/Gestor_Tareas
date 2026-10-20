#!/usr/bin/env python3
"""Harness verificable sin librerías externas: SPEC modular -> backend -> frontend."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_MODULES = (
    ('auth', 'login.scps', tuple(f'AC-{i:03d}' for i in range(1, 8))),
    ('tasks', 'minitask.scps', tuple(f'MT-{i:03d}' for i in range(1, 8))),
)


def check_spec():
    failures = []
    for module, spec_name, criteria in SPEC_MODULES:
        module_dir = ROOT / 'specs' / module
        spec_file = module_dir / spec_name
        trace_file = module_dir / 'traceability.json'
        if not spec_file.is_file():
            failures.append(f'Falta especificación: specs/{module}/{spec_name}')
            continue
        if not trace_file.is_file():
            failures.append(f'Falta trazabilidad: specs/{module}/traceability.json')
            continue
        contents = spec_file.read_text(encoding='utf-8')
        if len(contents.splitlines()) > 150:
            failures.append(f'{spec_file.relative_to(ROOT)} supera 150 líneas')
        try:
            traceability = json.loads(trace_file.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            failures.append(f'Trazabilidad no válida en {module}: {exc}')
            continue
        for key in criteria:
            if key not in contents:
                failures.append(f'{key} no está en {spec_name}')
            refs = traceability.get(key, [])
            if not isinstance(refs, list) or not refs:
                failures.append(f'{key} sin referencia de test')
                continue
            for ref in refs:
                file, _, scenario = ref.partition('::')
                test_file = ROOT / file
                if not test_file.is_file():
                    failures.append(f'{key} apunta a archivo inexistente: {file}')
                elif scenario and scenario not in test_file.read_text(encoding='utf-8'):
                    failures.append(f'{key} apunta a escenario inexistente: {ref}')
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

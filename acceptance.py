"""Самоперевірка за наперед записаними еталонами ЛР4 (без сторонніх пакетів)."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def load_cases(path=None):
    data = json.loads(Path(path or ROOT / 'acceptance_cases.json').read_text(encoding='utf-8'))
    ids = [c['id'] for c in data['cases']]
    if len(ids) != len(set(ids)):
        raise ValueError('Ідентифікатори прикладів мають бути унікальними.')
    return data


def compare(actual, expected):
    return all(actual[key] == expected[key] for key in ('stdout', 'stderr', 'exit_code'))


def run_case(case, command):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    with tempfile.TemporaryDirectory(prefix='frequency-case-') as folder:
        for name, content in case.get('files_hex', {}).items():
            path = Path(folder) / name
            if path.parent != Path(folder):
                raise ValueError('Тестові файли мають лежати в корені тимчасової папки.')
            path.write_bytes(bytes.fromhex(content))
        completed = subprocess.run(
            command + case.get('args', []), input=case.get('stdin', ''),
            text=True, encoding='utf-8', capture_output=True, cwd=folder,
            env=env, timeout=30, check=False,
        )
    actual = {'stdout': completed.stdout, 'stderr': completed.stderr,
              'exit_code': completed.returncode}
    return {'id': case['id'], 'name': case['name'],
            'input': case['input_description'], 'expected': case['expected'],
            'actual': actual, 'passed': compare(actual, case['expected'])}


def main(argv=None):
    # Redirected Windows stdout may otherwise use cp1251, which lacks arrows.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path, help='Перевірити зібраний EXE замість main.py')
    parser.add_argument('--json', type=Path, dest='json_path', help='Зберегти точні результати JSON')
    args = parser.parse_args(argv)
    command = ([str(args.executable.resolve())] if args.executable
               else [sys.executable, str(ROOT / 'main.py')])
    results = [run_case(c, command) for c in load_cases()['cases']]
    for result in results:
        print(f"{'ЗБІГ' if result['passed'] else 'ПОМИЛКА'} {result['id']}: {result['name']}")
        print('Вхід:', result['input'])
        print('Очікується:', json.dumps(result['expected'], ensure_ascii=False))
        print('Фактично:', json.dumps(result['actual'], ensure_ascii=False))
    passed = sum(r['passed'] for r in results)
    payload = {'command': command, 'passed': passed, 'failed': len(results) - passed,
               'total': len(results), 'results': results}
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Пройшло {passed} з {len(results)}; не пройшло {len(results) - passed}.")
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())

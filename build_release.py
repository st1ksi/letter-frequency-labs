"""Зібрати автономний консольний випуск для Windows x64 за поточним VERSION.

Запускати Python із середовища, у якому встановлено build-requirements.txt.
Скрипт фіксує версії інструментів, вхідні файли та контрольні суми.
Побайтова ідентичність EXE між окремими збираннями не гарантується.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if version != '1.0.0':
        raise SystemExit('Цей випуск ЛР4 потребує VERSION 1.0.0 перед збиранням.')
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise SystemExit('Потрібні Windows x64 та Python x64.')
    if platform.architecture()[0] != '64bit':
        raise SystemExit('Потрібен саме 64-бітний Python.')
    name = f'letter-frequency-{version}-windows-x64'
    work = ROOT / 'build' / 'release'
    out = ROOT / 'dist'
    package = out / name
    work.mkdir(parents=True, exist_ok=True)
    package.mkdir(parents=True, exist_ok=True)
    hook = work / 'utf8_streams.py'
    hook.write_text(
        'import sys\n'
        'for stream in (sys.stdin, sys.stdout, sys.stderr):\n'
        '    if stream is not None and hasattr(stream, "reconfigure"):\n'
        '        stream.reconfigure(encoding="utf-8")\n', encoding='utf-8')
    parts = tuple(int(x) for x in version.split('.')) + (0,)
    resources = work / 'version_info.txt'
    resources.write_text(
        f"VSVersionInfo(ffi=FixedFileInfo(filevers={parts!r}, prodvers={parts!r}, "
        "mask=0x3f, flags=0, OS=0x40004, fileType=0x1, subtype=0, date=(0,0)), "
        "kids=[StringFileInfo([StringTable('040904B0', ["
        "StringStruct('CompanyName','Andrii Kononov'),"
        "StringStruct('FileDescription','Letter frequency console analyzer'),"
        f"StringStruct('FileVersion','{version}'),"
        f"StringStruct('ProductVersion','{version}'),"
        "StringStruct('ProductName','Letter Frequency'),"
        "StringStruct('OriginalFilename','letter-frequency.exe')])]),"
        "VarFileInfo([VarStruct('Translation',[1033,1200])])])", encoding='utf-8')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
               '--onefile', '--console', '--noupx', '--optimize', '1',
               '--name', 'letter-frequency', '--paths', str(ROOT),
               '--specpath', str(work), '--workpath', str(work / 'pyinstaller'),
               '--distpath', str(package), '--runtime-hook', str(hook),
               '--version-file', str(resources), str(ROOT / 'main.py')]
    subprocess.run(command, cwd=ROOT, check=True)
    licenses = package / 'LICENSES'
    licenses.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'LICENSE', licenses / 'PROJECT-zlib.txt')
    shutil.copy2(ROOT / 'LICENSES' / 'zanalyze-zlib.txt', licenses / 'zanalyze-zlib.txt')
    python_license = Path(sys.base_prefix) / 'LICENSE.txt'
    shutil.copy2(python_license, licenses / 'Python-LICENSE.txt')
    pyi_dist = importlib.metadata.distribution('pyinstaller')
    pyi_license = next(pyi_dist.locate_file(f) for f in pyi_dist.files
                       if str(f).replace('\\', '/').endswith('/COPYING.txt'))
    shutil.copy2(pyi_license, licenses / 'PyInstaller-COPYING.txt')
    (package / 'sample.txt').write_text('Аааа Бб! 123\n', encoding='utf-8')
    (package / 'empty.txt').write_bytes(b'')
    (package / 'VERSION').write_text(version + '\n', encoding='ascii')
    (package / 'Run.cmd').write_bytes(
        b'@echo off\r\nchcp 65001 >nul\r\ncd /d "%~dp0"\r\n'
        b'letter-frequency.exe\r\npause\r\n')
    (package / 'README.txt').write_text(f'''Частотний аналіз літер {version} — Windows x64

Призначення: частоти літер і пропорційна консольна діаграма.
Розпакуйте весь ZIP у звичайну папку. Python та IDE не потрібні.
Для інтерактивного вводу двічі відкрийте Run.cmd (вікно залишиться після результату).
Або відкрийте термінал у цій папці й виконайте:
  .\\letter-frequency.exe
  .\\letter-frequency.exe --file sample.txt
  .\\letter-frequency.exe --file sample.txt --min-count 2 --chart-style blocks
  .\\letter-frequency.exe --file empty.txt

Файли мають бути UTF-8 (BOM допускається). Великі й малі літери об'єднуються;
цифри та розділові знаки пропускаються. Поріг включний, має бути цілим >=1.
Стиль ascii — типовий; найдовший стовпчик має 50 символів, половини вгору.
Код завершення 0 — успіх, 2 — діагностика вводу. Порожній файл — помилка з поясненням.
У перенаправлених stdin/stdout/stderr використовується UTF-8.

Перший запуск onefile розпаковує runtime у тимчасову папку. Потрібні права
запису до звичайного TEMP; права адміністратора не потрібні. Збірка не підписана.
Платформа: Windows x64. На інших ОС цей EXE не запускається.
Перевірка на окремому ПК не заявляється; виконано ізольований запуск на цьому ПК.

Код та історія: https://github.com/st1ksi/letter-frequency-labs
Сторінка: https://st1ksi.github.io/letter-frequency-labs/
Власні внески: zlib; стороння діаграма zanalyze: zlib, Hans Kristian Rosbach.
Участь OpenAI Codex та попереднє використання Antigravity розкрито в репозиторії.
EXE містить CPython та bootloader PyInstaller: тексти умов у LICENSES.
PyInstaller дозволяє поширювати отриманий bundle під умовами застосунку
за дотримання умов залежностей; його bootloader exception наведено в COPYING.
''', encoding='utf-8')
    inputs = {str(f.relative_to(ROOT)).replace('\\', '/'): digest(f)
              for f in [ROOT / 'main.py', ROOT / 'scaling.py', ROOT / 'vendor/zanalyze_histogram.py',
                        ROOT / 'VERSION', Path(__file__).resolve()]}
    manifest = {'version': version, 'platform': platform.platform(),
                'python': sys.version, 'configuration': 'Release; console; onefile; no debug; no UPX; optimize=1',
                'pyinstaller': importlib.metadata.version('pyinstaller'),
                'build_packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
                'command': command, 'input_sha256': inputs,
                'files': {str(f.relative_to(package)).replace('\\', '/'): digest(f)
                          for f in sorted(package.rglob('*')) if f.is_file()}}
    (package / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive = out / (name + '.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(package.rglob('*')):
            if f.is_file():
                info = zipfile.ZipInfo(str(Path(name) / f.relative_to(package)).replace('\\', '/'),
                                       (2026, 11, 12, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, f.read_bytes())
    (out / (archive.name + '.sha256')).write_text(digest(archive) + '  ' + archive.name + '\n', encoding='ascii')
    print(json.dumps({'zip': str(archive), 'bytes': archive.stat().st_size, 'sha256': digest(archive),
                      'exe': str(package / 'letter-frequency.exe')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

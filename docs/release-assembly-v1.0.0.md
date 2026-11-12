# Final assembly of the Windows v1.0.0 artifact

Application source: tag `v1.0.0`, commit `1ee38ee642fee9e9b682a0417aa993b4327d7115`.
The source tag and EXE were not changed during this final notice assembly.
The recipe in tagged `build_release.py` builds the EXE and base ZIP. Its last archive
step is not the full final-release assembly: the bundled OpenSSL runtime notices
must be added before distributing that ZIP. This document records that extra step.
Do not describe the tagged builder alone as a one-command complete release recipe.

## Build the application

Use Windows x64, CPython 3.12.14 x64 and the versions pinned in build-requirements.txt.
Install build requirements in a separate build environment, then execute:

    python build_release.py

This uses PyInstaller 6.22.3, console/onefile, no debug bootloader, no UPX,
optimization 1, and a packaging-only UTF-8 stream hook. Tool paths and input hashes
are recorded in BUILD-MANIFEST.json. Byte-identical rebuilds are not guaranteed.

## Assemble runtime notices

1. Verify the OpenSSL version of the CPython used for the build with
   `python -c "import ssl; print(ssl.OPENSSL_VERSION)"`. For this artifact it is
   `OpenSSL 3.5.8 25 Aug 2026`; libcrypto DLL version metadata also says 3.5.8.
2. Download the complete unmodified files below into the expanded package LICENSES:
   - https://raw.githubusercontent.com/openssl/openssl/openssl-3.5.8/LICENSE.txt
     saved as OpenSSL-3.5.8-LICENSE.txt;
   - https://raw.githubusercontent.com/openssl/openssl/openssl-3.5.8/README.md
     saved as OpenSSL-3.5.8-README.md.
3. Preserve the attribution in OpenSSL-3.5.8-COPYRIGHT.txt supplied with this archive;
   it identifies its source and is explicitly a package-authored notice. For another
   OpenSSL version, inventory that runtime and use its matching notices instead.
4. Include this SOURCE-BUILD-NOTICES.md. Recreate BUILD-MANIFEST.json's files mapping
   using SHA256 of every final package file EXCEPT BUILD-MANIFEST.json itself. Keep
   the source input hashes and add the runtime-notice sources/hashes. Otherwise a
   second build may preserve a stale self-hash of the previous manifest.
5. Recreate letter-frequency-1.0.0-windows-x64.zip from the final expanded folder,
   with that single top-level folder, all paths slash-separated and ZIP timestamps
   2026-11-12 00:00:00. Write the new ZIP SHA256 to its .zip.sha256 sidecar.
6. Extract the final ZIP into a new empty directory, remove Python variables, limit
   PATH to Windows system directories, then run normal/blocks/empty-file checks and
   the ten static acceptance cases against that EXE. Check all output channels and
   exit codes. A same-machine isolation test is not a second-PC compatibility test.

## Inventory

The onefile executable contains CPython and its collected runtime modules,
libcrypto from OpenSSL, and the PyInstaller bootloader. The application contains
the original zlib-licensed contributions and zanalyze's zlib-licensed renderer.
The LICENSES folder carries project, zanalyze, Python, PyInstaller and OpenSSL texts.
No executable code was altered when the missing OpenSSL notices were added.

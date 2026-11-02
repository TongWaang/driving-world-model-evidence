"""Create a deterministic release ZIP and file-integrity manifest."""
from pathlib import Path
import hashlib,zipfile

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_DIRS={'data','docs','scripts','tests','reports'}
ALLOWED_ROOT_FILES={'README.md','.gitignore'}

def release_files():
    output=[]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        relative=path.relative_to(ROOT)
        if '__pycache__' in relative.parts or path.suffix in {'.pyc','.pyo'}:
            continue
        if relative.parts[0] in ALLOWED_DIRS or relative.as_posix() in ALLOWED_ROOT_FILES:
            output.append(path)
    return output

def main():
    files=release_files()
    if not (ROOT/'docs'/'S1.pdf').exists():
        raise SystemExit('Generate and inspect S1.pdf before packaging')
    manifest=ROOT/'SHA256SUMS'
    manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8')
    files.append(manifest)
    output=ROOT.parent/'driving-world-model-evidence-v1.0.0.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files):
            relative=path.relative_to(ROOT).as_posix()
            info=zipfile.ZipInfo('driving-world-model-evidence/'+relative,date_time=(2026,11,2,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            archive.writestr(info,path.read_bytes())
    print(f'{output}\n{len(files)} files\nSHA256 {hashlib.sha256(output.read_bytes()).hexdigest()}')

if __name__=='__main__':
    main()

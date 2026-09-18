# tools/check_routing_docs.py

## 계층과 책임

문서 검증 — 클라이언트 범위에서 파일·문서·색인·시그니처의 일치를 검사한다.

원문: `Game-client/tools/check_routing_docs.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from pathlib import Path
import ast
import os
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 ROOT ← Path(__file__).resolve().parents[1]
설정 EXCLUDED ← {'.venv', '__pycache__', '.git', 'docs'}
```

## client_files()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 result ← []
반복 (directory, folders, files) ← os.walk(ROOT):
  설정 folders[:] ← [name for name in folders if name not in EXCLUDED]
  반복 name ← files:
    조건 name.endswith(('.pyc', '.pyo', '.log')) 이면:
      다음 반복으로
    실행 result.append((Path(directory) / name).relative_to(ROOT))
반환 sorted(result)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(Path(directory) / name).relative_to
Path
name.endswith
os.walk
result.append
sorted
```

## signatures(tree, prefix='')

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `tree`: 호출자가 전달하는 `tree`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `prefix`: 호출자가 전달하는 `prefix`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 node ← tree.body:
  조건 isinstance(node, ast.ClassDef) 이면:
    실행 (yield from signatures(node, prefix + node.name + '.'))
  그 외:
    조건 isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) 이면:
      설정 name ← prefix + node.name
      실행 (yield (name + '(' + ast.unparse(node.args) + ')'))
      실행 (yield from signatures(node, name + '.'))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ast.unparse
isinstance
signatures
```

## main()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 routing ← ROOT / 'docs' / 'client-routing'
설정 index ← (routing / 'README.md').read_text(encoding='utf-8')
설정 files ← client_files()
설정 expected ← {path.as_posix() + '.md' for path in files}
설정 actual ← {path.relative_to(routing / 'files').as_posix() for path in (routing / 'files').rglob('*.md')}
설정 errors ← ['missing: ' + name for name in sorted(expected - actual)]
갱신 errors += ['orphan: ' + name for name in sorted(actual - expected)]
반복 path ← files:
  설정 document ← routing / 'files' / (path.as_posix() + '.md')
  조건 not document.exists() 이면:
    다음 반복으로
  조건 'files/' + path.as_posix() + '.md' not in index 이면:
    실행 errors.append('not indexed: ' + path.as_posix())
  조건 path.suffix == '.py' 이면:
    설정 contents ← document.read_text(encoding='utf-8')
    설정 tree ← ast.parse((ROOT / path).read_text(encoding='utf-8'))
    반복 signature ← signatures(tree):
      조건 signature not in contents 이면:
        실행 errors.append('signature missing: ' + path.as_posix() + ': ' + signature)
조건 errors 이면:
  실패 전달 SystemExit('\n'.join(errors))
실행 print(f'OK: {len(files)} client files, {len(actual)} paired documents; signatures and index match.')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
'\n'.join
(ROOT / path).read_text
(routing / 'README.md').read_text
(routing / 'files').rglob
SystemExit
ast.parse
client_files
document.exists
document.read_text
errors.append
len
path.as_posix
path.relative_to
path.relative_to(routing / 'files').as_posix
print
signatures
sorted
```

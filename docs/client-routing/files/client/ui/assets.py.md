# client/ui/assets.py

## 책임과 상태

메인 스레드에서 로컬 font/image를 한 번 로드한다. asset root는 `client/ui/assets.py`의 두 단계 부모와 `config.assets_dir`에서 온다.

## 메서드

`AssetStore.__init__(self, config)`

```text
메인 thread assert
NotoSans font 13/15/17/20/26/32 로드, 실패 시 system font와 notice
grass/path/tree/house/hero PNG decode·32px scale, 실패 시 notice
```

직접 호출: `pygame.font.Font/SysFont`, `pygame.image.load`, `pygame.transform.scale`, `Path`.

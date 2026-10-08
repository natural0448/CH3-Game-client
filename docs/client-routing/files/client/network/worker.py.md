# client/network/worker.py

## 22일차·23일차2교시 교안기준 최종 구현

NetworkWorker는 기존 하나의 thread/loop/AuthSession 위에 AdGateway를 구성한다. ad 요청은 start로 별도 async task, busy는 correlated error event. 로그인 성공 identity 전달, 계정 변경/로그아웃/종료에서 gateway close. 이미지 URL은 게임 origin만 접속한다. Pygame import를 추가하지 않는다. 기존 WS/action/query routing은 유지한다. 23일차사건kind를AdGateway.start_event로연결한다. busy/거부는교안의ad_event_error와원래slot/player/request/decision/type으로반환해pending이남지않는다. 기존로그아웃은ad/query/play/auth close로session을정리하며교안의인증해제를현재구조에적응한다.

클래스계약: `class NetworkWorker`.

### `NetworkWorker.__init__(self, config)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| config | 없음 | load_config의 공개 설정 dict; 계정/매체키 없음. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `AuthSession`, `float`, `queue.Queue`, `threading.Thread`, `threading.Event`, `config.get`, `ValueError`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker.start(self)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self.thread.start`, `RuntimeError`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker.submit(self, request)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: 실제반환식: `False`, `True`.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self._stop.is_set`, `self.requests.put_nowait`, `dict`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker.drain_events(self, limit=200)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| limit | `200` | drain_events최대건수;음수는0. |

반환·실패: 실제반환식: `result`.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `range`, `max`, `result.append`, `self.events.get_nowait`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker.is_alive(self)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: 실제반환식: `self.thread.is_alive()`.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self.thread.is_alive`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker.stop(self, timeout=None)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| timeout | `None` | join시간초또는None. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self._stop.set`, `self.thread.join`, `self.loop.is_closed`, `self.loop.call_soon_threadsafe`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker._emit(self, kind, **data)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| kind | 없음 | 기존queue/조회/의도허용종류문자열. |
| data | 없음 | 요청/조회 public dict 또는 Django POST mapping; 파일 책임의 필드·타입 범위 참조. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self.events.put`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker._thread_main(self)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `asyncio.run`, `self._emit`, `self._run`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker._run(self)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `asyncio.get_running_loop`, `asyncio.current_task`, `PlayChannel`, `QueryGateway`, `AdGateway`, `self._stop.is_set`, `self.ads.close`, `self.queries.close`, `self.play.close`, `self.auth.close`, `self.play.check_timeout`, `self.requests.get_nowait`, `request.get`, `request.clear`, `self.requests.get_nowait().clear`, `self._emit`, `asyncio.sleep`, `self._login`, `self._logout`, `self.play.send_command`, `self.queries.start`, `self.ads.start`, `self.ads.start_event`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker._login(self, request)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self._emit`, `request.pop`, `self.ads.close`, `self.queries.close`, `self.play.close`, `self.auth.close`, `self.queries.set_identity`, `self.ads.set_identity`, `self.play.start`, `self.auth.login`, `str`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

### `NetworkWorker._logout(self)`

| 파라미터 | 기본값 | 의미·허용범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 파일책임의입력/소유상태확인→아래직접호출→기존결과또는상태전달.

직접호출: `self._emit`, `self.queries.invalidate`, `self.ads.close`, `self.play.close`, `self.auth.logout`, `self.queries.close`, `self.auth.close`. 호출결과는위반환·상태에사용하며하위내부구현은그짝문서가설명한다.

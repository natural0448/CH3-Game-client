# client/application/state.py

## 책임과 상태 출처

Pygame 타입 없이 입력 초안·화면 상태와 renderer용 불변 표시 DTO를 정의한다. mutable 값은 Controller만 쓴다.

## 타입과 변수

```text
LoginDraft: username='', password='', focus='username'
ApplicationState: phase='signed_out', message, closing/stopped, API 화면과 최근 WS 문구
LoginView/ApplicationView/GameView/QueryView/ScreenModel: Controller가 프레임마다 복사해 만드는 frozen DTO; QueryView는 page와 windows용 filter_value도 전달하고 can_request는 busy와 최소 간격에서 계산
```

## 메서드

`LoginDraft.clear(self)`

```text
username·password를 빈 문자열로 만들고 focus를 None으로 설정
```

`ApplicationState.remember_ws(self, message)`

```text
message를 추가하고 최근 3개만 유지
```

`ApplicationState.clear_account(self)`

```text
LoginDraft.clear 호출
API 표시·scroll·최근 WS 목록 초기화
```

파라미터 값은 Controller의 intent/event에서 온다. 외부 서비스 호출은 없다.

## 22일차 이미지 광고 최종 반영

기존 frozen ScreenModel에 ads:Mapping=field(default_factory=dict)를 추가한다. 기존 호출자의 app/game/queries만 있는 생성도 호환된다. 광고 뷰는 Controller가 공급하고 UI가 읽으며 비밀 키는 포함하지 않는다.

클래스 계약: `class LoginDraft`, `class ApplicationState`, `class LoginView`, `class ApplicationView`, `class GameView`, `class QueryView`, `class ScreenModel`.


### `LoginDraft.clear(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `ApplicationState.remember_ws(self, message)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| message | 없음 | 기존 message 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.ws_messages.append`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `ApplicationState.clear_account(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.login.clear`, `self.ws_messages.clear`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

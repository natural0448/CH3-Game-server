# Game-client

Python 3.12와 pygame-ce, aiohttp로 실행하는 작은 마을 접속기다. 서버 계약과 게임 규칙은 변경하지 않으며, 클라이언트는 서버가 확정한 state와 snapshot만 화면에 반영한다.

## 실행

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client\main.py --check
.\.venv\Scripts\python.exe client\main.py
```

`--check`는 설정과 의존성만 확인하며 서버에 연결하지 않는다.

## 구조

- `client/application`: 사용자 의도, 조회 상관관계, 읽기 전용 화면 모델
- `client/model`: 서버가 확정한 플레이어·방·명령 상태
- `client/contracts`: HTTP와 WebSocket 응답 검증 및 허용 필드
- `client/network`: 단일 worker의 세션, HTTP, WebSocket, 조회 작업
- `client/ui`: 메인 스레드 입력, Layout, Pygame 표시, 마을 장면
- `tests`: 서버를 켜지 않고 실행하는 계약·상태·표시 회귀 검사

행동 통계는 사용자가 버튼을 눌렀을 때만 같은 인증 세션으로 `GET /api/analytics/actions/`를 호출한다. Spark 작업 실행이나 Kafka 연결을 요청하지 않는다.

## 검사

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe tools\check_routing_docs.py
```

에셋의 라이선스와 출처는 `assets/README.md`와 `assets/sources/`를 따른다.

## 수정23일차 v2.3 · 3교시를 현재 구조에서 진행하기

교안은 client/messages.py·ads_panel.py·network_api.py처럼 한 폴더에 모인 구조다. 현재 프로젝트는 같은 역할을 contracts/application/network/ui로 분리했다. 아래 현재 파일·함수에서 확인하면 된다. main.py 실행 경로는 동일하다.

| 교안 파일/역할 | 현재 파일 | 확인 함수·상태 |
|---|---|---|
| client/messages.py · Request/Result | client/contracts/messages.py | 기존 dict queue의 decision_id/event_type/ad_event/needs_login/event_rejected |
| client/ports.py · 패널/API 계약 | client/application/ads.py, client/network/session.py, client/network/port.py | AdView/AdSlot, AuthSession, 기존 NetworkPort |
| client/network_api.py · post_ad_event/거절 | client/network/session.py, client/network/http.py | AuthSession.post_ad_event, AdEventRejected, JsonHttpClient.request_json |
| client/network.py · 사건 task | client/network/worker.py, client/network/ads.py | NetworkWorker._run, AdGateway.start_event/fetch_event/close |
| client/controller.py | client/application/controller.py | Controller.request_ad_event/confirm_ad_display/handle_network_event |
| client/ads_panel.py | client/application/ads.py | AdSlot.reset_events/request_event/accept_event/can_request, AdStore.mark_displayed |
| client/client_app.py · 표시 후 전송/마우스 | client/app.py, client/ui/input.py | run의 render 이후 confirm_ad_display, InputRouter.route의 ad_click |
| client/render_ads.py · 카드 표시 | client/ui/ads.py, client/ui/renderer.py | AdsRenderer.draw, ScreenRenderer.render의 display.flip 이후 receipt |
| tests/test_day23_ads_events.py | tests/test_ads_events.py | 사건/오류/재시도/표시/세션 회귀검사 |
| tests/test_ads_client.py | tests/test_ads_feature.py | 표시 후10초 유지·노출 확인 뒤 다음 선택 검사 |
| game/test_day23_ad_events.py | ../Game-server/server/game/test_ads.py | 기존 게임 Player·CSRF·사건 중계 검사 |

이번 시간의 기본 확인 대상은 **로그인 후 마을 게시판(village-board)** 광고다. 로비 카드는 기존 표시를 유지한다. 마을 게시판의 실제 표시·flip 뒤에 노출을 전송하며 서버 응답이 성공한 다음 클릭할 수 있다. 다운로드 성공이나 광고주 웹 조회는 노출이 아니다.

아래부터 실행한다. 기존 Pygame 창이 켜져 있다면 닫고 새 코드로 다시 실행한다. 프로젝트별 가상환경의 python을 직접 지정하므로 다른 폴더의 활성 가상환경과 혼동하지 않는다.

```powershell
Set-Location C:\MLO01-01\Chapter3\ad_server
.\.venv\Scripts\python.exe config/day23-period-03.py
Set-Location C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client/main.py
```

기초 파일은 교안 CODE28 그대로이며 False 다음 True가 출력된다. 광고/게임 서버는 기존8001/8000을 사용한다. 서버가 꺼져 있다면 각 기존 가상환경에서 광고 ad_config/manage.py, 게임 server/manage.py를 실행한다. 게임의 기존 HTTP·WS 운영 명령을 유지한다.

1. 접속기에서 기존 게임 계정으로 로그인하고 마을 게시판 광고 이미지가 실제 표시되는지 확인한다.
2. 카드에 **노출 완료**가 표시되면 광고주 웹 http://127.0.0.1:8001/advertiser/events/에서 기존 광고 계정으로 로그인한다. 카드의 결정 ID와 같은 행에 노출 시각이 생겼는지 확인한다.
3. 게임의 **광고 이미지/카드 영역**을 클릭한다. 새로 보기 버튼은 광고 클릭이 아니다.
4. **클릭 완료**를 확인하고 웹을 새로고침하여 같은 결정 행의 클릭 시각을 확인한다. 확인된 클릭은 재전송하지 않으므로 다시 클릭해도 최초 시각이 유지된다.
5. 서버 로그에서 POST /api/ads/events/200과 POST /api/media/events/200을 대조한다. 필요하면 Compass의 기존 village_ads.ad_events에서 그 결정 ID의 impression/click을 확인한다. shell에서 subject·결정 ID를 만들어 사건을 저장하지 않는다.

빈 광고/이미지 실패는 사건을 보내지 않는다.503·timeout은 같은 결정으로2초 뒤 다시 전송한다(클릭도 실제 클릭을 기억하고 다음 표시 프레임에서 재시도).400·403·404는 사건 재시도를 중지하고2초 뒤 새 광고 선택을 허용하며 카드에 **광고 새 요청 필요**를 표시한다.401/302는 기존 세션 정리 후 게임 재로그인이 필요하다. 새 결정/로그아웃에는 상태를 초기화하고 늦은 이전 결과를 무시한다.

새 선택은15초 요청 간격·실제 첫 표시 뒤10초 유지·노출 저장 확인·전송 중 상태를 검사한다. 마을 카드 클릭이 아직 성공하지 않았다면 같은 결정을 유지한다. 표시된 광고는 조건을 만족한 다음 자동 갱신되므로 웹에서는 같은 결정 ID 행을 대조한다. 숨겨진 조회 패널이나 최소화 상태에서는 새 노출·클릭을 만들지 않는다.

검사는 기존 테스트 파일 이름으로 실행한다.

```powershell
Set-Location C:\MLO01-01\Chapter3\Game-client
$env:SDL_VIDEODRIVER = 'dummy'
$env:SDL_AUDIODRIVER = 'dummy'
.\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

SDL dummy는 테스트용이다. 실제 게임을 같은 터미널에서 실행할 때는 먼저 아래 두 환경변수를 제거한다.

```powershell
Remove-Item Env:SDL_VIDEODRIVER -ErrorAction SilentlyContinue
Remove-Item Env:SDL_AUDIODRIVER -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe client/main.py
```

57개 접속기 테스트와 격리 HTTP/PNG/Pygame/광고주 실적 연결 검사가 통과했다. 증거는 ../ad_server/docs/server-routing/verification/day23-period03/다. 실제 학생 창의 표시·클릭 관찰은 not_run이며 수업에서는 위 순서대로 별도로 확인한다.

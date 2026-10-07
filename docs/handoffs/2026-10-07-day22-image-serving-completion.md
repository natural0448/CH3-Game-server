# 2026-10-07 · Game-server 22일차 광고 이미지 연결

상세 인수인계: [광고 집행 보완](../../../ad_server/docs/handoffs/2026-10-07-day22-image-serving-completion.md).

작업 시작 Git: clean; 4f75c2d; staged/unstaged/untracked 없음. 기존 사용자 변경 없음. 현재 개발 변경은 이번 요청에서 추가/수정한 아래 파일이며 commit/stage하지 않았다. 비밀값을 기록하지 않는다.

## 변경 개발 파일

- modified: `config/settings.py`
- modified: `server/game/urls.py`
- added: `server/game/ad_gateway.py`
- added: `server/game/ad_views.py`
- added: `server/game/static/game/ad_preview.js`
- added: `server/game/templates/game/ad_preview.html`
- added: `server/game/static/ads/creatives/forest-tools.png`
- added: `server/game/static/ads/creatives/camp-tea.png`
- added: `server/game/test_ads.py`
- added: `data/evidence/asset-sources.md`

## 검증과 문서

게임 relay·gateway5개 및 기존 history3개 memory SQLite 테스트 성공. 실제 MySQL 쓰기 없음. ADS_MEDIA_KEY 전달은 자동 승인 거부로 대기하며 server/.env hash 보존.

변경 개발 파일의 짝 문서와 server-routing/README.md를 최종 코드에 맞췄다. routing-doc-auditor issue0. 

실제 수업용 키 연결 승인 후 서버를 재시작하고 광고주 웹에서 소재를 선택·저장해야 한다. 임시 fixture의 전체 HTTP/PNG/Chrome/SDL 통합 검증은 성공했으나 실제 수업 관찰값으로 쓰지 않는다. 실행 명령과 남은23일차 events.py 사항은 상세 인수인계 참조.

## 후속 키 연결 상태

사용자 명시 승인으로 ADS_MEDIA_KEY만 게임 서버 로컬 환경에 복사·저장했다. 다른 기존 설정과 광고 서버 원본은 보존했다. --noreload로 동작하던8000 게임 개발 서버를 재시작했고 인증·설정 검사와 HTTP200 확인을 마쳤다.15초 이후 접속기의 새로 보기로 실제 게임 요청을 확인한다. 키 값은 기록하지 않는다. 상세 승인/프로세스/검증 기록은 광고 집행 인수인계의 후속 승인 절 참조.

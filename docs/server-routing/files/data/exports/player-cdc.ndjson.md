# data/exports/player-cdc.ndjson

현재 존재하는 24일차 공개 Player snapshot 데이터 파일의 1:1 문서다. 사용자가 생성한 원본을 server/data/exports에서 기존 루트 data/exports로 이동한 결과이며 bytes는 수정하지 않았다. 생산 코드는 `server/game/management/commands/export_player_snapshot.py`다. 함수·클래스·메서드·코드 상수는 없다.

## 실제 파일과 계약

- 현재 경로: `C:/MLO01-01/Chapter3/Game-server/data/exports/player-cdc.ndjson`.
- 관찰값: 56행, UTF-8 NDJSON, 13,275 bytes. 행 수는 이 수집본의 관찰 결과이지 고정 Player 수가 아니다.
- SHA-256: `6ea30948a1c6924b186676511207bd2099683ca00cf1b1582cb595e6437375d0`.
- 각 행의 정확한 키: `id`, `room_id`, `coins`, `version`, `updated_at`, `schema_version`, `source_kind`, `captured_at`.
- 스키마 값: `schema_version="player-snapshot/v1"`, `source_kind="player-snapshot"`.
- 업무 값의 출처: 기존 게임 DB의 Player 공개 다섯 필드. 쓰기 소유자는 게임 export 관리명령이다.
- `id`: 양의 정수·중복 없음·오름차순. `room_id`: 문자열. `coins`: 정수. `version`: 0 이상의 정수. 시각은 시간대가 있는 ISO 문자열이며 이 파일의 captured_at은 행 전체에 동일하다.

파일에는 계정·비밀번호·세션·좌표·광고 선택/노출/클릭 사건을 넣지 않는다. 각 Player 값·전체 ID 목록은 이 문서에 복사하지 않는다. 파일명 cdc는 binlog 수집 증거를 뜻하지 않는다.

## 직접 생산·소비 경계

저장소 루트에서 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`을 실행하면 이 경로를 쓴다. 이미 보관한 원본을 다시 수집할 때는 새 파일명을 지정해 증거를 보존한다. 광고 소비 경로는 광고 작업 폴더 기준 `../Game-server/data/exports/player-cdc.ndjson`이다. 후속 광고 검사/계약/인계 구현이 존재한다고 주장하지 않는다.

실제 bytes·형식·ID·시각 검사 결과와 이동 전후 무결성은 [경로 정정 인수인계](../../../../handoffs/2026-10-08-day24-data-path-correction.md) 및 `docs/server-routing/verification/day24-data-path-correction/snapshot-check.json`에 있다.

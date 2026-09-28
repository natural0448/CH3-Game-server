Django: server/ 에서 Daphne 단일 프로세스
게임 상태: MySQL village DB
이벤트 발행: 별도 publisher 한 개
Kafka: 앞선 3 Broker
Spark: 앞선 Master 1 + Worker 2
측정: tools/ws_load.py 를 실행하는 Python 프로세스
표시: python client/main.py 로 실행한 Pygame 창
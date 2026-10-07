# `config/settings.py`

## 책임과 호출 경계

Django 5.2 서버의 앱, middleware, MySQL, 인증 이동 경로, Channels, Kafka 및 Spark 제출 설정을 제공한다. `.env`는 `server/.env`에서 읽지만 비밀값 자체를 코드나 이 문서에 기록하지 않는다.

## 주요 변수와 값의 출처

```text
PROJECT_DIR
  출처: config/settings.py의 부모의 부모. Game-server 루트.

BASE_DIR
  값: PROJECT_DIR/server.

SECRET_KEY
  출처: DJANGO_SECRET_KEY 환경 변수. 값은 문서화하지 않음.

DEBUG / ALLOWED_HOSTS
  값: True / 127.0.0.1, localhost. 로컬 수업용 설정.

INSTALLED_APPS
  Django 기본 앱, daphne, channels, game, analytics.

DATABASES.default
  MySQL utf8mb4.
  NAME·USER·PASSWORD 출처: DB_NAME·DB_USER·DB_PASSWORD 환경 변수.
  HOST·PORT 출처: DB_HOST·DB_PORT, 기본값 127.0.0.1·3306.

LANGUAGE_CODE / TIME_ZONE / USE_TZ
  값: ko-kr / Asia/Seoul / True.

DATA_DIR
  값: PROJECT_DIR/data.

KAFKA_BOOTSTRAP_SERVERS
  출처: KAFKA_BOOTSTRAP_SERVERS 환경 변수의 쉼표 구분 값.
  기본값: 127.0.0.1:9092, 127.0.0.1:9094, 127.0.0.1:9096.

KAFKA_EVENT_TOPIC / KAFKA_GROUP_ID
  환경 변수 출처, 기본값 game.events.v1 / village-watch-v1.

KAFKA_PACKAGE
  값: org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3.

DELTA_PACKAGE
  값: io.delta:delta-spark_4.1_2.13:4.1.0.

ASGI_APPLICATION / CHANNEL_LAYERS
  config.asgi.application / 메모리 Channels layer.

LOGIN_URL / LOGIN_REDIRECT_URL / LOGOUT_REDIRECT_URL
  /accounts/login/ / /play/ / /accounts/login/.

SPARK_SUBMIT
  출처: 필수 SPARK_SUBMIT 환경 변수.

SPARK_MASTER
  출처: SPARK_MASTER 환경 변수, 기본값 spark://127.0.0.1:7077.
```

## 로딩 흐름

```text
PROJECT_DIR과 BASE_DIR 계산
server/.env 로드
필수 Django·MySQL·Spark 환경 변수 읽기
Django 앱·middleware·template·인증 설정 제공
Kafka broker·topic·group과 Spark JVM package 좌표 제공
ASGI와 Channels 설정 제공
```

직접 호출: `dotenv.load_dotenv`. Django와 관리 명령이 모듈 상수를 읽는다.

## 22일차 이미지 광고 최종 반영

ADS_BASE_URL은 process env의 기본 http://127.0.0.1:8001에서 끝 /를 제거한다. ADS_MEDIA_ID 기본 village-game, ADS_MEDIA_KEY 기본 빈 문자열이며 server/.env/process env에서만 읽는다. 기존 Django·MySQL·Channels·analytics 설정은 유지한다. 키는 브라우저·Pygame 설정·JSON에 전달하지 않는다.

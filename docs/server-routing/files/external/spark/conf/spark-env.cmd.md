# `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-env.cmd`

## 책임과 호출 경계

로컬 Spark 4.1.3 Master·Worker 프로세스가 공유하는 Windows 환경 설정이다. `tools/start-dev.ps1`이 `SPARK_CONF_DIR`을 이 폴더로 지정한 뒤 `spark-class.cmd`를 실행한다.

## 변수와 값

```text
JAVA_HOME
  호출 프로세스의 JAVA_HOME/bin/java.exe가 실제 파일이면 그 값을 유지한다.
  없거나 삭제된 경로이면 Game-server에 포함된 Temurin JDK 21 경로를 사용한다.

PYSPARK_PYTHON, PYSPARK_DRIVER_PYTHON
  기본 Python 경로. Django 제출 명령은 현재 가상환경 Python으로 다시 지정한다.

SPARK_LOCAL_IP
  127.0.0.1.

SPARK_WORKER_CORES
  Worker 한 개당 4 core.

SPARK_WORKER_MEMORY
  Worker 한 개가 executor에 제공하는 총 메모리 768m.

SPARK_DAEMON_MEMORY
  Master·Worker daemon JVM 메모리 192m.

HADOOP_HOME, PATH
  현재 Spark 설치 폴더와 그 bin 디렉터리.

TEMP, TMP
  실제 HADOOP_HOME 아래 spark-tmp. 폴더가 없으면 환경을 읽을 때 생성한다.
```

Spark 기본 driver·executor 메모리는 `spark-defaults.conf`에서 각각 768m로 제한한다. 개별 Django 제출 명령의 명시 값이 있으면 해당 값이 우선한다.

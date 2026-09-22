# `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-defaults.conf`

## 책임과 호출 경계

로컬 Spark standalone application의 기본 Master·driver·executor 자원과 병렬도를 정한다. `spark-submit`이 이 설치본의 `conf`를 읽으며, 개별 Django 관리 명령이 같은 옵션을 명시하면 관리 명령 값이 우선한다.

## 변수와 값

```text
spark.master
  spark://127.0.0.1:7077.

spark.submit.deployMode
  client.

spark.driver.host, spark.driver.bindAddress
  127.0.0.1.

spark.driver.port, spark.driver.blockManager.port
  7090, 7091.

spark.driver.memory
  기본 driver JVM 메모리 768m.

spark.executor.memory
  기본 executor JVM 메모리 768m.

spark.executor.cores, spark.cores.max
  executor당 4 core, application 전체 기본 상한 4 core.

spark.dynamicAllocation.enabled
  false. 실행 중 executor 수를 자동 확대하지 않는다.

spark.default.parallelism, spark.sql.shuffle.partitions
  각각 4. Worker 한 개의 네 CPU core를 사용하면서 작은 수업 데이터의 task 수를 제한한다.

spark.sql.session.timeZone
  Asia/Seoul.
```

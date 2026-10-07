import hashlib

# 원본과 사본 bytes의 SHA-256을 비교하고 사본의 행 수를 센다.
original = b'event-1\nevent-2\n'
copied = b'event-1\nevent-2\n'
expected = hashlib.sha256(original).hexdigest()
actual = hashlib.sha256(copied).hexdigest()
print("matched", expected == actual)
print("rows", len(copied.splitlines()))

# TODO: 위 문제 1을 구현하고 결과를 print()로 확인한다.
run_id = "capture-002"
result = {
    "run_id": run_id,
    "matched": expected == actual,
    "rows": len(copied.splitlines()),
}
print(result)
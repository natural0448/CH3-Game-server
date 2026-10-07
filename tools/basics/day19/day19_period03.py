import hashlib

# 원본 길이와 두 값의 SHA-256 일치 여부를 확인한다. bytes(raw)는 새 객체 생성을 보장하지 않는다.
raw = b'{"event_id":"e1"}\n'
copied = bytes(raw)
print("bytes", len(raw))
print("same", hashlib.sha256(raw).hexdigest() == hashlib.sha256(copied).hexdigest())
rows = len(raw.splitlines())
print("rows", rows)
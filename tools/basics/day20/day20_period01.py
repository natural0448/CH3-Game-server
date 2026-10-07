import json

# 전달 위치는 바깥 사전에서, 행동 정보는 JSON 문자열을 해석한 사전에서 읽는다.
outer = {"offset": 104, "value": '{"event_id":"e1","player_id":"7"}'}
event = json.loads(outer["value"])
print("위치", outer["offset"])
print("행동", event["event_id"])
print("플레이어", event["player_id"])

event.update({"offset": outer["offset"]})
print(event)

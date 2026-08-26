from app.main import ChatRequest, _describe_turn

# message path
r1 = ChatRequest(session_id="s1", message="Compare RELIANCE and TCS")
print(_describe_turn(r1))

# action path, with payload
r2 = ChatRequest(session_id="s1", action_id="suggest_allocation", action_payload={"amount": "50000"})
print(_describe_turn(r2))

# action path, no payload
r3 = ChatRequest(session_id="s1", action_id="confirm")
print(_describe_turn(r3))
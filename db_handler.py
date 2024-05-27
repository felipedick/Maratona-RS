from tinydb import Query, TinyDB

db = TinyDB("db.json")


def get_session(phone_number: str):
    Session = Query()
    sessions = db.search(Session.phone == phone_number)
    if sessions:
        return sessions[0]
    return create_session(phone_number)


def create_session(phone_number: str):
    session = {"phone": phone_number, "step": 0}
    db.insert(session)
    return session


def update_step(phone_number: str, ts: int):
    Session = Query()
    sessions = db.search(Session.phone == phone_number)
    step = sessions[0].get("step", 0) + 1
    db.update({"step": step, "ts": ts}, Session.phone == phone_number)


def reset_step(phone_number: str):
    Session = Query()
    sessions = db.search(Session.phone == phone_number)
    db.update({"step": 0}, Session.phone == phone_number)


def update_user_data(phone_number: str, data):
    Session = Query()
    sessions = db.search(Session.phone == phone_number)
    user_data = sessions[0].get("user_data", {})
    user_data.update(data)
    db.update({"user_data": user_data}, Session.phone == phone_number)

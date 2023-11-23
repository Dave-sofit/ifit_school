from bot import SessionData, emptyRef
from bot.engine import async_session


def setSession():
    session = SessionData.session.get()
    if session and session != emptyRef:
        return session
    else:
        session = async_session()
        SessionData.session.set(session)
        return session

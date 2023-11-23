from bot import SessionData


def getLocale():
    return SessionData.language.get()

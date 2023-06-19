import jwt
import calendar
import datetime

class TokenBuilder():
    def new_token(email:str, secret:str) -> str:
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        return "token"
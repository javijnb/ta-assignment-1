import jwt
import calendar
import datetime

class TokenBuilder():
    def new_token(secret:str) -> str:
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        return jwt.encode({"ta": "first assignment", "timestamp": utc_time}, secret, algorithm="HS256")
import uuid

class UUIDGenerator():
    def new_uuid() -> str:
        return uuid.uuid1()
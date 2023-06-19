import uuid

class UUIDGenerator:
    def new_uuid(self) -> str:
        return str(uuid.uuid1())
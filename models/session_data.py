from pydantic import BaseModel


class SessionData(BaseModel):
  passkey: dict[str, object]

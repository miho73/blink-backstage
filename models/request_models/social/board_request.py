from pydantic import BaseModel


class CreateBoardRequest(BaseModel):
  name: str

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    genre_combo:str


class TokenData(BaseModel):
    email: str = None




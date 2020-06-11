from typing import List 

from pydantic import BaseModel,typing,UUID1

class Movie(BaseModel):
    title: str
    rating: int
    genres: str
    plot: str
    poster:str
    votes:int
    id:UUID1
    user_voted:str

class MovieResponse(BaseModel):
    movies:List[Movie] =[]
    has_more_pages:bool
    paging_state:str
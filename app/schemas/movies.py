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

class MovieResponse(BaseModel):
    movies:List[Movie] =[]
    has_more_pages:bool
    paging_state:str
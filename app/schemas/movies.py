from typing import List

from pydantic import BaseModel,typing

class Movie(BaseModel):
    title: str
    rating: int
    genres: str
    plot: str
    poster:str

class MovieResponse(BaseModel):
    movies:List[Movie] =[]
    has_more_pages:bool
    paging_state:str
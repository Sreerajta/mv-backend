#sql table containing movie names, and a flag 'has_data' which is set on getting movie details from 3rd party api 
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.connections.sql import Base

class MoviesList(Base):
    __tablename__ = "movies_list"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    year = Column(Integer)
    has_data = Column(Boolean, default=False)
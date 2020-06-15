genre_to_timeiline_mappings = {
    'action':["Action,Comedy"],
    'comedy':["Action,Comedy"],
    'drama':["Drama","Drama,Fantasy"],
    'fantasy':["Drama,Fantasy"]
}

def get_timelines_by_genre(genre:str):
    return genre_to_timeiline_mappings['genre']


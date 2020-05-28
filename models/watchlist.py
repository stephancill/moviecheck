from mongoengine import Document, BooleanField, ListField, ObjectIdField, EmbeddedDocumentField
from .movie_item import MovieItem

class Watchlist(Document):
    user_id = ObjectIdField(required=True)
    items = ListField(EmbeddedDocumentField(MovieItem))
    is_default = BooleanField()

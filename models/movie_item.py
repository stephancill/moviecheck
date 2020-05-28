from mongoengine import EmbeddedDocument, DateTimeField, StringField, BooleanField

class MovieItem(EmbeddedDocument):
    imdb_id = StringField(required=True)
    date = DateTimeField()

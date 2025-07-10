from peewee import (
    CharField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

db = SqliteDatabase("date_bot.db")


class Basemodel(Model):
    class Meta:
        database = db


class User(Model):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    class Meta:
        database = db


class Idea(Model):
    text = TextField()
    image_path = CharField(null=True)

    class Meta:
        database = db

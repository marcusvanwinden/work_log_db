from datetime import datetime
from peewee import *

DATE_FORMAT = "%m/%d/%Y"
DB = SqliteDatabase("entries.db")


class Entry(Model):
    employee = CharField()
    task = CharField()
    time = IntegerField()
    notes = CharField()
    date = DateField(default=datetime.strftime(datetime.now(), DATE_FORMAT))

    class Meta():
        database = DB


def initialize_database():
    DB.connect()
    DB.create_tables([Entry], safe=True)

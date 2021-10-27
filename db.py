
import databases
import sqlalchemy
import ormar

metadata = sqlalchemy.MetaData()
database = databases.Database("sqlite:///test.db")


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata

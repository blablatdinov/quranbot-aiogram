from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from db.base import Base


class City(Base):
    __tablename__ = 'cities'

    city_id = Column(String(), primary_key=True)
    name = Column(String())
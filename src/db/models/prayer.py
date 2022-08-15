from db.base import Base

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Time, Date


class Prayer(Base):
    """Модель времени намаза."""

    __tablename__ = 'prayers'

    prayer_id = Column(String(), primary_key=True)
    time = Column(Time(), nullable=False)
    city_id = Column(String(), ForeignKey('cities.city_id'))
    day_id = Column(Date(), ForeignKey('prayer_days.date'))

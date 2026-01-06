from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float

from config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Expense(Base):
    __tablename__ = 'Expense'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()




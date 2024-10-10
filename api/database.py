from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, Table, text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

username = "root"
password = "Abdallah%402004"
host = "localhost"
database = "note_db"

Base = declarative_base()

class User_db(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    session_id = Column(String(40), default=None)
    time_created = Column(DateTime, default=datetime.utcnow)
    last_opened = Column(DateTime, default=datetime.utcnow)
    date_of_birth = Column(Text, default=None)
    description = Column(String(500), default=None)


def create_engine_and_connect():
    """Creates the engine and connects to the database."""
    return create_engine(
        'mysql+mysqlconnector://{}:{}@{}/{}'.format(
            username, password, host, database
        )
    )

def create_database():
    """Creates the database schema."""
    engine = create_engine(
        'mysql+mysqlconnector://{}:{}@{}/'.format(
            username, password, host
    ))
    with engine.connect() as connection:
        connection.execute(text("CREATE DATABASE IF NOT EXISTS {}".format(database)))
    print("Database 'note_db' created or already exists.")

def create_tables():
    engine = create_engine_and_connect()
    Base.metadata.create_all(engine)
    print("Tables created or already exist.")

def drop_db():
    engine = create_engine_and_connect()
    with engine.connect() as connection:
        connection.execute(text("DROP DATABASE IF EXISTS {}".format(database)))
    print("Database 'note_db' dropped.")

def get_session():
    """Return a new session."""
    engine = create_engine_and_connect()
    Session = sessionmaker(bind=engine)
    return Session()
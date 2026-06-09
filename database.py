from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.engine import URL

# Es el mismo archivo desarrollado en clases, esta mi version para windows, igual dejare la de Linux a mano.

url_object = URL.create(    # windows
    "postgresql+psycopg",
    username="postgres",
    password="ale",  # No manual escaping needed
    port=5433,
    host="localhost",
    database="superrestaurant9"
)

DB_URL = "postgresql+psycopg//postgres:ale@localhost:5433/supermakert6" # Linux

engine = create_engine(url_object)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass


def get_db():
    db = Session()
    try:
        yield db 
    finally:
        db.close()
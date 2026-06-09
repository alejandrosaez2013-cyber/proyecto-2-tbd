from fastapi import FastAPI

from database import Base, engine
from routers import items, restaurantes, ordenes, usuarios

# Es el mismo archivo entregado en clases solo que modificado para que funcione con todo lo requerido.

app = FastAPI()
Base.metadata.create_all(engine)

app.include_router(items.router)
app.include_router(restaurantes.router)
app.include_router(ordenes.router)
app.include_router(usuarios.router)
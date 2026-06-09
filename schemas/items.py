import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.utils import RestauranteBase

class ItemRead(BaseModel):  # Esta estructura ayuda a mostrar los datos de un Item.

    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    nombre: str
    descripcion: str
    precio: int
    stock: int
    disponible: str

    restaurante_id: uuid.UUID
 
    restaurante: Optional[RestauranteBase] = None
        
class ItemCreate(BaseModel):    # Esta estructura ayuda a crearlos datos de un Item.

    nombre: str = Field(max_length=100)
    descripcion: str = Field(max_length=200)
    precio: int
    stock: int
    disponible: str = Field(max_length= 10)
    restaurante_id: uuid.UUID

class ItemUpdate(BaseModel):    # Esta estructura ayuda a actualizar los datos de un Item.

    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    precio: Optional[int] = None
    stock: Optional[int] = None
    disponible: Optional[str] = Field(default=None, max_length= 10)
    restaurante_id: uuid.UUID
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.utils import UsuarioBaseName, ItemsBase2, OrdenBase2, ItemsBaseuuid, UsuarioBaseuuuid


class RestauranteRead(BaseModel):   # Esta estructura sirve para ver los datos del restaurnate.

    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    nombre: str
    descripcion: Optional[str]
    direccion: str
    telefono: str
    estado: str
    costo_de_envio: int

    usuarios: list[UsuarioBaseName] = Field(default_factory=list)

    lista_items: list[ItemsBase2] = Field(default_factory=list)

    conjunto_de_ordenes: list[OrdenBase2] = Field(default_factory=list)
        
class RestauranteCreate(BaseModel): # Esta estructura sirve para crear el restaurnate.

    nombre: str = Field(max_length=100)
    descripcion: str = Field(max_length=200)
    direccion: str = Field(max_length= 100)
    telefono: str = Field(max_length= 12)
    estado: str = Field(max_length= 10)
    costo_de_envio: Optional[int] = None

    usuarios: list[UsuarioBaseuuuid] = Field(default_factory=list)

class RestauranteUpdate(BaseModel): # Esta estructura sirve para actualizar los datos del restaurnate.

    nombre: Optional[str] = Field(default = None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    direccion: Optional[str] = Field(default = None,max_length= 100)
    telefono: Optional[str] = Field(default = None,max_length= 12)
    estado: Optional[str] = Field(default = None, max_length= 10)
    costo_de_envio: Optional[int] = None

    usuarios: list[UsuarioBaseuuuid] = Field(default_factory=list)

    lista_items: list[ItemsBaseuuid] = Field(default_factory=list)

class RestauranteEstado(BaseModel): # Esta estructura sirve unicamenete para cambiar el estado del restaurante.

    estado: str = Field(max_length= 10)

class RestauranteReadOrden(BaseModel):  # Esta estructura sirve para ver las ordenes del restaurnate.

    model_config = ConfigDict(from_attributes=True)
    conjunto_de_ordenes: list[OrdenBase2] = Field(default_factory=list)

class RestauranteVentas(BaseModel): # Esta estructura sirve para mostrar el total de las ventas del restaurante. para su respectiva funcion 
                                    # "obtener_restaurante_ventas".

    total_ventas: int
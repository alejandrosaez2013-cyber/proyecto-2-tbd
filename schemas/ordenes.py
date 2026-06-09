import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.utils import ItemsBase2, RestauranteBase, UsuarioBaseName, ItemsBaseuuid

class OrdenRead(BaseModel): # Esta estructura sirve para mostrar los datos de una orden.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    descripcion_de_entrega: str
    estado: str
    subtotal: int
    costo_de_envio: int
    descuento: int
    total: int
    notas_opcionales: Optional[str] = None
    creado_en: datetime
    ultimo_actualizacion: datetime

    lista_items: list[ItemsBase2] = Field(default_factory=list)

    restaurante_id: uuid.UUID
 
    restaurante: Optional[RestauranteBase] = None

    usuario_id: uuid.UUID
 
    usuario: Optional[UsuarioBaseName] = None


class OrdenCreate(BaseModel):   # Esta estructura sirve para crear una orden.

    descripcion_de_entrega: str = Field(default=None, max_length=200)
    estado: str = Field(default="pendiente", max_length=10)
    notas_opcionales: Optional[str] = Field(default=None, max_length=200)
    costo_de_envio: int
    restaurante_id: uuid.UUID
    lista_items: list[ItemsBaseuuid] = Field(default_factory=list)

class OrdenUpdate(BaseModel):   # Esta estructura sirve para modificar los datos de una orden.
    
    descripcion_de_entrega: Optional[str] = Field(default=None, max_length=200)
    estado: str = Field(default="pendiente", max_length=10)
    notas_opcionales: Optional[str] = Field(default=None, max_length=200)
    usuario_id: Optional[uuid.UUID] = None
    restaurante_id: Optional[uuid.UUID] = None
    lista_items: list[ItemsBaseuuid] = Field(default_factory=list)

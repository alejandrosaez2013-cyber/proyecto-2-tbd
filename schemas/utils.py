from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, EmailStr, Field
    
class RestauranteBase(BaseModel):   # Esta es la estructura mostrar los datos del restaurante y no entrar en ciclos.

    id: uuid.UUID
    nombre: str
    descripcion: Optional[str]
    direccion: str
    telefono: str
    estado: str
    costo_de_envio: int

class UsuarioBaseName(BaseModel):   # Esta es la estructura mostrar los datos del usuario y no entrar en ciclos.

    id: uuid.UUID
    nombre_completo: str
    email: Optional[EmailStr] = None
    telefono: str
    direccion: Optional[str]
    ultimo_acceso: datetime
    creado_en: datetime
    rol: str

class UsuarioBase(UsuarioBaseName): # Esta estructura es una idea desechada.

    restaurante_id: Optional[uuid.UUID] = None
    restaurante: Optional[RestauranteBase] = None

class OrdenItemBase(BaseModel): # Esta es la estructura mostrar los datos de la tabla intermedia entre orden y items.

    orden_id: uuid.UUID 
    item_id: uuid.UUID
    cantidad_de_elementos: int
    precio_de_elemento: int

class OrdenBase(BaseModel): # Esta es la estructura mostrar los datos de una orden y no entrar en ciclos.

    id: uuid.UUID
    descripcion_de_entrega: str
    estado: str
    subtotal: int
    costo_de_envio: int
    descuento: int
    total: int
    notas_opcionales: str
    creado_en: datetime
    ultimo_actualizacion: datetime
    lista_items: list[OrdenItemBase] = Field(default_factory=list)
    
class ItemsBase(BaseModel): # Esta estructura es una idea desechada.
    
    id: uuid.UUID
    nombre: str
    descripcion: str
    precio: int
    stock: int
    disponible: str
    restaurante_id: uuid.UUID
    restaurante: Optional[RestauranteBase] = None

class OrdenBase2(BaseModel):    # Esta es la estructura mostrar los datos de la orden sin mostar los datos de la lista de items y no entrar en ciclos.

    id: uuid.UUID
    descripcion_de_entrega: str
    estado: str
    subtotal: int
    costo_de_envio: int
    descuento: int
    total: int
    notas_opcionales: str
    creado_en: datetime
    ultimo_actualizacion: datetime

class ItemsBase2(BaseModel):    # Esta es la estructura mostrar los datos del item sin los datos del restaurante y no entrar en ciclos.
    
    id: uuid.UUID
    nombre: str
    descripcion: str
    precio: int
    stock: int
    disponible: str

class ItemsBaseuuid(BaseModel): # Esta es la estructura para pedir el uuid.UUID de un item.
    
    id: uuid.UUID

class UsuarioBaseuuuid(BaseModel): # Esta es la estructura para pedir el uuid.UUID de un usuario.

    id: uuid.UUID
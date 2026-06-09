import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.utils import RestauranteBase, OrdenBase

class UsuarioRead(BaseModel):   # Esta es la principal estructura para leer los datos de los usuarios.

    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[uuid.UUID]
    nombre_completo: str
    email: Optional[EmailStr]
    telefono: str
    direccion: Optional[str]
    ultimo_acceso: datetime
    creado_en: datetime
    rol: str
    restaurante_id: Optional[uuid.UUID] = None
    restaurante: Optional[RestauranteBase] = None
    ordenes: Optional[list[OrdenBase]] = None

class UsuarioCreate(BaseModel): # Esta es la estructura usada para crear los usuarios.

    nombre_completo: str = Field(max_length=100)
    email:  Optional[EmailStr] = None
    telefono: str = Field(max_length= 12)
    direccion: Optional[str] = None
    hashed_password: str = Field(max_length=255)
    rol: str = Field(max_length= 20)
    restaurante_id: Optional[uuid.UUID] = None
    
class UsuarioUpdate(BaseModel): # Esta es la estructura para actualizar los datos de los usuarios.

    nombre_completo: Optional[str] = Field(default=None, max_length=100)
    email:  Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length= 12)
    direccion: Optional[str] = None
    rol: Optional[str] = Field(default=None, max_length= 20)
    restaurante_id: Optional[uuid.UUID] = None

class Token(BaseModel):    #Esta ultimas dos estructuras fueron entregadas en clase para manejar los Datsos del Token de verificacion.
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    nombre_completo: Optional[str] = None
    id: Optional[uuid.UUID] = None
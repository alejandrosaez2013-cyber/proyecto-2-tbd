from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class Usuario(Base):    #Esta es la clase Usuario, contiene la estructura para todos los usuarios, tiene una relacion 1 es a muchos con ordenes, y una relacion muchos a 1 con restaurante
    __tablename__ = "usuarios"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(100), unique=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    telefono: Mapped[str] = mapped_column(String(12), unique=True)
    direccion: Mapped[str] = mapped_column(String(100), unique=False)
    hashed_password: Mapped[str] = mapped_column(String(255))
    ultimo_acceso: Mapped[datetime] = mapped_column(DateTime, default = datetime.now)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default = datetime.now)
    rol: Mapped[str] = mapped_column(String(20), unique=False)

    ordenes: Mapped[list["Orden"]] = relationship(back_populates="usuario")

    restaurante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurantes.id"), nullable=True)

    restaurante: Mapped["Restaurante"] = relationship(back_populates="usuarios")

class Restaurante(Base):    #Esta es la clase Restaurante, contiene la estructura para los restaurantes, contiene relaciones 1 es amuchos con usuarios, items, y ordenes, no ocupe costo de envio de restaurante, solo ocupe el de orden
    __tablename__ = "restaurantes"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str] = mapped_column(String(200), unique=False)
    direccion: Mapped[str] = mapped_column(String(100), unique=True)
    telefono: Mapped[str] = mapped_column(String(12), unique=True)
    estado: Mapped[str] = mapped_column(String(10), unique=False)
    costo_de_envio: Mapped[int] = mapped_column(Integer)
 
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="restaurante")

    lista_items: Mapped[list["Items_del_menu"]] = relationship(back_populates="restaurante")

    conjunto_de_ordenes: Mapped[list["Orden"]] = relationship(back_populates="restaurante")

    
    
class Items_del_menu(Base): #Esta es la clase Items, contiene la estructura para todos los items, tiene una relacion muchos a muchos con ordenes, y una relacion muchos a 1 con restaurante
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=False)
    descripcion: Mapped[str] = mapped_column(String(200), unique=False)
    precio: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer)
    disponible: Mapped[str] = mapped_column(String(10), unique=False)

    ordenes: Mapped[list["Orden"]] = relationship(secondary="items_de_una_orden", back_populates="lista_items")

    restaurante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurantes.id"), nullable=True)
 
    restaurante: Mapped["Restaurante"] = relationship(back_populates="lista_items")

class Orden(Base):  #Esta es la clase Orden, contiene la estructura para todos las ordenes, tiene una relacion muchos a muchos con ordenes, y unas relaciones muchos a 1 con restaurante, y usuario
    __tablename__ = "ordenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    descripcion_de_entrega: Mapped[str] = mapped_column(String(200), unique=False)
    estado: Mapped[str] = mapped_column(String(10), unique=False)
    subtotal: Mapped[int] = mapped_column(Integer)
    costo_de_envio: Mapped[int] = mapped_column(Integer)
    descuento: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    notas_opcionales: Mapped[str | None] = mapped_column(String(200), unique=False, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default = datetime.now)
    ultimo_actualizacion: Mapped[datetime] = mapped_column(DateTime, default = datetime.now, onupdate=datetime.now)

    lista_items: Mapped[list["Items_del_menu"]] = relationship(secondary="items_de_una_orden", back_populates="ordenes")

    restaurante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurantes.id"), nullable=True)
 
    restaurante: Mapped["Restaurante"] = relationship(back_populates="conjunto_de_ordenes")

    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
 
    usuario: Mapped["Usuario"] = relationship(back_populates="ordenes")

class Items_de_una_orden(Base): #Esta es la clase es la tabla generada apartir de la relacion muchos a muchos entre Items y Orden
    __tablename__ = "items_de_una_orden"
    
    orden_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("ordenes.id", ondelete="CASCADE"), primary_key=True)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True)
    cantidad_de_elementos: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_de_elemento: Mapped[int] = mapped_column(Integer, nullable=False)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.items import ItemCreate, ItemRead, ItemUpdate
from routers.usuarios import obtener_usuario_actual
from models import Usuario
import uuid

# Esta es la tercera lista de enpoints que hice, ya con mas experiaencia de haber hecho las otras 2, aqui simplemente aplique lo aprendido.

router = APIRouter(prefix="/items", tags=["Items"])

# La funcion "listar_items" entrega una lista de items.

@router.get("/listar", response_model=list[ItemRead]) #
async def listar_items(db: Session = Depends(get_db)):
    items = db.execute(select(models.Items_del_menu)).scalars().all()
    return items

# La funcion "obtener_item" busca un item basado en su id.

@router.get("/{id}/obtener", response_model=ItemRead) #
async def obtener_item(id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(models.Items_del_menu, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

# La funcion "crear_item" verifica que sea el dueno del restaurante el que este creando el item, que el restaurante de donde estara el item exista, y que se 
# ingresen valores positivos de "precio" y "stock", una vez verificado se guarda el item en la base de datos.

@router.post("/crear", response_model=ItemRead, status_code=201) 
async def crear_item(data: ItemCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "dueno" or usuario.restaurante_id != data.restaurante_id:
        raise HTTPException(status_code=403, detail="Solo duenos de este restaurante pueden crear un item")

    restaurante = db.get(models.Restaurante, data.restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante inexistente")

    nuevo = models.Items_del_menu(**data.model_dump(exclude_none=True))
    nuevo.restaurate_id = usuario.restaurante_id

    if nuevo.precio < 0 or nuevo.stock < 0:
        raise HTTPException(status_code=404, detail="ingrese valores positivos")
        
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# La funcion "actualizar_item" verifica que sea el dueno del restaurante el que este actualizando el item, que el item exista, y que se ingresen valores 
# positivos de "precio" y "stock", una vez se verifique todo, se da acceso a los valores del item para modificarlo.

@router.patch("/{id}/actualizar", response_model=ItemRead) 
async def actualizar_item(id: uuid.UUID, data: ItemUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    item = db.get(models.Items_del_menu, id)

    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    if usuario.rol != "dueno" or usuario.restaurante_id != item.restaurante_id:
        raise HTTPException(status_code=403, detail="Solo duenos pueden actualizar un item")
    
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(item, campo, valor)

    if item.precio < 0 or item.stock < 0:
        raise HTTPException(status_code=404, detail="ingrese valores positivos")
    
    db.commit()
    db.refresh(item)
    return item

# La funcion "eliminar_item" verifica que sea el dueno del restaurante el que este creando el item, y que elitem exista, una vez verificado se elimnia el item
#  requerido.

@router.delete("/{id}/borrar", status_code=204)
async def eliminar_item(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    item = db.get(models.Items_del_menu, id)

    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    if usuario.rol != "dueno" or usuario.restaurante_id != item.restaurante_id:
        raise HTTPException(status_code=403, detail="Solo duenos pueden borrar un item")

    db.delete(item)
    db.commit()
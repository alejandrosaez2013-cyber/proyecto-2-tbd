from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.ordenes import OrdenCreate, OrdenRead, OrdenUpdate
from routers.usuarios import obtener_usuario_actual
from models import Usuario
import uuid

# Esta es la 4 lista de endpoints que ise, y fua una de las que mas costo, en esta tuve que pedirle ayuda a la ia principalmente en 2 funciones, que tenia a 
# medias y no funcionaban, recuerdo que esto fue lo mas complicado.

router = APIRouter(prefix="/ordenes", tags=["Ordenes"])

# La funcion "listar_ordenes" verifica que el rol del usuario sea "admin","dueno","staff", una vez verificado entrega una lista de ordenes.

@router.get("/listar", response_model=list[OrdenRead])
async def listar_ordenes(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol not in ["admin","dueno","staff"]:
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden ver las ordenes")

    ordenes = db.execute(select(models.Orden)).scalars().all()
    return ordenes

# La funcion "obtener_orden" verifica que el rol del usuario sea "admin","dueno","staff", una vez verificado busca una orden por id, la encuentra y entrega 
# los datos de la orden.

@router.get("/{id}/obtener", response_model=OrdenRead)
async def obtener_orden(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol not in ["admin","dueno","staff"]:
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden ver las ordenes")

    orden = db.get(models.Orden, id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrado")
    return orden

# La funcion "crear_orden" fue la que mas me costo, lo unico que pude hacer mas omenoes bien fue la parte de calcular el total en donde los unicos reparos fueron,
# 1 la forma de calcular la cantidad de ordenes, y el calculo del subtotal que ise la mitad de ese codigo, el resto fue un lio, que alfinal chatgpt termino 
# armando, hasta donde comprendo el funcionamiento de la funcion es el siguiente:

@router.post("/crear", response_model=OrdenRead, status_code=201)
async def crear_orden(data: OrdenCreate, db: Session = Depends(get_db), usuario: Usuario | None = Depends(obtener_usuario_actual)):
    datos= data.model_dump(exclude= {"lista_items"}, exclude_none=True)     
    nuevo = models.Orden(**datos)   # 1.- Se recuperan los datos ingresados por el usuario de forma segura.

    total_orden = 0
    nuevo.usuario_id = usuario.id   # 2.- Se dise que el usuario que esta usando la funcion es que esta haciendo la orden.

    if nuevo.restaurante_id is None:    # 3.- Se verifica que se alla agregado un restaurante no nulo.
        raise HTTPException(status_code=404, detail="Agrege un restaurante")

    existe = (db.query(models.Restaurante).filter(models.Restaurante.id == data.restaurante_id).first())
    abierto = (db.query(models.Restaurante).filter(models.Restaurante.estado == "cerrado", models.Restaurante.id == data.restaurante_id).first())

    if abierto:
        raise HTTPException(status_code=409,detail="Esta cerrado el restaurante")

    if existe is None:
        raise HTTPException(status_code=409,detail="No existe un restaurante con ese id")   # 4.- Se verifica que se alla agregado un restaurante de los 
                                                                                            # existentes y que este abierto.

    nuevo.subtotal = 0
    nuevo.descuento = 0
    nuevo.total = 0 # 5.- Inicializo las variables para que no sean nulas.

    db.add(nuevo)
    db.flush()      # 6.- Actualizo??(no estoy seguro de que hace el flush).
    
    for itemR in data.lista_items:  # 7.- Con este ciclo recorro la lista de items.

        item = db.get(models.Items_del_menu, itemR.id)  # 8.- Accedo a los datos del item.

        if item.disponible == "disponible": # 9.- Verifico que el item este disponible.
            total_orden = total_orden + item.precio
            item.stock = item.stock-1   # 10.- calculo el subtotal con la variable "total_orden".
            if item.stock == 0:
                item.disponible = "agotado" # 11.- Cambio el estado del item se se agota.
        else:
            raise HTTPException(status_code=404, detail="Item no disponible")

        detalleOrden = models.Items_de_una_orden(orden_id=nuevo.id, item_id=item.id, cantidad_de_elementos=1, precio_de_elemento=item.precio)

        db.add(detalleOrden)    # 12.- Actualizo la tabla intermedia.

    nuevo.subtotal = total_orden    # 13.- Almaceno el subtotal.

    cantidad_ordenes = (db.query(func.count(models.Orden.id)).filter(models.Orden.usuario_id == usuario.id).scalar())  # 14.- En las siguientes lineas calculo si 
                                                                                                                        # el necesita un descuento vasado en su 
                                                                                                                        # cantidad de ordense.

    if cantidad_ordenes < 5:
        nuevo.descuento = 0
    elif cantidad_ordenes >= 5 and cantidad_ordenes < 10:
        nuevo.descuento = 5
    elif cantidad_ordenes >= 10 and cantidad_ordenes < 15:
        nuevo.descuento = 10
    else:
        nuevo.descuento = 15

    descuento = nuevo.subtotal + nuevo.costo_de_envio
    descuento = descuento - ((nuevo.subtotal*nuevo.descuento)/100)

    nuevo.total = round(descuento)  # 15.- Por ultimo aplico el descuento y subo todo a la base de datos.

    db.commit()
    db.refresh(nuevo)
    return nuevo

# La funcion "actualizar_orden" verifica que el rol del usuario sea "staff", una vez verificado busca una orden por id, la encuentra y da acceso a los 
# datos de la orden para modificarlos.

@router.patch("/{id}/actualizar", response_model=OrdenRead)
async def actualizar_orden(id: uuid.UUID, data: OrdenUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "staff":
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden actualizar las ordenes")

    orden = db.get(models.Orden, id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrado")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(orden, campo, valor)
    db.commit()
    db.refresh(orden)
    return orden

# La funcion "eliminar_orden" verifica que el rol del usuario sea "staff", una vez verificado busca una orden por id, la encuentra y la elimina.

@router.delete("/{id}/eliminar", status_code=204)
async def eliminar_orden(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "staff":
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden eliminar las ordenes")

    orden = db.get(models.Orden, id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrado")
    db.delete(orden)
    db.commit()

# La funcion "actualizar_orden_estado" verifica que el rol del usuario sea "staff", una vez verificado busca una orden por id, la encuentra y la cambia 
# de estado al siguiente siempre que no este en el ultimo estado.

@router.patch("/{id}/actualizar_orden", response_model=OrdenRead)
async def actualizar_orden_estado(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "staff":
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden actualizar las ordenes")

    orden = db.get(models.Orden, id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrado")

    if orden.estado == "pendiente":
        orden.estado = "confirmado"
    elif orden.estado == "confirmado":
        orden.estado = "preparando"
    elif orden.estado == "preparando":
        orden.estado = "en_camino"
    else:
        orden.estado = "entregado"

    db.commit()
    db.refresh(orden)
    return orden

# La funcion "listar_ordenes_por" verifica que el rol del usuario sea "admin","dueno","staff", una vez verificado da la opcion de dar una lista de orden 
# basado en su estado y su monto. Esta funcion tampoco la supe hacer fue la ultima que hice, entonces le pregunte a chatgpt si la podia hacer y iso todo, 
# menos la verificacion esa la agrege yo vasado en experiencias anteriores dentro de este trabajo.

@router.get("/obtener_ordenes_por", response_model=list[OrdenRead])
async def listar_ordenes_por(estado:str | None = None, monto:int | None = None, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol not in ["admin","dueno","staff"]:
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden ver las ordenes")

    pregunta = select(models.Orden)

    if estado != None:
        pregunta = pregunta.where(models.Orden.estado == estado)

    if monto != None:
        pregunta = pregunta.where(models.Orden.total >= monto)

    ordenes = db.execute(pregunta).scalars().all()
    return ordenes
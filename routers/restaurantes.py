from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.restaurantes import RestauranteCreate, RestauranteRead, RestauranteUpdate, RestauranteEstado, RestauranteVentas, RestauranteReadOrden
from routers.usuarios import obtener_usuario_actual

from models import Usuario
import uuid

# Esta fue la segunda lista de enpoints que hice fue mas facil que la anterior use menos ia por el tema de que no ocuba nada nuevo de seguridad, asique solo 
# aplique lo de verificar usuario que ya habia aprendido.

router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])

# La funcion "listar_restaurantes" busca los restaurantes y te los muestra sus datos.

@router.get("/listar", response_model=list[RestauranteRead])
async def listar_restaurantes(db: Session = Depends(get_db)):
    restaurantes = db.execute(select(models.Restaurante)).scalars().all()
    return restaurantes

# La funcion "obtener_restaurante" busca el restaurante por su id y te muetra sus datos.

@router.get("/{id}/obtener", response_model=RestauranteRead)
async def obtener_restaurante(id: uuid.UUID, db: Session = Depends(get_db)):
    restaurante = db.get(models.Restaurante, id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return restaurante

# La funcion "crear_restaurante" verifica que seas un admin, que no exista otro restaurante con el mismo nombre, y si le ingresas un usuario verifica su 
# existencia. Recuerdo que esta funcion me dio problemas, le termine preguntado a chatgpt y me explico que el problema estaba en los schemas, resulta que antes en 
# vez de pedir solo la id del usuario pedia el usuario completo, asique tuve que crear un nuevo esquema para que solo me pida el uuid.UUID. De esta funcion chatgpt
# me aporto estas 3 lineas: "datos= data.model_dump(exclude= {"usuarios"}, exclude_none=True)" (me ayuda a manejar el tema ingresar usuarios), 
# "nuevo = models.Restaurante(**datos)"(crea la estructura con los datos), "db.flush()"(no estoy seguro de que ase, pero si no esta actualizacion? la funcion 
# no funciona), "userer.restaurante_id = nuevo.id"(ayuda a actualizar la base de datos para que todo concuerde).

@router.post("/crear", response_model=RestauranteRead, status_code=201) 
async def crear_restaurante(data: RestauranteCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear un restaurante")

    datos= data.model_dump(exclude= {"usuarios"}, exclude_none=True)

    existe = (db.query(models.Restaurante).filter(models.Restaurante.nombre == data.nombre).first())

    if existe:
        raise HTTPException(status_code=409,detail="Ya existe un restaurante con ese nombre")

    nuevo = models.Restaurante(**datos)

    db.add(nuevo)
    db.flush()

    for user in data.usuarios:

        userer=db.get(models.Usuario, user.id)

        if userer is None:
            raise HTTPException(status_code=403, detail="Usuario id no encontrado")

        userer.restaurante_id = nuevo.id

    db.commit()
    db.refresh(nuevo)
    return nuevo

# La funcion "actualizar_restaurante" revisaque seas un admin, una vez verificado te permite buscar el restaurante por su id y te da acceso a los datos 
# para modificarlos.

@router.patch("/{id}/actualizar", response_model=RestauranteRead)
async def actualizar_restaurante(id: uuid.UUID, data: RestauranteUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar un restaurante")

    restaurante = db.get(models.Restaurante, id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(restaurante, campo, valor)
    db.commit()
    db.refresh(restaurante)
    return restaurante

# La funcion "elimninar_restaurante" revisaque seas un admin, una vez verificado te permite buscar eliminar un restaurante bassado en su id. 
# para modificarlos.

@router.delete("/{id}/eliminar", status_code=204)
async def eliminar_restaurante(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar un restaurante")

    restaurante = db.get(models.Restaurante, id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    db.delete(restaurante)
    db.commit()

# La funcion "actualizar_apertura" revisaque que el restaurante exista, y que seas su dueno, una vez verificado te permite cambiar el estado del restaurante 
# la idea es cabiar los estaos solo entre "abierto" y "cerrado", este encuentra el restaurnate por id.

@router.patch("/{id}/actualizar/apertura", response_model=RestauranteEstado)
async def actualizar_apertura(id: uuid.UUID, data: RestauranteEstado, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    restaurante = db.get(models.Restaurante, id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if usuario.rol != "dueno" or usuario.restaurante_id != restaurante.id:
        raise HTTPException(status_code=403, detail="Solo los duenos pueden cambiar el estado de apertura de un restaurante")

    restaurante.estado = data.estado
    db.commit()
    db.refresh(restaurante)
    return restaurante

# La funcion "obtener_restaurante_ordenes" revisaque seas un "dueno" o "staff" del restaurante, que el restaurante exista, una vez verificado te mustra las 
# ordenes del restaurante. 

@router.get("/{id}/ordenes", response_model=RestauranteReadOrden) #
async def obtener_restaurante_ordenes(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    restaurante = db.get(models.Restaurante, id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if usuario.rol not in ["dueno","staff"] or usuario.restaurante_id != restaurante.id:
        raise HTTPException(status_code=403, detail="Solo los duenos y los de staff pueden ver las ordenes del restaurante")

    return restaurante

# La funcion "obtener_restaurante_ventas" revisaque seas el dueno del restaurante, que exista el restaurante, una vez verificado busca el restaurante por id, 
# te muestra las ventas totales del restaurante, recuerdo que cuando estaba haciendo esta funcion no sabia como sumar el total , debido a que aun no probaba 
# las funciones, y no sabia del problemas de los schemas que tenia a la hora de crear un restaurante, asique le pase a chatgpt la funcion sin la parte de
# la sumatoria, y el agrego la parte de la sumatoria y modifico el return "total = sum(orden.total for orden in restaurante.conjunto_de_ordenes)", 
# "return {"total_ventas": total}".

@router.get("/{id}/ventas", response_model=RestauranteVentas) #
async def obtener_restaurante_ventas(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    restaurante = db.get(models.Restaurante, id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if usuario.rol != "dueno" or usuario.restaurante_id != restaurante.id:
        raise HTTPException(status_code=403, detail="Solo los duenos pueden ver las ventas del restaurante")

    total = sum(orden.total for orden in restaurante.conjunto_de_ordenes)

    return {"total_ventas": total}

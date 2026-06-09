from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.usuarios import UsuarioCreate, UsuarioRead, UsuarioUpdate, Token, TokenData
from security import crear_hash_password, verificar_password, crear_access_token, verificar_token
from models import Usuario
import uuid
from config import settings

# Estos Endpoints de Usuario fueron los que mas me costaron hacer debido a que fueron los primeros que hice, como no entiandia mucho le pedi ayuda a chatgpt 
# cuando me perdia o confundia mucho, lo cual fue algo muy comun, pero de apoco fui entendiendo mas de como funciona y utilizando menos chatgpt, a no ser que 
# el problema sea muy complicado, o dificil de imaginar.

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
oauth2_schema = OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=False)  

 # Aqui mi primer gran problema, cuando estuve copiando y modificando el ejemplo entregado en clase, me guie por el archivo clientes.py, y 
 # no aplique nada sobre seguridad, cuando llego el momento deaplicar le termine preguntado a chatgpt, este me escribio un codigo funcional, para usarlo 
 # con el security.py, pero lo termine borrando debido a que encontre el codigo original del ejemplo de "obtener_usuario_actual" en users.py.
 
 # La funcion "obtener_usuario_actual" tiene "token:str | None = Depends(oauth2_schema)", que sirve que no de error de falta de token, la funcion "crear_usuario" 
 # al moneto de crear el primer usuario que sera de rol admin, sin necesidad de identificarse, igual mente el 
 # "oauth2_schema = OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=False)" tiene el "auto_error=False" para el mismo proposito.

def obtener_usuario_actual(token:str | None = Depends(oauth2_schema), db: Session = Depends(get_db)): 
    payload = verificar_token(token)

    if token is None:
        return None
    
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Token invalido o expirado", headers = {"WWW-Authenticate": "Bearer"})
    
    token_data = TokenData(id = payload.get("id"), username = payload.get("sub"))
    
    usuario = db.get(models.Usuario, token_data.id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# La funcion "listar_usuarios" entrga un listado de los usuarios, y verifica que el que usa la funcion sea un usuario verificado y que su rol sea:
# "admin", "dueno", "staff".

@router.get("/listar", response_model=list[UsuarioRead]) 
async def listar_usuarios(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if not usuario:
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden ver los usuarios")
    
    if usuario.rol not in ["admin","dueno","staff"]:
        raise HTTPException(status_code=401, detail="Solo trabajadores pueden ver los usuarios")

    usuarios = db.execute(select(models.Usuario)).scalars().all()
    return usuarios


# La funcion "obtener_usuario" se le pasa un "ID" de un usario, y recupera los datos del usuario. Esta funcion verifica que el que la usa sea un usuario 
# verificado y que su rol sea "admin", "dueno", "staff".

@router.get("/{id}/obtener", response_model=UsuarioRead) 
async def obtener_usuario(id: uuid.UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):

    if usuario.rol not in ["admin","dueno","staff"]:
        raise HTTPException(status_code=402, detail="Solo trabajadores pueden buscar usuarios")

    usuario = db.get(models.Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# La funcion "crear_usuario" solicita datos para crear un usuario. Esta funcion verifica que el que la usa sea un usuario verificado y que su rol sea "admin"
# Pero ademas hace algo mas en caso de que no se alla creado el primer usuario.

@router.post("/crear", response_model=UsuarioRead, status_code=201) 
async def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db), usuario: Usuario | None = Depends(obtener_usuario_actual)):

    existeadmin = (db.query(models.Usuario).filter(models.Usuario.rol == "admin").first())  # Primero pregunta si existe algun admin

    if not existeadmin: # Si no hay ningun admin solicita los datos entregados menos "rol", recupera la contrasena, la procesa y obliga que el rol sea admin, 
                        # por ultimo lo sube a la base de datos.

        datos = data.model_dump(exclude={"rol"}, exclude_none=True)

        password = datos.pop("hashed_password")

        nuevo = models.Usuario(**datos, hashed_password=crear_hash_password(password), rol="admin")

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    
    else:   # Si existe un admin pregunta si los datos otorgados estan repetidos, recupera la contrasena, la procesa, revisa si el restaurante ya tenia dueno, y 
            # lo sube a la base de datos.

        existe_usuairo = (db.execute(select(models.Usuario).where(models.Usuario.nombre_completo == data.nombre_completo))).scalar_one_or_none()
        
        existe_email = (db.execute(select(models.Usuario).where(models.Usuario.email == data.email))).scalar_one_or_none()

        if existe_usuairo or existe_email:
            raise HTTPException(status_code=409, detail="Información ya registrado")

        if usuario is None:
            raise HTTPException(status_code=403, detail="Debe autenticarse")

        if usuario.rol != "admin":
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear usuarios")

    
    datos = data.model_dump(exclude_none=True)

    password = datos.pop("hashed_password")

    nuevo = models.Usuario(**datos, hashed_password=crear_hash_password(password))

    existe_dueno = (db.execute(select(models.Usuario).where(models.Usuario.restaurante_id == data.restaurante_id, models.Usuario.rol == data.rol, data.rol == "dueno", data.restaurante_id != None))).scalar_one_or_none()

    if existe_dueno:
        raise HTTPException(status_code=404, detail="Ya tiene dueno")
        
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# # La funcion "actualizar_usuario" se le pasa un "ID" de un usario, recupera los datos del usuario, y los hace posible actualizar. Esta funcion verifica 
# que el que la usa sea un usuario verificado y que su rol sea "admin".

@router.patch("/{id}/actualizar", response_model=UsuarioRead)
async def actualizar_usuario(id: uuid.UUID, data: UsuarioUpdate, db: Session = Depends(get_db), admin: Usuario = Depends(obtener_usuario_actual)):

    if admin.rol != "admin":
        raise HTTPException(status_code=402, detail="Solo administradores pueden modificar usuarios")

    usuario = db.get(models.Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario

# La funcion "eliminar_usuario" se le pasa un "ID" de un usario, y elimina el suario de la base de datos. Esta funcion verifica que el que la usa sea un usuario 
# verificado y que su rol sea "admin".

@router.delete("/{id}/eliminar", status_code=204)
async def eliminar_usuario(id: uuid.UUID, db: Session = Depends(get_db), admin: Usuario = Depends(obtener_usuario_actual)):

    if admin.rol != "admin":
        raise HTTPException(status_code=401, detail="Solo administradores pueden borrar usuarios")

    usuario = db.get(models.Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()

# La funcion "login" esta tal cual la vista en clase solo con ligeros cambios de nombre para que funcione.

@router.post("/login")
async def login(credenciales_usuario: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = (db.execute(select(models.Usuario).where(models.Usuario.nombre_completo == credenciales_usuario.username))).scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Credenciales no validas")
    
    if not verificar_password(credenciales_usuario.password, usuario.hashed_password ):
        raise HTTPException(status_code=401, detail="Credenciales no validas")

    access_token = crear_access_token(data = {"sub": usuario.nombre_completo, "id": str(usuario.id)}, expires_delta=timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTOS))
    
    return Token(access_token=access_token, token_type="bearer") #{"mensaje":"Login exitoso"}

# La funcion "obtener_usuario_activo" es la misma funcion que vimos en clase de "obtener_clase" que lo que hace es mostrarte la informacion del usuario activo,
# solo con ligeros cambios de nombre para que funcione.

@router.get("/me", response_model=UsuarioRead)
def obtener_usuario_activo(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual
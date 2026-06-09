

Implementar el modelo `Cliente` y  `Orden` en SQLAlchemy, sus schemas Pydantic, y los 5 endpoints CRUD en FastAPI.

---

## Paso 1 — Modelos SQLAlchemy (`models.py`)

Crea el modelo `Cliente` con las siguientes columnas:

- `id` — entero, primary key
- `nombre` — string de máximo 100 caracteres
- `email` — string de máximo 150 caracteres, debe ser único
- `telefono` — string de máximo 20 caracteres, **opcional** (puede ser null)
- `activo` — booleano, por defecto `True`
- `creado_en` — datetime, por defecto la fecha/hora actual


Crea el modelo `Orden` con las siguientes columnas:

- `id` — UUID, primary key, generado automáticamente con `uuid.uuid4`
- `cantidad` — entero
- `estado` — string, por defecto `"pendiente"`
- `creado_en` — datetime, por defecto la fecha/hora actual

## Paso 2 — Schemas Pydantic (`schemas.py`)

Crea los siguientes schemas:

- **`ClienteRead`** — `nombre`,`email`, `telefono`, `activo`  agrega `id` y `creado_en`. Configúralo para que pueda leer datos desde objetos SQLAlchemy.
- **`ClienteCreate`** — todos los campos excepto el  `id`.
- **`ClienteUpdate`** — todos los campos opcionales.
- **`OrdenCreate`** — todos los campos excepto el id 
- **`OrdenUpdate`** — `cantidad` y `estado`, ambos opcionales.
- **`OrdenRead`** — mismos campos que `OrdenCreate` más `id`

Puedes validar el email utilizando el tipo de Pydantic `EmailStr`

## Paso 3 — Endpoints (`routers/clientes.py`)

Crea un router con prefijo `/clientes`. Implementa estos 5 endpoints:

- **GET `/`** — devuelve la lista de todos los clientes.
- **GET `/{cliente_id}`** — devuelve un cliente por su id. Si no existe, retorna 404.
- **POST `/`** — recibe un `ClienteCreate`, crea el cliente y lo retorna. Status code 201.
- **PATCH `/{cliente_id}`** — recibe un `ClienteUpdate` y actualiza solo los campos que llegaron. Si no existe, retorna 404.
- **DELETE `/{cliente_id}`** — elimina el cliente. Si no existe, retorna 404. Status code 204, sin body.

Crea un router con prefijo `/ordenes`. Implementa estos 5 endpoints:
- **GET `/`** — devuelve la lista de todas las órdenes.
- **GET `/{orden_id}`** — devuelve una orden por su UUID. Si no existe, retorna 404.
- **POST `/`** — recibe un `OrdenCreate`, crea la orden y la retorna. Status code 201.
- **PATCH `/{orden_id}`** — recibe un `OrdenUpdate` y actualiza solo los campos que llegaron. Si no existe, retorna 404.
- **DELETE `/{orden_id}`** — elimina la orden. Si no existe, retorna 404. Status code 204, sin body.



## Paso 4 — Registrar el router

Incluye los router en `main.py` para que los endpoints queden disponibles.

## Paso 5 — Relaciones entre tablas

Agrega las siguientes relaciones:

- `Orden` → `Cliente`: **muchos a uno**. Muchas órdenes pueden pertenecer al mismo cliente. Se implementa con una foreign key `cliente_id` en `Orden`.
- `Orden` ↔ `Producto`: **muchos a muchos**. Una orden puede tener varios productos, y un producto puede aparecer en varias órdenes. Se implementa mediante una tabla intermedia.

Recuerda que puedes usar `secondary=tabla_intermedia` para indicar que la relación pasa por la tabla intermedia y back_populates para definir el lado inverso de la relación.



### Qué hacer si ya tienes datos en la tabla

Dado que la tabla Orden y Cliente ya existen se puede generar un problema, dado que `cliente_id` pertenece `Orden`. Esta columna es nueva en una tabla que ya tiene filas. Declarala como nullable para que PostgreSQL pueda agregarla sin error.

La opción más rápida es añadir la columna directamente en PostgreSQL con `ALTER TABLE`:

```sql
ALTER TABLE ordenes ADD COLUMN cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE;

ALTER TABLE ordenes ALTER COLUMN cliente_id SET NOT NULL; 

```

Luego utiliza `PATCH /ordenes/{orden_id}` para asignar el `cliente_id` a cada orden existente. Una vez que todas las filas tengan valor, puedes cambiarla a `NOT NULL`, para que a futuro no se permita tener órdenes sin cliente asignado.

`create_all()` solo **crea** tablas que no existen, no modifica las que ya existen. Si agregas una columna a un modelo, la base de datos no se entera hasta que la agregues manualmente.

### Esquemas
Actualiza los esquemas para que incluyan la información de las relaciones. Por ejemplo, `OrdenRead` debería incluir el `cliente_id` y una lista de productos asociados a esa orden. En `ClientRead` pueden incluir las órdenes asociadas. Puedes importar `ProductoRead` desde schemas.productos para usarlo en `OrdenRead`.

**Importante**: Si dos schemas se importan entre sí, se produce un error de importación circular. Para evitarlo, utiliza modelos simplificados (como ClientSimple) y/o mueve los modelos compartidos a un archivo común.

### Cambios en el router (`routers/ordenes.py`)

Al utilizar SQLAlchemy para modelar una relación muchos a muchos, la tabla intermedia no se manipula directamente desde el código, sino a través de las relaciones definidas en los modelos.

Esto permite que, al crear una orden, puedas enviar los productos desde el endpoint de órdenes (por ejemplo, como una lista de producto_ids). Luego, en el backend, esos IDs se usan para buscar los productos en la base de datos y asignarlos a la orden.

De esta forma, no necesitas insertar manualmente en la tabla intermedia: simplemente trabajas con los objetos y SQLAlchemy se encarga automáticamente de crear las relaciones.



### ON DELETE CASCADE

El `ondelete="CASCADE"` se especifica dentro de `ForeignKey`, porque es una instrucción para **PostgreSQL**. Le dice que cuando se elimine un registro padre, las filas que lo referencian se eliminen automáticamente. En la tabla `orden_producto` esto significa que si se elimina una orden, sus filas en la tabla de asociación desaparecen también, sin dejar registros huérfanos.

El `cascade="all, delete-orphan"` en el `relationship()` hace lo mismo pero desde **SQLAlchemy**: cuando eliminás un objeto desde la sesión de Python, el ORM elimina los objetos hijos antes de ejecutar el `DELETE`. Conviene tener los dos: el de PostgreSQL cubre los deletes que llegan directo a la base de datos sin pasar por la app.
"# proyecto-2-tbd" 

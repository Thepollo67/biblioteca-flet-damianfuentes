"""Endpoints CRUD de la tabla libros."""

from fastapi import APIRouter, HTTPException, Request

from backend.connect import get_conexion


router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("/")
def listar_libros():
    """Devuelve todos los registros de la tabla."""
    conexion = get_conexion()

    with conexion.cursor() as cursor:
        cursor.callproc("SP_LISTAR_LIBROS")
        #cursor.execute("SELECT * FROM libros ORDER BY id")
        libros = cursor.fetchall()

    conexion.close()
    return libros


@router.get("/{libro_id}")
def obtener_libro(libro_id: int):
    """Busca un libro mediante su id."""
    conexion = get_conexion()

    with conexion.cursor() as cursor:
        cursor.execute("SP_OBTENER_LIBRO", (libro_id,))
        libro = cursor.fetchone()

    conexion.close()

    if libro is None:
        """Endpoints CRUD de la tabla `libros`.

        Rutas ordenadas: listar -> buscar -> obtener -> crear -> actualizar -> eliminar.
        """

        from fastapi import APIRouter, HTTPException, Request

        from backend.connect import get_conexion


        router = APIRouter(prefix="/libros", tags=["Libros"])


        @router.get("/")
        def listar_libros():
            """Devuelve todos los registros de la tabla."""
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    # Usar procedimiento almacenado si existe, sino SELECT directo
                    try:
                        cursor.callproc("SP_LISTAR_LIBROS")
                        libros = cursor.fetchall()
                    except Exception:
                        cursor.execute("SELECT * FROM libros ORDER BY id")
                        libros = cursor.fetchall()
                return libros
            finally:
                conexion.close()


        @router.get("/buscar/")
        def buscar_libros(texto: str):
            """Busca libros por título, autor o género (LIKE)."""
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    texto_busqueda = f"%{texto}%"
                    cursor.execute(
                        """SELECT * FROM libros
                        WHERE titulo LIKE %s OR autor LIKE %s OR genero LIKE %s
                        ORDER BY id""",
                        (texto_busqueda, texto_busqueda, texto_busqueda),
                    )
                    return cursor.fetchall()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                conexion.close()


        @router.get("/{libro_id}")
        def obtener_libro(libro_id: int):
            """Busca un libro mediante su id."""
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT * FROM libros WHERE id = %s", (libro_id,))
                    libro = cursor.fetchone()
                    if libro is None:
                        raise HTTPException(status_code=404, detail="Libro no encontrado")
                    return libro
            finally:
                conexion.close()


        @router.post("/", status_code=201)
        async def crear_libro(request: Request):
            """Recibe JSON y crea un registro nuevo."""
            datos = await request.json()
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO libros
                            (titulo, autor, genero, anio_publicacion, ejemplares)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            datos.get("titulo"),
                            datos.get("autor"),
                            datos.get("genero"),
                            datos.get("anio_publicacion"),
                            datos.get("ejemplares"),
                        ),
                    )
                    conexion.commit()
                    nuevo_id = cursor.lastrowid
                return {"id": nuevo_id, **datos}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                conexion.close()


        @router.put("/{libro_id}")
        async def actualizar_libro(libro_id: int, request: Request):
            """Reemplaza los datos de un libro existente."""
            datos = await request.json()
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE libros
                        SET titulo = %s, autor = %s, genero = %s,
                            anio_publicacion = %s, ejemplares = %s
                        WHERE id = %s
                        """,
                        (
                            datos.get("titulo"),
                            datos.get("autor"),
                            datos.get("genero"),
                            datos.get("anio_publicacion"),
                            datos.get("ejemplares"),
                            libro_id,
                        ),
                    )
                    conexion.commit()
                    filas_afectadas = cursor.rowcount

                if filas_afectadas == 0:
                    raise HTTPException(status_code=404, detail="Libro no encontrado")

                return {"id": libro_id, **datos}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                conexion.close()


        @router.delete("/{libro_id}")
        def eliminar_libro(libro_id: int):
            """Elimina un libro mediante su id."""
            conexion = get_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))
                    conexion.commit()
                    filas_afectadas = cursor.rowcount

                if filas_afectadas == 0:
                    raise HTTPException(status_code=404, detail="Libro no encontrado")

                return {"mensaje": "Libro eliminado correctamente"}
            finally:
                conexion.close()


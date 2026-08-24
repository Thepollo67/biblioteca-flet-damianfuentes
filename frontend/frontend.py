import ssl

# Bypasear verificación SSL para permitir la descarga de recursos de Flet
ssl._create_default_https_context = ssl._create_unverified_context

import threading
import flet as ft
import requests

# CONFIGURACIÓN
API_URL = "http://127.0.0.1:8000/libros/"


def main(page: ft.Page):
    # Configuración de la ventana.
    page.title = "Biblioteca"
    page.padding = 30
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#121212"

    libro_id_en_edicion = None

    # TEXTO PARA AVISOS
    lbl_mensaje = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

    # FORMULARIO
    txt_titulo = ft.TextField(label="titulo", expand=True)
    txt_autor = ft.TextField(label="autor", expand=True)
    txt_genero = ft.TextField(label="genero", expand=True)
    txt_anio = ft.TextField(label="anio_publicacion", expand=True)
    txt_ejemplares = ft.TextField(label="ejemplares", expand=True)
    txt_buscar = ft.TextField(label="Buscar libro", prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.BLUE_GREY_600,)
    # TABLA
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Título")),
            ft.DataColumn(ft.Text("Autor")),
            ft.DataColumn(ft.Text("Género")),
            ft.DataColumn(ft.Text("Año")),
            ft.DataColumn(ft.Text("Ejemplares")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )

    # FUNCIONES
    def mostrar_mensaje(texto, es_error=False):
        lbl_mensaje.value = texto
        lbl_mensaje.color = "#FF5252" if es_error else "#4CAF50"
        page.update()

    def limpiar_formulario():
        nonlocal libro_id_en_edicion
        libro_id_en_edicion = None
        txt_titulo.value = ""
        txt_autor.value = ""
        txt_genero.value = ""
        txt_anio.value = ""
        txt_ejemplares.value = ""
        btn_guardar.text = "Guardar libro"
        page.update()

    def buscar_libros(e):

        texto = txt_buscar.value.strip()
        if not texto:
             mostrar_mensaje("Por favor, ingresa un texto para buscar.", es_error=True)
             return

        try:
            respuesta = requests.get(
                f"{API_URL}buscar/",
                params={"texto" : texto},
                timeout=5,
            )
            respuesta.raise_for_status()
            libros = respuesta.json()
            tabla.rows.clear()
            for libro in libros:
                fila = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(libro["id"]))),
                        ft.DataCell(ft.Text(str(libro["titulo"]))),
                        ft.DataCell(ft.Text(str(libro["autor"]))),
                        ft.DataCell(ft.Text(str(libro["genero"]))),
                        ft.DataCell(ft.Text(str(libro["anio_publicacion"]))),
                        ft.DataCell(ft.Text(str(libro["ejemplares"]))),
                    ]

                )
                tabla.rows.append(fila)
            page.update()

            if not libros:
                mostrar_mensaje("No se encontraron libros que coincidan con la búsqueda.", es_error=True)
        except requests.exceptions.RequestException:
            mostrar_mensaje("Error al buscar los libros", es_error=True)

    def mostrar_todo():
        txt_buscar.value = ""
        cargar_libros()

    # botones y layout principales se añaden más abajo después de definir todas las funciones


    def cargar_datos_para_editar(libro):
        nonlocal libro_id_en_edicion
        libro_id_en_edicion = libro["id"]
        txt_titulo.value = str(libro.get("titulo", ""))
        txt_autor.value = str(libro.get("autor", ""))
        txt_genero.value = str(libro.get("genero", ""))
        txt_anio.value = str(libro.get("anio_publicacion", ""))
        txt_ejemplares.value = str(libro.get("ejemplares", ""))
        btn_guardar.text = "Actualizar libro"
        page.update()

    # ELIMINAR LIBRO
    def eliminar_libro_click(libro_id):
        try:
            respuesta = requests.delete(
                f"{API_URL.rstrip('/')}/{libro_id}", timeout=5
            )

            if respuesta.status_code == 200:
                mostrar_mensaje("Libro eliminado correctamente")
                cargar_libros()
            else:
                mostrar_mensaje("Error al eliminar el libro", True)

        except requests.ConnectionError:
            mostrar_mensaje("No se puede conectar a la API", True)

    # CARGAR LIBROS
    def cargar_libros():
        try:
            respuesta = requests.get(API_URL, timeout=5)
            respuesta.raise_for_status()
           

            libros = respuesta.json()
            tabla.rows.clear()

            for libro in libros:
                btn_update = ft.ElevatedButton(
                    "Editar",
                    bgcolor="#FFC107",
                    color="#000000",
                    on_click=lambda e, l=libro: cargar_datos_para_editar(l),
                )

                btn_delete = ft.ElevatedButton(
                    "Eliminar",
                    bgcolor="#D32F2F",
                    color="#FFFFFF",
                    on_click=lambda e, id_l=libro[
                        "id"
                    ]: eliminar_libro_click(id_l),
                )

                tabla.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(libro["id"]))),
                            ft.DataCell(ft.Text(str(libro["titulo"]))),
                            ft.DataCell(ft.Text(str(libro["autor"]))),
                            ft.DataCell(ft.Text(str(libro["genero"]))),
                            ft.DataCell(
                                ft.Text(str(libro["anio_publicacion"]))
                            ),
                            ft.DataCell(ft.Text(str(libro["ejemplares"]))),
                            ft.DataCell(ft.Row([btn_update, btn_delete])),
                        ]
                    )
                )

            page.update()

        except requests.exceptions.RequestException:
            mostrar_mensaje("Error al cargar los libros", True)

    # CREAR O ACTUALIZAR
    def obtener_datos_formulario():
        return {
            "titulo": txt_titulo.value,
            "autor": txt_autor.value,
            "genero": txt_genero.value,
            "anio_publicacion": txt_anio.value,
            "ejemplares": txt_ejemplares.value,
        }

    def crear_o_actualizar_libro(e):
        if not txt_titulo.value or not txt_autor.value:
            mostrar_mensaje("Complete los datos obligatorios", True)
            return

        datos = obtener_datos_formulario()

        try:
            if libro_id_en_edicion is None:
                respuesta = requests.post(API_URL, json=datos, timeout=60)

                if respuesta.status_code == 201:
                    mostrar_mensaje("Libro creado exitosamente")
                    limpiar_formulario()
                    cargar_libros()
                else:
                    mostrar_mensaje("Error al crear el libro", True)

            else:
                url = f"{API_URL.rstrip('/')}/{libro_id_en_edicion}"

                respuesta = requests.put(url, json=datos, timeout=50)

                if respuesta.status_code == 200:
                    mostrar_mensaje("Libro actualizado exitosamente")
                    limpiar_formulario()
                    cargar_libros()
                else:
                    mostrar_mensaje("Error al actualizar el libro", True)

        except requests.ConnectionError:
            mostrar_mensaje("No se puede conectar a la API", True)

    # BOTONES
    btn_guardar = ft.Button(
        "Guardar libro",
        on_click=crear_o_actualizar_libro,
        bgcolor="#1976D2",
        color="#FFFFFF",
    )

    btn_limpiar = ft.OutlinedButton(
        "Limpiar", on_click=lambda e: limpiar_formulario()
    )

    # INTERFAZ
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Biblioteca Azteca",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color="#42A5F5",
                    ),
                    ft.Text(
                        "Sistema de gestión de libros", color="#BDBDBD"
                    ),
                ]
            ),
            padding=20,
            bgcolor="#1E1E1E",
            border_radius=15,
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Registrar libro",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    lbl_mensaje,
                    ft.Row([txt_titulo, txt_autor]),
                    ft.Row([txt_genero, txt_anio, txt_ejemplares]),
                    ft.Row([btn_guardar, btn_limpiar]),
                ]
            ),
            padding=25,
            bgcolor="#1E1E1E",
            border_radius=15,
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Libros registrados",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row([tabla], scroll=ft.ScrollMode.AUTO),
                ]
            ),
            padding=25,
            bgcolor="#1E1E1E",
            border_radius=15,
        ),
    )
    cargar_libros()
    # Carga los libros al iniciar (en segundo plano para arranque rápido)
    threading.Thread(target=cargar_libros, daemon=True).start()


if __name__ == "__main__":
    ft.run(main)

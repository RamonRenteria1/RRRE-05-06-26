import flet as ft
import mysql.connector
import hashlib

DB_SERVER = {
    "host": "localhost",
    "user": "root",
    "password": ""
}

DB_NAME = "crud_alumnos_leyva"



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



def crear_base_y_tablas():
    conn = mysql.connector.connect(**DB_SERVER)
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            usuario VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            matricula VARCHAR(20) PRIMARY KEY,
            apellido_paterno VARCHAR(80),
            apellido_materno VARCHAR(80),
            nombres VARCHAR(100),
            curp VARCHAR(18),
            especialidad VARCHAR(100),
            telefono VARCHAR(10),
            ciudad_origen VARCHAR(100),
            estado VARCHAR(100),
            disciplina VARCHAR(100),
            foto VARCHAR(255)
        )
    """)

    try:
        cursor.execute("ALTER TABLE alumnos ADD COLUMN foto VARCHAR(255)")
    except:
        pass

    cursor.execute("""
        INSERT IGNORE INTO usuarios(nombre, usuario, password)
        VALUES (%s, %s, %s)
    """, ("Administrador Leyva", "admin", hash_password("Admin123")))

    conn.commit()
    conn.close()



def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database=DB_NAME
    )


def main(page: ft.Page):
    page.title = "CRUD Alumnos Leyva"
    page.bgcolor = "#0B1120"
    page.window_width = 1200
    page.window_height = 750
    page.scroll = "auto"

    AZUL = "#00B4D8"
    TARJETA = "#111827"
    BLANCO = "#1F2937"
    VERDE = "#16A34A"
    ROJO = "#DC2626"

    usuario_actual = {"id": None, "nombre": None}

    estados = [
        "Chihuahua", "Durango", "Sonora", "Coahuila", "Nuevo León",
        "Jalisco", "CDMX", "Estado de México", "Sinaloa", "Veracruz"
    ]

    disciplinas = [
        "Fútbol", "Basquetbol", "Voleibol", "Béisbol", "Atletismo",
        "Box", "Natación", "Ninguna"
    ]

    especialidades = [
        "Programación", "Electrónica", "Recursos Humanos", "Secretariado Bilingüe"
    ]

    def opcion_negra(texto):
        return ft.dropdown.Option(
            texto,
            content=ft.Text(texto, color="white")
        )

    def limpiar():
        page.controls.clear()

    def mostrar_mensaje(label, texto, color):
        label.value = texto
        label.color = color
        page.update()

    def solo_numeros(campo, maximo):
        nuevo = ""
        for letra in campo.value:
            if letra.isdigit():
                nuevo += letra

        campo.value = nuevo[:maximo]
        page.update()

    def solo_letras(campo):
        permitido = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZÁÉÍÓÚabcdefghijklmnñopqrstuvwxyzáéíóú "
        nuevo = ""

        for letra in campo.value:
            if letra in permitido:
                nuevo += letra

        campo.value = nuevo
        page.update()

    
    def mostrar_login():
        limpiar()

        lbl = ft.Text("", size=14)

        txt_usuario = ft.TextField(label="Usuario", width=320, bgcolor=BLANCO, color="white")
        txt_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            bgcolor=BLANCO,
            color="white"
        )

        def login(e):
            if not txt_usuario.value or not txt_password.value:
                mostrar_mensaje(lbl, "Completa usuario y contraseña", ROJO)
                return
            
            try:
                conn = conectar()
                cursor = conn.cursor(dictionary=True)

                cursor.execute(
                    "SELECT * FROM usuarios WHERE usuario=%s AND password=%s",
                    (txt_usuario.value, hash_password(txt_password.value))
                )

                user = cursor.fetchone()
                conn.close()

                if user:
                    usuario_actual["id"] = user["id"]
                    usuario_actual["nombre"] = user["nombre"]
                    mostrar_panel()
                else:
                    mostrar_mensaje(lbl, "Usuario o contraseña incorrectos", ROJO)

            except:
                mostrar_mensaje(lbl, "Ocurrió un error al iniciar sesión", ROJO)

        page.add(
            ft.Container(
                bgcolor=TARJETA,
                padding=35,
                border_radius=15,
                margin=40,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Sistema CRUD Alumnos", size=32, weight="bold", color=AZUL),
                        ft.Text("Inicia sesión para continuar", color="#FFFFFF"),
                        ft.Container(height=15),
                        txt_usuario,
                        txt_password,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Button("Iniciar sesión", on_click=login),
                                ft.Button("Crear cuenta", on_click=lambda e: mostrar_registro())
                            ]
                        ),
                        lbl
                    ]
                )
            )
        )
        page.update()

    
    def mostrar_registro():
        limpiar()

        lbl = ft.Text("", size=14)

        reg_nombre = ft.TextField(label="Nombre completo", width=320, bgcolor=BLANCO, color="white")
        reg_usuario = ft.TextField(label="Usuario", width=320, bgcolor=BLANCO, color="white")
        reg_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            bgcolor=BLANCO,
            color="white"
        )
        reg_confirmar = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            bgcolor=BLANCO,
            color="white"
        )

        def guardar_cuenta(e):
            if not reg_nombre.value or not reg_usuario.value or not reg_password.value:
                mostrar_mensaje(lbl, "Llena todos los campos", ROJO)
                return

            if reg_password.value != reg_confirmar.value:
                mostrar_mensaje(lbl, "Las contraseñas no coinciden", ROJO)
                return

            try:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO usuarios(nombre, usuario, password) VALUES(%s,%s,%s)",
                    (reg_nombre.value, reg_usuario.value, hash_password(reg_password.value))
                )

                conn.commit()
                conn.close()

                mostrar_login()

            except mysql.connector.IntegrityError:
                mostrar_mensaje(lbl, "Ese usuario ya existe", ROJO)
            except:
                mostrar_mensaje(lbl, "Ocurrió un error", ROJO)

        page.add(
            ft.Container(
                bgcolor=TARJETA,
                padding=35,
                border_radius=15,
                margin=40,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Crear cuenta", size=32, weight="bold", color=AZUL),
                        ft.Text("Registra un usuario para entrar al sistema", color="#FFFFFF"),
                        ft.Container(height=15),
                        reg_nombre,
                        reg_usuario,
                        reg_password,
                        reg_confirmar,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Button("Registrar", on_click=guardar_cuenta),
                                ft.Button("Volver", on_click=lambda e: mostrar_login())
                            ]
                        ),
                        lbl
                    ]
                )
            )
        )
        page.update()

    def mostrar_panel():
        limpiar()

        matricula_original = [""]

        lbl = ft.Text("", size=16, weight="bold")

        matricula = ft.TextField(label="Matrícula", width=180, bgcolor=BLANCO, color="white")
        ap_paterno = ft.TextField(label="Apellido paterno", width=220, bgcolor=BLANCO, color="white")
        ap_materno = ft.TextField(label="Apellido materno", width=220, bgcolor=BLANCO, color="white")
        nombres = ft.TextField(label="Nombre(s)", width=250, bgcolor=BLANCO, color="white")
        curp = ft.TextField(label="CURP", width=250, bgcolor=BLANCO, color="white")
        especialidad = ft.Dropdown(
        label="Especialidad",
        width=250,
        bgcolor=BLANCO,
        color="white",
        text_style=ft.TextStyle(color="white"),
        options=[opcion_negra(e) for e in especialidades]
)
        telefono = ft.TextField(label="Teléfono", width=180, bgcolor=BLANCO, color="white")
        ciudad = ft.TextField(label="Ciudad de origen", width=230, bgcolor=BLANCO, color="white")

        foto = ft.TextField(label="Ruta o link de foto", width=350, bgcolor=BLANCO, color="white")
        imagen_foto = ft.Container(
            width=100,
            height=100,
            bgcolor="#1F2937",
            border_radius=5,
            content=ft.Text("Sin foto", color="gray", size=12)
        )

        def mostrar_foto(e):
            if not foto.value:
                mostrar_mensaje(lbl, "Escribe la ruta o link de la foto", ROJO)
                return

            foto_minuscula = foto.value.lower()

            if not (foto_minuscula.endswith(".jpg") or foto_minuscula.endswith(".jpeg") or foto_minuscula.endswith(".png")):
                mostrar_mensaje(lbl, "La imagen debe terminar en .jpg, .jpeg o .png", ROJO)
                return

            imagen_foto.content = ft.Image(src=foto.value, width=100, height=100, fit="contain")
            mostrar_mensaje(lbl, "Foto cargada", VERDE)
            page.update()

        telefono.on_change = lambda e: solo_numeros(telefono, 10)
        ap_paterno.on_change = lambda e: solo_letras(ap_paterno)
        ap_materno.on_change = lambda e: solo_letras(ap_materno)
        nombres.on_change = lambda e: solo_letras(nombres)
        ciudad.on_change = lambda e: solo_letras(ciudad)

        estado = ft.Dropdown(
        label="Estado",
        width=230,
        bgcolor=BLANCO,
        color="white",
        text_style=ft.TextStyle(color="white"),
        options=[opcion_negra(e) for e in estados]
)

        disciplina = ft.Dropdown(
        label="Disciplina deportiva",
        width=230,
        bgcolor=BLANCO,
        color="white",
        text_style=ft.TextStyle(color="white"),
        options=[opcion_negra(d) for d in disciplinas]
    )

        buscar = ft.TextField(label="Buscar por matrícula o apellido", width=330, bgcolor=BLANCO, color="white")

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Matrícula", color=AZUL)),
                ft.DataColumn(ft.Text("Nombre", color=AZUL)),
                ft.DataColumn(ft.Text("CURP", color=AZUL)),
                ft.DataColumn(ft.Text("Teléfono", color=AZUL)),
                ft.DataColumn(ft.Text("Estado", color=AZUL)),
                ft.DataColumn(ft.Text("Disciplina", color=AZUL)),
                ft.DataColumn(ft.Text("Foto", color=AZUL)),
            ],
            rows=[]
        )

        def limpiar_campos():
            matricula.disabled = False
            matricula_original[0] = ""

            matricula.value = ""
            ap_paterno.value = ""
            ap_materno.value = ""
            nombres.value = ""
            curp.value = ""
            especialidad.value = ""
            telefono.value = ""
            ciudad.value = ""
            foto.value = ""
            imagen_foto.content = ft.Text("Sin foto", color="gray", size=12)
            estado.value = None
            disciplina.value = None

            page.update()

        
        def cargar_alumnos(filtro=""):
            try:
                conn = conectar()
                cursor = conn.cursor(dictionary=True)

                if filtro:
                    cursor.execute("""
                        SELECT * FROM alumnos
                        WHERE matricula LIKE %s OR apellido_paterno LIKE %s
                    """, (f"%{filtro}%", f"%{filtro}%"))
                else:
                    cursor.execute("SELECT * FROM alumnos")

                datos = cursor.fetchall()
                conn.close()

                tabla.rows.clear()

                for a in datos:
                    nombre_completo = str(a["nombres"]) + " " + str(a["apellido_paterno"])
                    
                    celda_foto = ft.DataCell(ft.Text("Sin foto", color="gray", size=10))
                    
                    if a.get("foto") and a["foto"].strip():
                        try:
                            foto_url = a["foto"].lower()
                            if foto_url.endswith(".jpg") or foto_url.endswith(".jpeg") or foto_url.endswith(".png"):
                                celda_foto = ft.DataCell(
                                    ft.Container(
                                        width=50,
                                        height=50,
                                        border_radius=5,
                                        content=ft.Image(src=a["foto"], width=50, height=50, fit="cover")
                                    )
                                )
                        except Exception as ex:
                            print(f"Error al cargar foto de {a['matricula']}: {str(ex)}")
                            celda_foto = ft.DataCell(ft.Text("Sin foto", color="gray", size=10))

                    tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(a["matricula"]), color="#FFFFFF")),
                                ft.DataCell(ft.Text(nombre_completo, color="#FFFFFF")),
                                ft.DataCell(ft.Text(str(a["curp"]), color="#FFFFFF")),
                                ft.DataCell(ft.Text(str(a["telefono"]), color="#FFFFFF")),
                                ft.DataCell(ft.Text(str(a["estado"]), color="#FFFFFF")),
                                ft.DataCell(ft.Text(str(a["disciplina"]), color="#FFFFFF")),
                                celda_foto,
                            ],
                            on_select_change=lambda e, alumno=a: seleccionar_alumno(alumno)
                        )
                    )

                page.update()

            except:
                mostrar_mensaje(lbl, "Error al cargar alumnos", ROJO)

        # Carga los datos del alumno seleccionado al formulario
        def seleccionar_alumno(a):
            matricula_original[0] = a["matricula"]
            matricula.value = a["matricula"]
            matricula.disabled = False
            ap_paterno.value = a["apellido_paterno"]
            ap_materno.value = a["apellido_materno"]
            nombres.value = a["nombres"]
            curp.value = a["curp"]
            especialidad.value = a["especialidad"]
            telefono.value = a["telefono"]
            ciudad.value = a["ciudad_origen"]
            estado.value = a["estado"]
            disciplina.value = a["disciplina"]
            
            if a.get("foto"):
                foto.value = a["foto"]
                imagen_foto.content = ft.Image(src=a["foto"], width=100, height=100, fit="contain")
            else:
                foto.value = ""
                imagen_foto.content = ft.Text("Sin foto", color="gray", size=12)
            
            page.update()

        # Revisa que los datos estén correctos
        def validar_campos():
            if not matricula.value:
                mostrar_mensaje(lbl, "Falta la matrícula", ROJO)
                return False

            if not ap_paterno.value:
                mostrar_mensaje(lbl, "Falta el apellido paterno", ROJO)
                return False

            if not nombres.value:
                mostrar_mensaje(lbl, "Falta el nombre", ROJO)
                return False

            if not curp.value:
                mostrar_mensaje(lbl, "Falta la CURP", ROJO)
                return False

            curp.value = curp.value.upper()

            if len(curp.value) != 18:
                mostrar_mensaje(lbl, "La CURP debe tener 18 caracteres", ROJO)
                return False

            if len(telefono.value) != 10:
                mostrar_mensaje(lbl, "El teléfono debe tener 10 dígitos", ROJO)
                return False

            if especialidad.value is None:
                mostrar_mensaje(lbl, "Selecciona una especialidad", ROJO)
                return False

            if estado.value is None:
                mostrar_mensaje(lbl, "Selecciona un estado", ROJO)
                return False

            if disciplina.value is None:
                mostrar_mensaje(lbl, "Selecciona una disciplina", ROJO)
                return False

            if foto.value:
                foto_minuscula = foto.value.lower()

                if not (foto_minuscula.endswith(".jpg") or foto_minuscula.endswith(".jpeg") or foto_minuscula.endswith(".png")):
                    mostrar_mensaje(lbl, "La imagen debe terminar en .jpg, .jpeg o .png", ROJO)
                    return False

            return True

        # Guardar alumno nuevo
        # Guarda un alumno nuevo
        def insertar(e):
            if not validar_campos():
                return

            try:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO alumnos (
                        matricula,
                        apellido_paterno,
                        apellido_materno,
                        nombres,
                        curp,
                        especialidad,
                        telefono,
                        ciudad_origen,
                        estado,
                        disciplina,
                        foto
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    matricula.value,
                    ap_paterno.value,
                    ap_materno.value,
                    nombres.value,
                    curp.value.upper(),
                    especialidad.value,
                    telefono.value,
                    ciudad.value,
                    estado.value,
                    disciplina.value,
                    foto.value if foto.value else None
                ))

                conn.commit()
                conn.close()

                mostrar_mensaje(lbl, "Alumno registrado correctamente", VERDE)
                limpiar_campos()
                cargar_alumnos()

            except mysql.connector.IntegrityError:
                mostrar_mensaje(lbl, "Esa matrícula ya existe", ROJO)
            except:
                mostrar_mensaje(lbl, "Error al insertar", ROJO)

        # Modificar alumno seleccionado
        # Actualiza el alumno seleccionado
        def actualizar(e):
            if matricula_original[0] == "":
                mostrar_mensaje(lbl, "Selecciona un alumno de la tabla", ROJO)
                return

            if not validar_campos():
                return

            try:
                conn = conectar()
                cursor = conn.cursor()

                matricula_buscar = matricula_original[0]

                if matricula_buscar == "":
                    matricula_buscar = matricula.value

                cursor.execute("""
                    UPDATE alumnos SET
                    matricula=%s,
                    apellido_paterno=%s,
                    apellido_materno=%s,
                    nombres=%s,
                    curp=%s,
                    especialidad=%s,
                    telefono=%s,
                    ciudad_origen=%s,
                    estado=%s,
                    disciplina=%s,
                    foto=%s
                    WHERE matricula=%s
                """, (
                    matricula.value,
                    ap_paterno.value,
                    ap_materno.value,
                    nombres.value,
                    curp.value.upper(),
                    especialidad.value,
                    telefono.value,
                    ciudad.value,
                    estado.value,
                    disciplina.value,
                    foto.value if foto.value else None,
                    matricula_buscar
                ))

                conn.commit()
                conn.close()

                mostrar_mensaje(lbl, "Alumno actualizado correctamente", VERDE)
                limpiar_campos()
                cargar_alumnos()

            except:
                mostrar_mensaje(lbl, "Error al actualizar", ROJO)

        def borrar_confirmado(e):
            confirmar_borrar.visible = False

            try:
                conn = conectar()
                cursor = conn.cursor()

                matricula_borrar = matricula_original[0]

                if matricula_borrar == "":
                    matricula_borrar = matricula.value

                cursor.execute("DELETE FROM alumnos WHERE matricula=%s", (matricula_borrar,))
                conn.commit()

                if cursor.rowcount > 0:
                    mostrar_mensaje(lbl, "Alumno eliminado correctamente", VERDE)
                else:
                    mostrar_mensaje(lbl, "No se encontró la matrícula", ROJO)

                conn.close()
                limpiar_campos()
                cargar_alumnos()

            except:
                mostrar_mensaje(lbl, "Error al borrar", ROJO)

        def cancelar_borrar(e):
            confirmar_borrar.visible = False
            mostrar_mensaje(lbl, "Borrado cancelado", AZUL)

        confirmar_borrar = ft.Row(
            visible=False,
            controls=[
                ft.Text("¿Seguro que quieres borrar este alumno?", color="#FFFFFF"),
                ft.Button("Sí, borrar", on_click=borrar_confirmado),
                ft.Button("Cancelar", on_click=cancelar_borrar)
            ]
        )

        def borrar(e):
            if not matricula.value:
                mostrar_mensaje(lbl, "Selecciona un alumno o escribe la matrícula", ROJO)
                return

            confirmar_borrar.visible = True
            mostrar_mensaje(lbl, "Confirma el borrado", AZUL)

        def cerrar_sesion(e):
            usuario_actual["id"] = None
            usuario_actual["nombre"] = None
            mostrar_login()

        page.add(
            ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor=TARJETA,
                            padding=15,
                            border_radius=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Bienvenido, " + usuario_actual["nombre"], size=24, weight="bold", color=AZUL),
                                    ft.Button("Cerrar sesión", on_click=cerrar_sesion)
                                ]
                            )
                        ),

                        ft.Container(height=10),

                        ft.Container(
                            bgcolor=TARJETA,
                            padding=15,
                            border_radius=10,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Registro de Alumno", size=24, weight="bold", color=AZUL),
                                    ft.Row([matricula, ap_paterno, ap_materno, nombres], wrap=True),
                                    ft.Row([curp, especialidad, telefono, ciudad], wrap=True),
                                    ft.Row([estado, disciplina], wrap=True),
                                    ft.Row([
                                        foto,
                                        ft.Button("Mostrar foto", on_click=mostrar_foto),
                                        imagen_foto
                                    ], wrap=True),
                                    ft.Row([
                                        ft.Button("Insertar", on_click=insertar),
                                        ft.Button("Modificar", on_click=actualizar),
                                        ft.Button("Borrar", on_click=borrar),
                                        ft.Button("Limpiar", on_click=lambda e: limpiar_campos()),
                                    ]),
                                    lbl,
                                    confirmar_borrar
                                ]
                            )
                        ),

                        ft.Container(height=10),

                        ft.Container(
                            bgcolor=TARJETA,
                            padding=15,
                            border_radius=10,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Alumnos registrados", size=24, weight="bold", color=AZUL),
                                    ft.Row([
                                        buscar,
                                        ft.Button("Buscar", on_click=lambda e: cargar_alumnos(buscar.value)),
                                        ft.Button("Mostrar todos", on_click=lambda e: cargar_alumnos())
                                    ]),
                                    tabla
                                ]
                            )
                        )
                    ]
                )
            )
        )

        page.update()
        cargar_alumnos()

    try:
        crear_base_y_tablas()
        mostrar_login()
    except:
        page.add(ft.Text("Error al iniciar el sistema", color="red", size=20))
        page.update()


ft.run(main)
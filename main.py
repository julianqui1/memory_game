import flet as ft
from logic import memory_card
from audio import SoundManager
import asyncio
from flet import AnimatedSwitcher, Animation
import os
import sys

def ruta_recurso(rel_path):
    """Devuelve la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

async def main(page: ft.Page):
    page.title = "Juego de Memoria"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#1e1e1e"
    page.padding = 20
    page.window.width = 1200  # Ancho deseado en píxeles
    page.window.height = 800  # Alto deseado en píxeles

    # Volver a la pantalla de inicio
    def volver_a_inicio(e=None):
        page.views.clear()
        page.views.append(vista_inicio)
        page.go("/")

    # ------------------------------
    # FUNCION PARA INICIAR EL JUEGO
    # ------------------------------
    def ir_a_juego(nivel):
        if nivel == "nivel1":
            assets = [ruta_recurso(f"assets/cards/{letra}.jpg") if letra not in ["G", "H", "J"] else ruta_recurso(f"assets/cards/{letra}.gif")
                      for letra in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]]
        elif nivel == "nivel2":
            assets = [ruta_recurso(f"assets/cards/{letra}.jpg") if letra not in ["RR", "S", "Z", "Ñ"] else ruta_recurso(f"assets/cards/{letra}.gif")
                      for letra in ["O", "P", "Q", "R", "RR", "S", "T", "U", "V", "W", "X", "Y", "Z", "Ñ"]]
        else:
            assets = []

        game = memory_card(assets)
        sound = SoundManager()
        sonido_activo = True

        titulo = ft.Text("Juego de Memoria", size=40, color="white", font_family="Bungee Inline")

        def actualizar_tablero():
            botones = []
            for i, card in enumerate(game.cards):
                if card.revealed or card.matched:
                    letra = card.asset.split("/")[-1][0]  # Extrae la letra del nombre del archivo
                    contenido = ft.Column(
                        controls=[
                            ft.Image(src=card.asset, width=90, height=90, fit=ft.ImageFit.CONTAIN),
                            ft.Text(letra, size=15, color="white", weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                else:
                    contenido = ft.Text("❓", size=30, color="white")


                async def manejar_click(e, i=i):
                    await click_carta(i)

                btn = ft.ElevatedButton(
                    content=AnimatedSwitcher(
                        content=contenido,
                        transition=Animation(duration=300, curve="easeInOut"),
                        switch_in_curve="easeInOut",
                        switch_out_curve="easeInOut"
                    ),
                    width=120,
                    height=120,
                    disabled=card.matched,
                    on_click=manejar_click,
                    style=ft.ButtonStyle(
                        bgcolor="#446DFF",
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        shadow_color="rgba(0,0,0,0.4)",
                        elevation=4,
                        overlay_color="rgba(255,255,255,0.1)",
                        animation_duration=300,
                    )
                )
                botones.append(btn)
            return botones

        async def click_carta(index):
            if game.locked:
                return

            # Revela la carta y actualiza UI
            game.cards[index].reveal()
            tablero.controls = actualizar_tablero()
            page.update()
            await asyncio.sleep(0.3)

            # Asigna cartas seleccionadas
            if not game.first_card:
                game.first_card = game.cards[index]
            elif not game.second_card and game.cards[index] != game.first_card:
                game.second_card = game.cards[index]

                matched = await game.check_match()

                if matched:
                    print("✅ Pareja encontrada")
                    if sonido_activo:
                        sound.play_success()
                else:
                    print("❌ No coinciden")
                    if sonido_activo:
                        sound.play_fail()

            # Verifica si ya se ganó el juego
            if game.is_finished():
                titulo.value = "¡Ganaste! 🎉"
                if sonido_activo:
                    sound.play_victory()

            tablero.controls = actualizar_tablero()
            page.update()

        tablero = ft.Row(
            controls=actualizar_tablero(),
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            width=11 * 100,  # 7 columnas aprox (ajustable)
            spacing=30
        )

        salir_btn = ft.TextButton(
            "Salir",
            on_click=volver_a_inicio,
            style=ft.ButtonStyle(
                color="white"
            )
        )

        icono_sonido = ft.IconButton(
            icon=ft.Icons.VOLUME_UP,
            icon_size=30,
            tooltip="Desactivar sonido",
            on_click=lambda e: toggle_sonido()
        )

        def toggle_sonido():
            nonlocal sonido_activo
            sonido_activo = not sonido_activo

            if sonido_activo:
                icono_sonido.icon = ft.Icons.VOLUME_UP
                icono_sonido.tooltip = "Desactivar sonido"
            else:
                icono_sonido.icon = ft.Icons.VOLUME_OFF
                icono_sonido.tooltip = "Activar sonido"

            page.update()

        vista_juego = ft.View(
            "/juego",
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[icono_sonido, salir_btn],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                        ft.Container(height=20),
                        ft.Column(
                            controls=[
                                titulo,
                                ft.Container(height=30),
                                tablero
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.START,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.START,
        )

        page.views.append(vista_juego)
        page.go("/juego")

    # ------------------------------
    # FUNCION PARA PANTALLA DE NIVELES
    # ------------------------------
    def ir_a_niveles(e):
        nivel1_btn = ft.ElevatedButton(
            text="Nivel 1 (A - N)",
            width=300,
            height=60,
            bgcolor="#446DFF",
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline")),
            on_click=lambda e: ir_a_juego("nivel1")
        )

        nivel2_btn = ft.ElevatedButton(
            text="Nivel 2 (O - Z)",
            width=300,
            height=60,
            bgcolor="#446DFF",
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline")),
            on_click=lambda e: ir_a_juego("nivel2")
        )

        volver_btn = ft.IconButton(icon=ft.Icons.ARROW_BACK,
          icon_size=30,
          tooltip="Volver",
          on_click=volver_a_inicio,
          style=ft.ButtonStyle(color=ft.Colors.WHITE )
          )
        
        vista_niveles = ft.View(
    "/niveles",
    controls=[
        ft.Row(  # Botón "Volver" alineado a la derecha
            controls=[ft.Container(expand=True), volver_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        ft.Column(
            [
                ft.Text("Selecciona un nivel", size=40, color="white", font_family="Bungee Inline"),
                ft.Container(height=30),
                nivel1_btn,
                ft.Container(height=10),
                nivel2_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
    ],
    vertical_alignment=ft.MainAxisAlignment.START,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER
)


        page.views.append(vista_niveles)
        page.go("/niveles")

    # ------------------------------
    # PANTALLA DE INICIO
    # ------------------------------
    salir_btn = ft.Container(
        content=ft.TextButton(
            content=ft.Text(
                "x",
                size=60,
                font_family="Bungee Inline",
                color=ft.Colors.WHITE
            ),
            width=100,
            height=100,
            on_click=lambda e: page.window.close(),
            style=ft.ButtonStyle(
                bgcolor="transparent",
                overlay_color="transparent",
                shape=None
            )
        ),
        padding=10
    )

    salir_row = ft.Row(
        controls=[ft.Container(expand=True), salir_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    titulo = ft.Text(
        "Bienvenido",
        size=60,
        weight=ft.FontWeight.BOLD,
        font_family="Bungee Inline",
        color="white"
    )

    boton1 = ft.ElevatedButton(
        "Jugar",
        width=200,
        height=60,
        bgcolor="#446DFF",
        color=ft.Colors.WHITE,
        on_click=lambda e: ir_a_juego("nivel1"),
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline"))
    )

    boton2 = ft.ElevatedButton(
        "Niveles",
        width=200,
        height=60,
        bgcolor="#446DFF",
        color=ft.Colors.WHITE,
        on_click=ir_a_niveles,
        style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline"))
    )

    botones = ft.Row(
        controls=[boton1, boton2],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    vista_inicio = ft.View(
        "/",
        [
            salir_row,
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(height=75),
                        titulo,
                        ft.Container(height=30),
                        botones
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

    page.views.append(vista_inicio)
    page.go("/")

ft.app(target=main,view=ft.AppView.FLET_APP)

import flet as ft
from logic import memory_card
from audio import SoundManager
import asyncio

async def main(page: ft.Page):
    page.title = "Juego de Memoria"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#1e1e1e"
    page.padding = 20

    #Volver a la pantalla de inicio
    def volver_a_inicio(e=None):
        page.views.clear()
        page.views.append(vista_inicio)
        page.go("/")

    # ------------------------------
    # FUNCION PARA INICIAR EL JUEGO
    # ------------------------------
    def ir_a_juego(e):
        #assets = ["🍎", "🍌", "🍇", "🍉", "🍍", "🥝", "🍓", "🍑", "🍒", "🍈", "🥥", "🍏"]
        assets = ["assets/cards/A.jpg","assets/cards/B.jpg","assets/cards/C.jpg","assets/cards/D.jpg","assets/cards/E.jpg","assets/cards/F.jpg","assets/cards/G.gif","assets/cards/H.gif","assets/cards/I.jpg","assets/cards/J.gif","assets/cards/K.jpg","assets/cards/L.jpg","assets/cards/M.jpg","assets/cards/N.jpg"]
        game = memory_card(assets)
        sound = SoundManager()
        sonido_activo = True

        titulo = ft.Text("Juego de Memoria", size=40, color="white", font_family="Bungee Inline")

        def actualizar_tablero():
            botones = []
            for i, card in enumerate(game.cards):
                if card.revealed or card.matched:
                    contenido = ft.Image(src=card.asset, width=140, height=140, fit=ft.ImageFit.CONTAIN)
                else:
                    contenido = ft.Text("❓", size=30)


                async def manejar_click(e, i=i):
                  await click_carta(i)

                btn = ft.ElevatedButton(
                    content=contenido,
                    width=90,
                    height=90,
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
          width=12 * 70,  # 6 columnas de 60px + 10px de espacio aprox
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

        controles_superiores =ft.Container(
            content=ft.Row(
              controls=[icono_sonido, salir_btn],
              alignment=ft.MainAxisAlignment.END,
              spacing=10
            ),
          alignment=ft.alignment.top_right,
          padding=10
        )

        vista_juego = ft.View(
    "/juego",
    controls=[
        ft.Column(
            controls=[
                # Fila con botones arriba, alineados a la derecha
                ft.Row(
                    controls=[icono_sonido, salir_btn],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                ),
                ft.Container(height=20),  # Espacio para separar botones del contenido
                # Contenido principal: título y tablero
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

    boton1 = ft.ElevatedButton("Jugar", width=200, height=60, bgcolor="#446DFF", color=ft.Colors.WHITE,
                               on_click=ir_a_juego,
                               style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline")))
    
    boton2 = ft.ElevatedButton("Por supuesto", width=200, height=60, bgcolor="#446DFF", color=ft.Colors.WHITE,
                               on_click=ir_a_juego,
                               style=ft.ButtonStyle(text_style=ft.TextStyle(size=20, font_family="Bungee Inline")))
    
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

ft.app(target=main)

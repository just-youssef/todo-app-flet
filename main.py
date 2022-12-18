import flet
from flet import Page
from app import TodoApp


def main(page: Page):
    page.title = "To-Do App"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "end"
    page.scroll = "adaptive"
    page.window_width = page.window_min_width = 700
    page.window_height = page.window_min_height = 500
    page.theme_mode = "dark"

    page.update()

    # create application instance
    todo = TodoApp(page)

    # add application's root control to the page
    page.add(todo)

flet.app(target=main)

from flet import (
    Column,
    FloatingActionButton,
    Row,
    Tab,
    Tabs,
    TextField,
    UserControl,
    icons,
    Text,
    OutlinedButton,
    Container,
    border,
    IconButton,
    AppBar,
    Icon,
)
from task import Task
import sqlite3

class TodoApp(UserControl):
    def __init__(self, page):
        super().__init__()
        self.page=page
        self.page.appbar = AppBar(
            leading=Icon(icons.NOTE_ALT_OUTLINED, size=30),
            title=Text("To-Do App"),
            leading_width=60,
            center_title=True,
            bgcolor="#252525",
            actions=[
                IconButton(
                    icon=icons.LIGHT_MODE_OUTLINED,
                    tooltip="Dark mode",
                    on_click=self.toggle_theme
                )
            ]
        )
        self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode=="dark":
            self.page.theme_mode="light"
            e.control.icon=icons.DARK_MODE_OUTLINED
            self.app_view.bgcolor="#e1e1e1"
            self.page.appbar.bgcolor="#e1e1e1"
        else:
            self.page.theme_mode="dark"
            e.control.icon=icons.LIGHT_MODE_OUTLINED
            self.app_view.bgcolor="#252525"
            self.page.appbar.bgcolor="#252525"
        self.update()
        self.page.update()

    def refresh(self, e):
        self.update()
        self.page.update()

    def build(self):
        self.new_task = TextField(label="Whats needs to be done?", expand=True)
        self.tasks = Column()

        with sqlite3.connect('todo_tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT * from task''')
            result = cursor.fetchall()
            conn.commit()

            for t in result:
                old_task = Task(t[1], self.task_status_change, self.task_delete, bool(t[2]))
                self.tasks.controls.append(old_task)
        
        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="All"), Tab(text="Active"), Tab(text="Completed")],
        )
        self.count = 0
        self.items_left = Text(f"{self.count} active item(s) left")

        # application's root control (i.e. "view") containing all other controls
        self.app_view = Container(
            border_radius=5,
            bgcolor="#252525",
            padding=20,
            content=Column(
                width=600,
                controls=[
                    Row(
                        alignment="spaceBetween",
                        vertical_alignment="center",
                        controls=[
                            Text(value="To-Do List", style="headlineLarge"),
                            IconButton(
                                icon=icons.REFRESH,
                                tooltip="Refresh",
                                on_click=self.refresh
                            )
                        ],
                    ),
                    Row(
                        controls=[
                            self.new_task,
                            FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                        ],
                    ),
                    Column(
                        controls=[
                            self.filter,
                            Container(
                                width=596,
                                border= border.all(1),
                                border_radius=5,
                                content=self.tasks
                            ),
                            Row(
                                alignment="spaceBetween",
                                vertical_alignment="center",
                                controls=[
                                    self.items_left,
                                    OutlinedButton(text="Clear completed", on_click=self.clear_clicked, icon=icons.DELETE_OUTLINED),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        )

        return self.app_view

    def add_clicked(self, e):
        try:
            self.new_task.error_text = None
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            task.push()
            self.tasks.controls.append(task)
            self.new_task.value = ""
        except Exception as err:
            self.new_task.error_text = err
        self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        with sqlite3.connect('todo_tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f'''DELETE FROM task WHERE name="{task.task_name}"''')
            conn.commit()
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls:
            if task.completed:
                self.task_delete(task)

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        self.count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "All"
                or (status == "Active" and not task.completed)
                or (status == "Completed" and task.completed)
            )
            if not task.completed:
                self.count += 1
        self.items_left.value = f"{self.count} active item(s) left"
        #print([task.task_name for task in self.tasks.controls])
        super().update()

import os

from nicegui import ui
from dotenv import load_dotenv

## Load environment variables
load_dotenv()

token = os.environ.get("TOKEN")

with ui.dialog() as dialog, ui.card():
    ui.label('Are you sure?')
    with ui.row():
        ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
        ui.button('No', on_click=lambda: dialog.submit('No'))

async def show():
    result = await dialog
    ui.notify(f'You chose {result}')

ui.button('Await a dialog', on_click=show)

ui.run(host="127.0.0.1", port="4443", title='Gitlab Tool')
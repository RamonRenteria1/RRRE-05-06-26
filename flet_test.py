import flet as ft

print('START TEST')

def main(page):
    print('INSIDE MAIN')
    page.title = 'TEST'
    page.add(ft.Text('OK'))

print('BEFORE RUN')
try:
    ft.run(main, view=ft.AppView.WEB_BROWSER, host='127.0.0.1', port=8552)
    print('AFTER RUN')
except Exception as e:
    print('RUN ERROR', e)

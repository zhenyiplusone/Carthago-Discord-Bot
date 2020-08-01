from openpyxl import load_workbook
import excel2img

book = load_workbook('spreadsheet/War.xlsx')
sheet = book.active #active means last opened sheet

book.save('spreadsheet/War.xlsx')

excel2img.export_img("spreadsheet/War.xlsx","spreadsheet/image.png","War Scenario Sheet")
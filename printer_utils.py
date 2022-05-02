import win32print
import win32ui
from PIL import Image, ImageWin
from config import app_config


def load_printer_config():
    return app_config['PRINTER_CONFIG'].as_pairs()


def get_printer_name():
    if app_config['PRINTER_NAME'].get() == None:
        return win32print.GetDefaultPrinter()
    else:
        return app_config['PRINTER_NAME'].get()

def get_device_context(printer_name):
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    return hDC

def print_image(img_file, device_context):
    #load image
    bmp = Image.open(img_file)
    if bmp.size[0] > bmp.size[1]:
        bmp = bmp.rotate(90)

    #set printer device-context config
    printer_conf = load_printer_config()
    printable_area = device_context.GetDeviceCaps(printer_conf['HOZRES']), device_context.GetDeviceCaps(printer_conf['VERTRES'])
    printer_size = device_context.GetDeviceCaps(printer_conf['PHYSICALWIDTH']), device_context.GetDeviceCaps(printer_conf['PHYSICALHEIGHT'])

    ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
    scale = min(ratios)

    try:
        device_context.StartDoc(img_file)
        device_context.StartPage()
        dib = ImageWin.Dib(bmp)
        scaled_width, scaled_height = [int(scale * i) for i in bmp.size]
        x1 = int((printer_size[0] - scaled_width) / 2)
        y1 = int((printer_size[1] - scaled_height) / 2)
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        dib.draw (device_context.GetHandleOutput(), (x1, y1, x2, y2))
        device_context.EndPage()
        device_context.EndDoc()
        device_context.DeleteDC()
    except Exception as e:
        raise e

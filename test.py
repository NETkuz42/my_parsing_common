from pywinauto import Desktop, Application
from pywinauto import findwindows, ElementNotFoundError
from time import sleep


def close_popup_another_vpn(surf_windows):
    try:
        close_click = surf_windows.child_window(title="Close pop up", auto_id="popup_close_button", control_type="Button")
        close_click.click_input()
        print(close_click)
    except ElementNotFoundError:
        return False
    return True


Application(backend="uia").start(r"C:\Program Files (x86)\Surfshark\Surfshark.exe")
sleep(2)
app = Application(backend="uia", allow_magic_lookup=False).connect(path="Surfshark.exe")
surf = app["Surfshark"]
albania = surf['ListBox3'].child_window(title="United States St. Louis", control_type="ListItem").
albania.select()
# surf["ListBox"].print_control_identifiers()
# test = app_window.print_control_identifiers()
# app_window.print_control_identifiers()

# albania = surf.child_window(title="Albania", auto_id="location_albania", control_type="Button").wrapper_object()
# albania.click_input()
#
# test = close_popup_another_vpn(surf)
# print(test)
#
#
# sleep(1)
# close_button = surf.child_window(title="Close application", control_type="Button").wrapper_object()
# close_button.click_input()



from pywinauto import Desktop, Application
from pywinauto import findwindows, ElementNotFoundError
from pywinauto.timings import always_wait_until_passes
from time import sleep


def close_popup_another_vpn(surf_windows):
    try:
        close_click = surf_windows.child_window(title="Close pop up", auto_id="popup_close_button", control_type="Button")
        close_click.click_input()
        print(close_click)
    except ElementNotFoundError:
        return False
    return True


# @always_wait_until_passes(4, 2)
# def ensure_text_changed(ctrl):
#     if previous_text == ctrl.window_text():
#         raise ValueError('The ctrl text remains the same while change is expected')


Application(backend="uia").start(r"C:\Program Files (x86)\Surfshark\Surfshark.exe")
sleep(2)
app = Application(backend="uia").connect(path="Surfshark.exe")
surf_window = app["Surfshark"].print_control_identifiers()
country_list = surf_window['ListBox3']

slovenia = country_list["Slovenia"].set_focus()
sleep(2)
belize = country_list["Belize"].set_focus()
# test = slovenia.wrapper_object()
# print(type(test))
# albania.select()
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



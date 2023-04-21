from pywinauto import Desktop, Application, timings
from pywinauto import findwindows, ElementNotFoundError
from pywinauto.timings import always_wait_until_passes
from time import sleep





# @always_wait_until_passes(4, 2)
# def ensure_text_changed(ctrl):
#     if previous_text == ctrl.window_text():
#         raise ValueError('The ctrl text remains the same while change is expected')


# Application(backend="uia").start(r"C:\Program Files (x86)\Surfshark\Surfshark.exe")
# sleep(2)


class SurfWindowControl:
    def __init__(self):
        app = Application(backend="uia").connect(path="Surfshark.exe")
        self.surf = app["Surfshark"]
        self.country_list = []
        self.result_country=[]

    def check_popup_another_vpn(self):
        try:
            close_click = self.surf.child_window(title="Close pop up", auto_id="popup_close_button",
                                                    control_type="Button")
            close_click.click_input()
            print(close_click)
        except ElementNotFoundError:
            return False
        return True

    def get_country_list(self):
        country_tree_list = self.surf.child_window(title="Armenia", auto_id="location_armenia", control_type="Button").parent().parent().texts()
        country_list = []
        for country_row in country_tree_list:
            country = country_row[0]
            country_list.append(country)
        self.country_list = country_list
        return country_list

    def connect_to_country(self, country):
        select_country = self.surf.child_window(title=country, control_type="Button")
        select_country.wrapper_object().click_input()
        try:
            self.surf.child_window(title="Disconnect", auto_id="connect_button", control_type="Button").wait("exists", 10, 1)
            print("Успешно подключился к стране")
        except timings.TimeoutError:
            print("коннект не удался")

        select_details = self.surf.child_window(title="Home info", auto_id="homeinfo_connectionlabel", control_type="Button")
        select_details.wrapper_object().click_input()

        ip_button = self.surf.child_window(auto_id="homeinfo_ipaddress_button", control_type="Button").wait("exists", 10, 1)
        ip_button.click_input()

        ip_details = self.surf.child_window(title="Real:", control_type="Text").wait("exists", 10, 1)
        current_ip = ip_details.parent().children()[10].texts()[0]
        print("Текущий IP:", current_ip)
        return current_ip

    def disconnect_country(self):
        self.surf.child_window(title="Back", auto_id="BackButton", control_type="Button").wrapper_object().click_input()
        disconnect_button = self.surf.child_window(title="Disconnect", auto_id="connect_button", control_type="Button").wait("exists", 10, 1)
        disconnect_button.click_input()
        print("Отключился от страны")

    def get_test(self):
        self.get_country_list()
        self.connect_to_country(self.country_list[0])


SurfWindowControl().disconnect_country()


# surf.child_window(title="Back", auto_id="BackButton", control_type="Button").wrapper_object().click_input()
# current_ip = surf.child_window(title="Real:", control_type="Text").parent().children()[10].texts()[0]
# test = surf.children()[10].texts()
# print(test)
# test = surf.select(5).draw_outline()
# print(test)
# finland = surf.child_window(title="Finland", auto_id="location_finland", control_type="Button").wrapper_object()
# finland.set_focus()dr
# finland.click_input()
# ip_button = surf.child_window(auto_id="homeinfo_ipaddress_button", control_type="Button").wrapper_object()
# ip_button.click_input()
# ip_loc = surf.child_window(auto_id="UserControl", control_type="Custom").draw_outline()
# text = ip_loc.child_window(auto_id="homeinfo_ipaddress_text", control_type="Custom").texts()
# print(text)
# sleep(5)
# test = surf.child_window(title="Home info", auto_id="homeinfo_connectionlabel", control_type="Button").wrapper_object().click_input()
# print(test)
# surf_window = app["Surfshark"].print_control_identifiers()
# country_list = surf_window['ListBox3']
#
# slovenia = country_list["Slovenia"].set_focus()
# sleep(2)
# belize = country_list["Belize"].set_focus()
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



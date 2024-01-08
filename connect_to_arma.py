from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as KBControl
from pynput.keyboard import Key
from pynput import mouse
from time import  sleep
import pyautogui
import pydirectinput

class MouseListener:
    def __init__(self):
        pass

    def on_move(self, x, y):
        print('Pointer moved to {0}'.format(
            (x, y)))

    def on_click(self, x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        if not pressed:
            # Stop listener
            return False

    def on_scroll(self, x, y, dx, dy):
        print('Scrolled {0} at {1}'.format(
            'down' if dy < 0 else 'up',
            (x, y)))

    def listen(self):
        # Collect events until released
        with mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll) as listener:
            listener.join()

        # ...or, in a non-blocking fashion:
        listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        listener.start()

class ClickOnServer:
    def __init__(self):
        pass

    def click_server(self):
        mouse = Controller()
        keyboard = KBControl()
        mouse.position = (334, 381)
        sleep(1)
        mouse.click(Button.left)
        sleep(1)
        keyboard.press(Key.enter)


        # mouse.press(Button.left)
        # sleep(1)
        # mouse.release(Button.left)

class CliclOnServer_new():
    def __init__(self):
        pass

    def click(self):

        pydirectinput.moveTo(334, 381)  # Move the mouse to the x, y coordinates 100, 150.
        pydirectinput.click()  # Click the mouse at its current location.
        sleep(2)
        pydirectinput.press('enter')
        # pydirectinput.click()
        # pydirectinput.click(200, 220)  # Click the mouse at the x, y coordinates 200, 220.
        # pydirectinput.move(None,
        #                         10)  # Move mouse 10 pixels down, that is, move the mouse relative to its current position.
        # pydirectinput.doubleClick()  # Double click the mouse at the
        # pydirectinput.press('esc')  # Simulate pressing the Escape key.
        # pydirectinput.keyDown('shift')
        # pydirectinput.keyUp('shift')



# MouseListener().listen()
ClickOnServer().click_server()

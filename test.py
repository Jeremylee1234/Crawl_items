import pyautogui
import time

gradients = [
    pyautogui.linear,
    pyautogui.easeInQuad,
    pyautogui.easeOutQuad,
    pyautogui.easeInOutQuad,
    pyautogui.easeInCubic,
    pyautogui.easeOutCubic,
    pyautogui.easeInOutCubic,
    pyautogui.easeInQuart,
    pyautogui.easeOutQuart,
    pyautogui.easeInOutQuart,
    pyautogui.easeInQuint,
    pyautogui.easeOutQuint,
    pyautogui.easeInOutQuint,
    pyautogui.easeInSine,
    pyautogui.easeOutSine,
    pyautogui.easeInOutSine,
    pyautogui.easeInExpo,
    pyautogui.easeOutExpo,
    pyautogui.easeInOutExpo,
    pyautogui.easeInCirc,
    pyautogui.easeOutCirc,
    pyautogui.easeInOutCirc
]
for gradient in gradients:
    print(gradient)
    time.sleep(0.5)
    pyautogui.moveTo(400,540,0.5)
    time.sleep(0.3)
    pyautogui.moveRel(500,0,1,pyautogui.linear)
    time.sleep(0.3)

from stepper import *
import keyboard
#setup motors
#initialize objects
m1 = stepper(90,"cw",2,3,4,17,False)
m2 = stepper(120,"cw",14,15,18,23,True)
m3 = stepper(90,"cw",22,10,9,11,False)

#sero everything
m1.zero()
m2.zero()
m3.zero()

#tighten functions
def tighten_stiff():
    m1.set_loc(m1.set_loc(m1.location+1))
    m3.set_loc(m3.set_loc(m3.location+1))
#loosen funcitons
def loosen_stiff():
    m1.set_loc(m1.set_loc(m1.location-1))
    m3.set_loc(m3.set_loc(m3.location-1))

#add hotkeys
keyboard.add_hotkey('right_arrow', lambda: m2.set_loc(m2.set_loc(m2.location+1)))
keyboard.add_hotkey('left_arrow', lambda: m2.set_loc(m2.set_loc(m2.location-1)))
keyboard.add_hotkey('up_arrow', lambda: tighten_stiff())
keyboard.add_hotkey('down_arrow', lambda: loosen_stiff())

#begin waiting
keyboard.wait()

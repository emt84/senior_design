from stepper import *

#initialize objects
m1 = stepper(120,"cw",2,3,4,11)
m2 = stepper(120,"cw",14,15,18,23)
m3 = stepper(120,"cw",22,10,9,11)

#zero each motor
m1.zero()
m2.zero()
m3.zero()

#set each motor to a different location
m1.set_loc(20)
m2.set_loc(50)
m3.set_loc(60)

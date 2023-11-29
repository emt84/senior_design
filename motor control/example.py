from stepper import *

#initialize objects
m1 = stepper(120,"cw",2,3,4,11,False)
m2 = stepper(120,"cw",14,15,18,23,True)
m3 = stepper(120,"cw",22,10,9,11,False)

#zero each motor
# m1.zero()
# m2.zero()
# m3.zero()

#set each motor to a different location
# m1.set_loc(20)
# m2.set_loc(50)
# m3.set_loc(60)

#use claw to control motor 2
c = claw(m2,100,100,4,6,3,20)
#set claw so tips of sheets are touching
c.set_width(0)


#2 stiffness objects
s1 = stiffness(m1)
s2 = stiffness(m2)

#create whole object
w = whole(c,s1,s2)

#pick up 30 gram, 30mm wide object with .5 strength
w.grab_obj(30,40,.5)

#open to max size
#w.open_up()

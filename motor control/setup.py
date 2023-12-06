from stepper import *

#initialize objects
m1 = stepper(120,"cw",2,3,4,17,False)
m2 = stepper(120,"cw",14,15,18,23,True)
m3 = stepper(120,"cw",22,10,9,11,False)

#zero each motor
m1.zero()
m2.zero()
m3.zero()

#use claw to control motor 2
c = claw(m2,100,100,4,6,3,20)
#set claw so tips of sheets are touching
c.set_width(0)

#2 stiffness objects
s1 = stiffness(m1)
s2 = stiffness(m2)

#create whole object
w = whole(c,s1,s2)

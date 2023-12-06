from math import *
#used to test values outside of pi
def grab_obj(width, weight, strength):
    #calc force required to pick up object, .1 assumed for coeffecient of friction
    # (sheets typically bend to vertical position so little normal force)
    force = weight/1000 * 9.81 / .62 / 2
    curvature = 90*sqrt(strength)
    #linear relationship between strength and stifnesss
    stiffness =0.01493523*exp(-0.00218377*weight)*exp(0.0279950285*exp(-0.0038579591*weight)*curvature)
    #calculate displacement based on calculated force and stiffness
    disp = force/stiffness
    #estimate width based on width and strength
    width = width-disp*2

    print("calculated stiffness", str(stiffness))
    print("calculated disp", str(disp))
    print("calculated width", str(width))
grab_obj(50,200,1)
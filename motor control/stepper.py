import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time
from scipy.optimize import root_scalar
import numpy as np

class stepper:

  def __init__(self, rot_limit, orientation, limit_pin, enable_pin, step_pin, direction_pin,switch_mode):

    self.rot_limit = rot_limit #INT - how many steps the motor can rotate
    self.delay = .01 #FLOAT - time in between steps
    self.orientation = orientation #STR- direction to close/tighten, "cw"=clockwise, "ccw"=counterclockwise
    self.direction_pin = direction_pin #INT - GPIO pin number
    self.step_pin = step_pin #INT - GPIO pin number
    self.enable_pin = enable_pin #INT - GPIO pin number
    self.limit_pin = limit_pin #INT - GPIO pin number
    self.location = 0 #INT - number of steps from 0
    self.switch_mode = switch_mode #BOOL - True if limit switch is normally open, False otherwise

    self.m = RpiMotorLib.A4988Nema(self.direction_pin, self.step_pin, (21,21,21), "DRV8825") #initialize motor object from lib
    GPIO.setup(self.enable_pin,GPIO.OUT) # set enable pin as output
    GPIO.setup(self.limit_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) #initialize enable pin

    GPIO.output(self.enable_pin,GPIO.LOW) # pull enable to low to enable motor

  #returns the state of the limit switch
  def get_limit(self):
    return GPIO.input(self.limit_pin)
    
  #moves the number of *steps(int)*, postive=tighten
  #HAS NO BOUNDS CHECKING
  #HAS NO LOCATION TRACKING
  def mov(self,steps):
    #update direction
    direction = steps > 0
    if self.orientation == "cw":
      self.m.motor_go(not direction, # True=Clockwise, False=Counter-Clockwise
        "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
        abs(steps), # number of steps
        self.delay, # step delay [sec]
        False, # True = print verbose output
        0) # initial delay [sec]
    elif self.orientation == "ccw":
      self.m.motor_go(direction, # True=Clockwise, False=Counter-Clockwise
        "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
        abs(steps), # number of steps
        self.delay, # step delay [sec]
        False, # True = print verbose output
        0) # initial delay [sec]
        
  #zeroes the location of the motor
  def zero(self):
    #if limit switch normally open
    if self.switch_mode:
      #tighten until not touching switch
      while(not self.get_limit()):
        self.mov(1)
      #open until touching switch
      while(self.get_limit()):
       self.mov(-1)
    #if limit switch normally close
    else:
      #tighten until touching switch
      while(self.get_limit()):
        self.mov(1)
      #open until not touching switch
      while(not self.get_limit()):
       self.mov(-1)
    self.location = 0
  
  #moves to the location *loc(int)*, loc is specified in steps from zero
  def set_loc(self, loc):
    #check bounds
    if loc >= 0 and loc <= self.rot_limit:
      #determine amount to move
      delta = loc - self.location
      #check that it needs to move
      if delta != 0:
        self.mov(delta)
        self.location = loc
      else:
        print("already there")
    else:
      print("location out of bounds!")

class claw:
  def __init__(self, stepper, distance, length, x_off, y_off, gear_ratio,r_off):
    self.stepper = stepper #STEPPER - the stepper object corresponding to the claw
    self.length = length #INT - length in mm of the plastic sheets
    self.x_off = x_off #INT - perpendicular offest in mm of the plastic sheet to the axis of rotation
    self.y_off = y_off #INT - parallel offset in mm of the plastic sheet to the axis of rotation
    self.distance = distance #INT - distance in mm between axis of rotation
    self.gear_ratio = gear_ratio #FLOAT - gear ration between stepper motor and axis of rotation
    self.r_off = r_off #FLOAT - angle in degrees measured from parallel that the sheets can open

  #calculate the angle of the sheets for *width(int)*, width should be in mm
  def calc_angle(self,width):
    #governing equation for distance based on angle theta
    def eqn(theta):
      return self.distance + 2*(self.x_off*np.cos(theta)-(self.length+self.y_off)*np.cos(np.pi/2-theta)) - width
    #calculate theta
    sol = root_scalar(eqn, x0=.5, method='secant')
    theta = round(sol.root,5)
    #convert to degrees
    theta = np.rad2deg(theta)
    return(theta)

  #sets claw to given *width(int)*, width should be in mm
  def set_width(width):
    #find required angle including the offset
    angle = self.calc_angle(width) + self.r_off
    #calculate the angle in steps from zero
    steps = round(self.gear_ratio*angle/1.8)
    #move the motor to the calculated steps
    stepper.set_loc(steps)

class stiffness:
  def __init__(self, stepper):
    self.stepper = stepper  #STEPPER - the stepper object corresponding to the stiffness control

  #calculate the location for *stiff(float)*, stiffness should be in N/mm
  def calc_loc(stiff):
    #fitted equation from empirical data
    def eqn(loc):
      return .0001769*loc**2+.0022213*loc+.1423-stiff
    #calculate location
    sol = root_scalar(eqn, x0=20, method='secant')
    loc = round(sol.root,5)
    return loc

  #sets stiffness actuator to given *stiff(float)*, stiffness should be in N/mm
  def set_stiffness(stiff):
    loc = calc_loc(stiff)
    self.stepper.set_loc(loc)

class whole:
  def __init__(self,claw,stiff1,stiff2):
    self.claw = claw #CLAW - claw object
    self.stiff1 = stiff1 #STIFFNESS - stiffness object 
    self.stiff2 = stiff2 #STIFFNESS - stiffness object

  #set width and stiffness for object with given *width(float)*, *weight(float)*, and *strength(float)*
  #width should be in mm
  #weight should be in grams
  #strength varies from 0-1 with 0 being very fragile and 1 being relatively sturdy
  def grab_obj(width, weight, strength):
    #calc force required to pick up object, .1 assumed for coeffecient of friction
    # (sheets typically bend to vertical position so little normal force)
    force = weight/1000 * 9.81 / .1 / 2

    #linear relationship between strength and stifness
    stiffness = .15+strength*.6
    #calculate displacement based on calculated force and stiffness
    disp = force/stiffness
    #estimate width based on width and strength
    width = width-disp*2-strength*width*.25

    #set all parts to respective setttingsß
    self.claw.set_width(width)
    self.stiff1.set_stiffness(stiffness)
    self.stiff2.set_stiffness(stiffness)
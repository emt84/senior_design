import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

class stepper:

  def __init__(self, rot_limit, orientation, limit_pin, enable_pin, step_pin, direction_pin):

    self.rot_limit = rot_limit #INT - how many steps the motor can rotate
    self.delay = .01 #FLOAT - time in between steps
    self.orientation = orientation #STR- direction to close/tighten, "cw"=clockwise, "ccw"=counterclockwise
    self.direction_pin = direction_pin #INT - GPIO pin number
    self.step_pin = step_pin #INT - GPIO pin number
    self.enable_pin = enable_pin #INT - GPIO pin number
    self.limit_pin = limit_pin #INT - GPIO pin number
    self.location = 0 #INT - number of steps from 0

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
    #tighten until not touching switch
    while(not self.get_limit()):
      self.mov(1)
    #open until touching switch
    while(self.get_limit()):
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


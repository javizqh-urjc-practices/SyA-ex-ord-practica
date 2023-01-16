
import RPi.GPIO as GPIO

class Sensor():
  def __init__(self, pin:int):
    '''Initialize the actuator setting the GPIO mode to board'''
    self.setMode()
    self.__pin = pin
    self.setPin()
  
  def setMode(self):
    # Set the GPIO mode to board
    self.GPIO = GPIO
    self.GPIO.setmode(self.GPIO.BOARD) # Select pin number mode 
  
  def setPin(self):
     self.GPIO.setup(self.__pin, self.GPIO.IN, pull_up_down = self.GPIO.PUD_UP)

  def connect(self,trigger, function, bouncetime = 1):
    if trigger == "rising":
      self.GPIO.add_event_detect(self.__pin, self.GPIO.RISING,callback=function, bouncetime=bouncetime)
    elif trigger == "falling":
      self.GPIO.add_event_detect(self.__pin, self.GPIO.FALLING,callback=function, bouncetime=bouncetime)
    elif trigger == "both":
      self.GPIO.add_event_detect(self.__pin, self.GPIO.BOTH,callback=function, bouncetime=bouncetime)
    else:
      raise("Unknown trigger")

  def clean(self):
    """Clean the GPIO channels"""
    self.GPIO.cleanup(self.__pin)

class Switch (Sensor):
  def __init__(self, pin:int):  
    super(Switch,self).__init__(pin)

class Button (Sensor):
  def __init__(self, pin:int):  
    super(Button,self).__init__(pin)

import RPi.GPIO as GPIO
import pigpio,time

class Actuator():
  def __init__(self, pin:int, inputRange = (100,0), outputRange = (100,0)):
    '''Initialize the actuator setting the GPIO mode to board'''
    self.setMode()
    self.__pin = pin
    self.__state = False # Off/False, On/True
    self.__inputRange = inputRange
    self.__outputRange = outputRange
    self.setPin()
  
  def setMode(self):
    # Set the GPIO mode to board
    self.GPIO = GPIO
    self.GPIO.setmode(GPIO.BOARD) # Select pin number mode 
  
  def setPin(self):
    GPIO.setup(self.__pin, GPIO.OUT) # Change pin mode to output
    self.__pwm = self.GPIO.PWM(self.__pin,100)
    self.__pwm.start(self.__outputRange[1]) 
  
  def setIntensity(self, intensity):
    self.checkInputRange(intensity)
    self.normalize()
    self.__pwm.ChangeDutyCycle(self.__signalIntensityNormal) 
  
  def getIntensity(self):
    return self.__signalIntensity

  def checkInputRange(self,value:int):
    if value > self.__inputRange[0]: value = self.__inputRange[0]
    if value < self.__inputRange[1]: value = self.__inputRange[1]
    self.__signalIntensity = value

  def switch(self):
    if self.__state :
      self.off()
    else:
      self.on()

  def on(self):
    self.__state = True
    self.setIntensity(self.__inputRange[0])
  
  def off(self):
    self.__state = False
    self.setIntensity(self.__inputRange[1])

  def normalize(self):
    '''Normalize the value input to the desire range'''
    
    if self.__signalIntensity == self.__inputRange[1]:
      norm = self.__outputRange[1]
    else:
      norm = (self.__signalIntensity - self.__inputRange[1])/(self.__inputRange[0] - self.__inputRange[1])
      norm = norm * (self.__outputRange[0] - self.__outputRange[1]) + self.__outputRange[1]

    self.__signalIntensityNormal = norm 
  
  def clean(self):
    """Clean the GPIO channels"""
    self.off()
    self.GPIO.cleanup(self.__pin)

class Led(Actuator):
  def __init__(self, pin:int, inputRange = (100, 0), outputRange = (100,0)):  
    super(Led,self).__init__(pin, inputRange, outputRange)

class LedRGB():

  def __init__(self, redPin:int, greenPin:int, bluePin:int, inverted:bool = False):

    # If the led is inverted then output range is inverted
    rgbRange = (255,0) # Input range
    if inverted:
      outputRange = (0,100)
    else:
      outputRange = (100,0)

    # Set the pin number and RGB values as privates atributes
    self.__r = Led(redPin,rgbRange,outputRange)

    self.__g = Led(greenPin,rgbRange,outputRange)

    self.__b = Led(bluePin,rgbRange,outputRange)

  def setRGB(self,r:int, g:int, b:int):
    """Sets the RGB values"""
    self.__r.setIntensity(r)
    self.__g.setIntensity(g)
    self.__b.setIntensity(b)

  def on(self):
    """Turn on the RGB value"""
    # Set the led values to (255,255,255) then the led is on
    self.setRGB(255,255,255)

  def off(self):
    """Turn off the RGB value"""
    # Set the led values to (0,0,0) then the led is off
    self.setRGB(0,0,0)
  
  def getRGB(self):
    """Return the current RGB values"""
    return (self.__r.getIntensity(), self.__g.getIntensity(), self.__b.getIntensity())
  
  def clean(self):
    self.__r.clean()
    self.__g.clean()
    self.__b.clean()

class ServoMotor():
  '''
    Según especificaciones de la compañía fabricante de estos servos, Parallax,
    la modulación PWM de estos servos tiene los siguientes rangos:
    - Girar en un sentido: [1280...1480]
    - Parar: 1500
    - Girar en el otro: [1520...1720]

    Mientras más cerca al valor 1500, más despacio; cuanto más alejado, más rápido.
  '''
  def __init__(self,pin:int, inputRange = (100,0)):
    '''Initialize the actuator setting the GPIO mode to board'''
    self.setMode()
    self.__pin = pin
    self.__state = False # Off/False, On/True
    self.__direction = False # Left/False, Right/True
    self.__inputRange = inputRange

    self.__motor = pigpio.pi() # instancia de la clase pi de la libreria pigpio
                      # Usaremos el demonio pigpiod para comandar al motor por teclado
                      # Por ello, IMPORTANTE, hay que lanzar el demonio: sudo pigpiod
    self.calibrate()
  
  def setMode(self):
    # Set the GPIO mode to board
    self.GPIO = GPIO
    self.GPIO.setmode(GPIO.BOARD) # Select pin number mode 
  
  def calibrate(self):
    '''Calibrate the motor'''
    # First left
    print("Calibrating left rotation\n - Press + until the motor starts to rotate\n - Press enter to finish") 
    order = ""
    leftThreshold = 1500
    while order != "\n":
      order = input(">")
      if order == "+":
        leftThreshold -= 1 
        self.__motor.set_servo_pulsewidth(self.__pin, leftThreshold )
    
    self.__leftRange = (1280,leftThreshold)
    
    # Then right
    print("\nCalibrating right rotation\n - Press + until the motor starts to rotate\n - Press enter to finish")
    order = ""
    rightThreshold = 1500
    while order != "\n":
      order = input(">")
      if order == "+":
        rightThreshold += 1 
        self.__motor.set_servo_pulsewidth(self.__pin, rightThreshold )
    
    self.__rightRange = (rightThreshold,1720)

  def setIntensity(self, intensity):
    self.checkInputRange(intensity)
    self.normalize()
    self.__motor.set_servo_pulsewidth(self.__pin, self.__signalIntensityNormal)
  
  def getIntensity(self):
    return self.__signalIntensity

  def checkInputRange(self,value:int):
    if value > self.__inputRange[0]: value = self.__inputRange[0]
    if value < self.__inputRange[1]: value = self.__inputRange[1]
    self.__signalIntensity = value

  def switch(self):
    if self.__state :
      # Change sides
      if self.__direction :
        self.left(self.__signalIntensity)
      else:
        self.right(self.__signalIntensity)

  def right(self, intensity):
    self.__outputRange = self.__rightRange
    self.setIntensity(intensity)

  def left(self, intensity):
    self.__outputRange = self.__leftRange
    self.setIntensity(intensity)
  
  def stop(self):
    self.__state = False
    self.__motor.set_servo_pulsewidth(self.__pin, 1500) # 1.º lo ponemos a 0 rpm

  def off(self):
    self.stop()
    time.sleep(1)
    self.__motor.set_servo_pulsewidth(self.__pin, 0) # y 2.º lo "apagamos"
    self.__motor.stop()

  def normalize(self):
    '''Normalize the value input to the desire range'''
    
    if self.__signalIntensity == self.__inputRange[1]:
      norm = self.__outputRange[1]
    else:
      norm = (self.__signalIntensity - self.__inputRange[1])/(self.__inputRange[0] - self.__inputRange[1])
      norm = norm * (self.__outputRange[0] - self.__outputRange[1]) + self.__outputRange[1]

    self.__signalIntensityNormal = norm 
  
  def clean(self):
    """Clean the GPIO channels"""
    self.off()
    self.GPIO.cleanup(self.__pin)
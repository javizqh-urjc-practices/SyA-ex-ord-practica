# Practica 10. Sensores y actuadores. URJC. Julio Vega
# Codigo de ejemplo de manejo del Servo Feedback 360 de Parallax

#!/usr/bin/env python3

import sys, tty, signal, time, pigpio
import RPi.GPIO as GPIO
import sensor, actuator

servoPin = 8 # numeracion en modo BCM (que es el usado por defecto por pigpio)

'''
  Según especificaciones de la compañía fabricante de estos servos, Parallax,
  la modulación PWM de estos servos tiene los siguientes rangos:
  - Girar en un sentido: [1280...1480]
  - Parar: 1500
  - Girar en el otro: [1520...1720]

  Mientras más cerca al valor 1500, más despacio; cuanto más alejado, más rápido.
'''

def callbackSalir(senial, cuadro):
    '''Clear the GPIO pin and exits the program'''
    GPIO.cleanup()
    sys.exit(0)

def callbackBotonPulsado (canal):
    '''Change the direction of the motor'''
    global estado
    if estado:
        acelerar(2)
    else:
        parar()


def acelerar (intensidad): # girar en el otro sentido a velocidad máxima

    ledRGB.setRGB(0,0,0)
    for i in range(1,50,1):
        time.sleep(1)
        vel = normalize(i*intensidad,[100,0],[1720,1500 + 25])
        miServo.set_servo_pulsewidth(servoPin, vel) # 36 hasta que empiece
        if(i < 15):
            ledRGB.setRGB(255, 0, 0) # Turn led red
        elif(i < 30):
            ledRGB.setRGB(255, 255, 0) # Turn led yellow
        else:
            ledRGB.setRGB(0, 255, 0) # Turn led green


def parar ():
    '''Stops the motor'''
    miServo.set_servo_pulsewidth(servoPin, 1500) # 1.º lo ponemos a 0 rpm
    time.sleep(1)
    miServo.set_servo_pulsewidth(servoPin, 0) # y 2.º lo "apagamos"
    miServo.stop()

def normalize(value:int ,inputRange,outputRange) -> int:
    # Change the value
    if value > inputRange[0]: value = inputRange[0]
    if value < inputRange[1]: value = inputRange[1]
    
    if value == inputRange[1]:
      norm = outputRange[1]
    else:
      norm = (value - inputRange[1])/(inputRange[0] - inputRange[1])
      norm = norm * (outputRange[0] - outputRange[1]) + outputRange[1]

    return norm

#==========================================================================
estado = True
miServo = pigpio.pi() # instancia de la clase pi de la libreria pigpio
                      # Usaremos el demonio pigpiod para comandar al motor por teclado
                      # Por ello, IMPORTANTE, hay que lanzar el demonio: sudo pigpiod
boton = sensor.Button(40)

ledRGB = actuator.LedRGB(37,35,33,True)
def main():
    
    signal.signal(signal.SIGINT, callbackSalir)
    acelerar(1)
    boton.connect(callbackBotonPulsado)


if __name__ == "__main__":
    main() 

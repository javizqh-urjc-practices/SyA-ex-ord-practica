# Practica 10. Sensores y actuadores. URJC. Julio Vega
# Codigo de ejemplo de manejo del Servo Feedback 360 de Parallax

#!/usr/bin/env python3

import sys, tty, signal, time, pigpio
import RPi.GPIO as GPIO

servoPin = 14 # numeracion en modo BCM (que es el usado por defecto por pigpio)
botonPin = 12
estado = True

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
    estado = not estado
        
def adelante (velocidad): # girar en un sentido a velocidad máxima 120 rpm
    '''Goes to the front with the specified speed (0-100)'''
    vel = normalize(int(velocidad),[100,0],[1720,1500 + 25])
    miServo.set_servo_pulsewidth(servoPin, vel) # 25 hasta que empiece

def atras (velocidad): # girar en el otro sentido a velocidad máxima
    '''Goes to the back with the specified speed (0-100)'''
    vel = normalize(int(velocidad),[100,0],[1280,1500 - 36])
    miServo.set_servo_pulsewidth(servoPin, vel) # 36 hasta que empiece

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
miServo = pigpio.pi() # instancia de la clase pi de la libreria pigpio
                      # Usaremos el demonio pigpiod para comandar al motor por teclado
                      # Por ello, IMPORTANTE, hay que lanzar el demonio: sudo pigpiod
def main(mode):
    GPIO.setmode(GPIO.BCM)
    
    signal.signal(signal.SIGINT, callbackSalir)
    
    if (mode == "Sensor"):
        PIN_TRIGGER = 4
        PIN_ECHO = 17

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        
        GPIO.setup(botonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(botonPin, GPIO.RISING, callback=callbackBotonPulsado, bouncetime=500) # expresado en ms.

        print( "Esperando a que se estabilice el US")
        time.sleep(2)
        while True:
            GPIO.output(PIN_TRIGGER, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(PIN_TRIGGER, GPIO.LOW)


            while GPIO.input(PIN_ECHO)==0:
                inicioPulso = time.time()
            while GPIO.input(PIN_ECHO)==1:
                finPulso = time.time()

            duracionPulso = finPulso - inicioPulso
            distancia = round(duracionPulso * 17150, 2) # In centimeters
            if (estado):adelante (100-distancia*2)
            else: atras (100-distancia*2)
            time.sleep(0.1)
    else:
        print ("Dispositivo listo. Esperando órdenes (w = adelante, s = atrás, x = parar)...")       
        while True:
            order = input('> ')

            orderList = order.split(' ') # Create a list of the command input
          
            if len(orderList) == 1:
                if orderList[0] == "x":
                    print("Parando motor (x) ...")
                    parar ()
                    print("Motor parado")
                    break

            if len(orderList) == 2:
                if orderList[0] == "w":
                    print("Adelante (w)")
                    adelante (orderList[1])

                elif orderList[0] == "s":
                    print("Atrás (s)")
                    atras (orderList[1])


if __name__ == "__main__":
    # main("User") Uncomment to have CLI interaction and comment the command below
    main("Senor") 

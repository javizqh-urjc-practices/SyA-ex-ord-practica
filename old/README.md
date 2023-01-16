# P9-Servo

## Observations
### Ej 1-2
The first excercise, was done using the provided code entirely, and only testing where the base values were.
We ended up with the following results:
```python
miServo.set_servo_pulsewidth(servoPin, vel) # 1525 hasta que empiece
miServo.set_servo_pulsewidth(servoPin, vel) # 1464 hasta que empiece
```
For the second excercise, we implemented a normalize function that will convert our input values, to the real ones that the motor takes.
```python
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
```
### Ej extra
In this part, we decided to mix some of the previous sensors, in order to make something more complex. We added the ultrasound sensor, to detect the distance between it an the object, so that the motor would run faster when the object was near. We also added a button to change the direction the motor would go.
from machine import PWM, UART, Pin
import utime

uart_in = UART(0, 9600, tx=Pin(0), rx=Pin(1))
uart_out = UART(1, 9600, tx=Pin(4), rx=Pin(5))

print("Pico UART ready")

led = Pin('LED', Pin.OUT)

class Servo:
    def __init__(self, MIN_DUTY=500000, MAX_DUTY=2500000, pin=15, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY
        
    def rotateDeg(self, pwm:int):
        if pwm < 0:
            pwm = 0
        elif pwm > 255:
            pwm = 255
            
        duty_ns = int(self.MAX_DUTY - pwm * (self.MAX_DUTY-self.MIN_DUTY)/255)
        self.pwm.duty_ns(duty_ns)

servo = Servo()
current = 128


while True:
    if uart_in.any():
        data = uart_in.read(1)
        
        if data:
            value = data[0]
            led.toggle()  # blinks when data received

            # Forward remaining bytes to next module
            remaining = uart_in.read()
            if remaining:
                print("Forwarding:", remaining)
                uart_out.write(remaining)

            # Smooth move to target
            if current < value:
                current = min(current + 2, value)
            elif current > value:
                current = max(current - 2, value)

            servo.rotateDeg(current)

    utime.sleep_ms(10)

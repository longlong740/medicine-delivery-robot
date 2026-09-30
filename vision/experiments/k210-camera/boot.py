import sensor, lcd, utime
from Maix import GPIO
from fpioa_manager import fm
fm.register(16, fm.fpioa.GPIOHS0, force=True)
KEY = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)
lcd.init()
key_pressed = 0
photo_mode = False
photo_counter = 1
def key_interrupt(KEY):
    global key_pressed
    utime.sleep_ms(10)
    if KEY.value() == 0:
        key_pressed = 1
KEY.irq(key_interrupt, GPIO.IRQ_FALLING)
while True:
    if not photo_mode:
        lcd.display(sensor.snapshot())
        if key_pressed:
            key_pressed = 0
            photo_mode = True
            photo_counter  =1
            print("进入拍照模式，开始自动拍摄...")
    else:
        if photo_counter <= 40:
            img = sensor.snapshot()
            filename = "/sd/{}.jpg".format(photo_counter)
            img.save(filename)
            print("已拍摄:", filename)
            lcd.display(img)
            utime.sleep_ms(500)
            lcd.display(sensor.snapshot())
            utime.sleep_ms(500)
            photo_counter += 1
        else:
            photo_mode = False
            print("已完成50张拍摄返回，预览模式")

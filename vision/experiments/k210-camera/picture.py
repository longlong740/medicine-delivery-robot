import sensor, lcd, utime
from Maix import GPIO
from fpioa_manager import fm

# 初始化硬件外设
fm.register(16, fm.fpioa.GPIOHS0, force=True)
KEY = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)

# 初始化LCD
lcd.init()

# 全局变量
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
        # 实时预览模式
        lcd.display(sensor.snapshot())

        if key_pressed:
            key_pressed = 0
            photo_mode = True
            photo_counter  =1
            print("进入拍照模式，开始自动拍摄...")
    else:
        # 拍照模式
        if photo_counter <= 100:
            # 拍摄并保存
            img = sensor.snapshot()
            filename = "/sd/{}.jpg".format(photo_counter)
            img.save(filename)
            print("已拍摄:", filename)

            # 显示照片1秒
            lcd.display(img)
            utime.sleep_ms(1000)  # 1秒预览

            # 等待3秒（总共4秒间隔）
            lcd.display(sensor.snapshot())  # 显示实时画面
            utime.sleep_ms(3000)  # 等待3秒

            photo_counter += 1
        else:
            photo_mode = False
            print("已完成100张拍摄返回，预览模式")

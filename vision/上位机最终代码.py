# -*- coding: utf-8 -*-
import sensor, image, lcd, time
import KPU as kpu
from machine import UART
import gc, sys
from fpioa_manager import fm

# ================== 全局配置 ==================
input_size = (224, 224)
labels = ['5', '8', '1', '2', '3', '4', '6', '7']
anchors = [1.56, 1.41, 2.91, 2.0, 2.0, 1.84, 1.62, 1.78, 1.91, 1.59]
# ================== 状态机 ==================
states = {
    "INIT": 0,       # 初始识别
    "MOVING": 1,     # 移动中（处理1、2）
    "WAIT_FOR_1": 2, # 等待下位机发1
    "CHECKING": 3,   # 验证中
    "DONE": 4        # 验证完成
}
current_state = states["INIT"]
stored_number = None
verify_counter = 0  # 验证次数计数器
special_verify = False  # 特殊验证标志
enhanced_verify_time = 0  # 用于增强型验证的计时器
enhanced_detect_count = 0  # 多目标验证计数器

def init_uart():
    """初始化串口"""
    fm.register(7, fm.fpioa.UART1_TX, force=True)
    fm.register(6, fm.fpioa.UART1_RX, force=True)
    return UART(UART.UART1, 115200, timeout=1000, read_buf_len=4096)

def send(uart, msg):
    """可靠发送消息"""
    uart.write(msg.encode('utf-8'))

def process_cmd(cmd):
    """指令处理"""
    global current_state, stored_number, verify_counter, special_verify

    if cmd == "S":
        current_state = states["INIT"]
        enhanced_verify_time = 0
        enhanced_detect_count = 0
        stored_number = None
        verify_counter = 0

    elif cmd == "1":
        verify_counter +=1  # 每次收到'1'都计数
        # 判断是否第三次验证
        special_verify = (verify_counter % 3 == 0)  # 每三次触发特殊验证

        if current_state in [states["WAIT_FOR_1"], states["DONE"]]:
            current_state = states["CHECKING"]

# 在main函数中添加状态显示函数
def draw_status(img, state):
    """在画面底部绘制状态信息"""
    state_names = {v:k for k,v in states.items()}  # 反转状态字典
    status_text = state_names.get(state, "UNKNOWN")
    img.draw_string(10, input_size[1]-30,  # 在底部留出30像素高度
                   status_text,
                   color=(255,255,0),     # 黄色文字
                   scale=2)


def enhanced_verify(img):
    """多目标验证（第三次使用）"""
    global enhanced_verify_time, enhanced_detect_count
    max_verify_duration = 3000  # 4000毫秒验证窗口
    required_count = 1

    # 初始化计时器
    if enhanced_verify_time == 0:
        enhanced_verify_time = time.ticks_ms()
        enhanced_detect_count = 0

    # 检查是否超时

    if time.ticks_diff(time.ticks_ms(), enhanced_verify_time) > max_verify_duration:
        enhanced_verify_time = 0
        enhanced_detect_count = 0
        return False

# 执行多目标检测
    objects = kpu.run_yolo2(task, img)
    if objects:
        objects = kpu.run_yolo2(task, img)
        current_count = sum(1 for obj in objects if labels[obj.classid()] == stored_number)
        enhanced_detect_count += current_count

# 结果判断
    if enhanced_detect_count >= required_count:
        enhanced_verify_time = 0
        enhanced_detect_count = 0
        return True


def normal_verify(img):
    """常规验证（前两次使用）"""
    objects = kpu.run_yolo2(task, img)
    if not objects:
        return None  # 未检测到目标返回None

    # 取置信度最高的目标
    best = max(objects, key=lambda x: x.value())
    return labels[best.classid()] == stored_number


def main():
    global current_state, stored_number,task

    try:
        # 硬件初始化
        sensor.reset()
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        sensor.set_windowing(input_size)
        sensor.set_hmirror(True)
        sensor.run(1)
        lcd.init(type=1)
        uart = init_uart()

        # 加载模型
        task = kpu.load("/sd/model-202860.kmodel")
        if not task:
            raise Exception("模型加载失败")
        kpu.init_yolo2(task, 0.5, 0.3, 5, anchors)
        while True:
            img = sensor.snapshot()

            text = uart.read()
            if text:
                try:
                    cmds = text.decode('utf-8').split('\n')
                    for cmd in cmds:
                        process_cmd(cmd.strip())
                except UnicodeError:
                    pass

            # 状态机逻辑

            if current_state == states["INIT"]:
                objects = kpu.run_yolo2(task, img)
                if objects:
                    # 遍历所有检测到的目标
                    for obj in objects:
                        pos = obj.rect()  # 获取矩形坐标(x,y,w,h)

                        # 在图像上绘制边界框
                        img.draw_rectangle(pos)

                        # 在框左上角显示标签和置信度
                        img.draw_string(pos[0], pos[1], "%s : %.2f" %(labels[obj.classid()], obj.value()), scale=2, color=(255, 0, 0))
                        num = labels[objects[0].classid()]
                        stored_number = num

                #stored_number ='3'
                        uart.write(b'\xAA\xBB' + bytes([int(stored_number)]) + b'\xBB\xAA')
                        if stored_number in ['1', '2']:
                           current_state = states["MOVING"]
                        else:
                            current_state = states["WAIT_FOR_1"]

                #stored_number ='3'
                #uart.write(b'\xAA\xBB' + bytes([int(stored_number)]) + b'\xBB\xAA')
                #if stored_number in ['1', '2']:
                #     current_state = states["MOVING"]
                #else:
                #     current_state = states["WAIT_FOR_1"]

            elif current_state == states["MOVING"]:
                # 移动中保持状态
                pass

            elif current_state == states["CHECKING"]:
                # 执行验证（结果可能是True/False/None）
                result = enhanced_verify(img) if special_verify else normal_verify(img)

                # 只在检测到目标时发送结果
                if result is not None:
                    uart.write(b'\xAA\xBB\x01\xBB\xAA' if result else b'\xAA\xBB\x00\xBB\xAA')
                    current_state = states["DONE"]
                    result_time = time.ticks_ms()  # 记录显示开始时间
                    show_result = True

            elif current_state == states["DONE"]:
                # 检查是否在显示期内
                img.draw_string(0, 0, "right" if result else "error",
                               color=(255,0,0), scale=3)

            # 显示目标病房
            if stored_number:  # 持久显示存储号码
               img.draw_string(input_size[0]-50, input_size[1]-50,
                                   stored_number,
                                   color=(255,0,0),
                                   scale=3)
            # +++ 状态显示 +++
            draw_status(img, current_state)  # 在所有状态处理完成后绘制
            lcd.display(img)
            gc.collect()

    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        if task:
            kpu.deinit(task)  # 关键！释放模型资源
        gc.collect()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        lcd.clear()
        img = image.Image(size=input_size)
        img.draw_string(0, 0, str(e), color=(255,0,0), scale=2)
        lcd.display(img)

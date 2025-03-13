import time
import socket
from zxtouch import tasktypes
from zxtouch import datahandler
from zxtouch import kbdtasktypes
from zxtouch import deviceinfotasktypes


class zxtouch(object):
    def __init__(self, ip):
        self.s = socket.socket()
        self.s.connect((str(ip), 6000))
        time.sleep(0.1)

    def touch(self, type, finger_index, x, y):
        """
            执行触摸事件

            ：参数类型：触摸式
            ：param finger_index：您要执行触摸的手指
            ：param x：x坐标
            ：param y：y坐标
            ：返回：无
        """
        if int(type) > 19:
            print("Touch index should not be greater than 19.")
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_PERFORM_TOUCH,
                                                   '1{}{:02d}{:05d}{:05d}'.format(type, finger_index, int(x * 10),
                                                                                  int(y * 10))))

    def touch_with_list(self, touch_list: list):
        """
            使用事件列表执行触摸事件
            触摸列表应该是要使用以下格式进行触摸的词典的列表

            ：param touch_list：[{“ type”：？，“ finger_index”：？，“ x”：？，“ y”：？}]
            ：返回：无
        """
        event_data = ''
        for touch_event in touch_list:
            event_data += '{}{:02d}{:05d}{:05d}'.format(touch_event['type'], touch_event['finger_index'],
                                                        touch_event['x'] * 10,
                                                        touch_event['y'] * 10)
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_PERFORM_TOUCH, str(len(touch_list)) + event_data))

    def switch_to_app(self, bundle_identifier):
        """
            将应用程序置于前台

            ：param bundle_identifier：应用程序的捆绑包标识符
            ：return：结果元组

            结果元组的格式：
            result_tuple [0]：如果在设备上执行命令时没有错误发生，则为true。否则为假
            result_tuple [1]：如果result_tuple [0] == False，则会显示错误信息。除此以外 ””
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_PROCESS_BRING_FOREGROUND, bundle_identifier))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def show_alert_box(self, title, content, duration):
        """
        在设备上显示警报框

        Args：
            title：警报框的标题
            内容：警报框的内容
            持续时间：警报框消失之前显示的时间

        返回值：
            结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_SHOW_ALERT_BOX, title, content, duration))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def run_shell_command(self, command):
        """
            以root身份在设备上运行shell命令

            ：param命令：要运行的命令
            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_RUN_SHELL, command))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def start_touch_recording(self):
        """
            开始记录触摸事件

            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_TOUCH_RECORDING_START))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def stop_touch_recording(self):
        """
            停止记录触摸事件

            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_TOUCH_RECORDING_STOP))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def accurate_usleep(self, microseconds):
        """
            不知道为什么，但是ios上的python有时无法正确睡眠。所以你可以用这个睡觉

            ：param microseconds：睡眠的微秒
            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_USLEEP, microseconds))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def play_script(self, script_absolute_path):
        """
            播放脚本

            ：param script_absolute_path：脚本的绝对路径
            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_PLAY_SCRIPT, script_absolute_path))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def force_stop_script_play(self):
        """强制停止播放当前脚本"""
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_PLAY_SCRIPT_FORCE_STOP))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def image_match(self, template_path, acceptable_value=0.8, max_try_times=4, scaleRation=0.8):
        """
            获取图像的坐标

            ：param template_path：ios设备上的模板路径
            ：param acceptable_value：对于成功的匹配，可接受的值
            ：param max_try_times：您想使用不同大小的模板尝试多少次
            ：param scaleRation：每次尝试，模板大小应为多少

            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_TEMPLATE_MATCH, template_path, max_try_times,
                                                   acceptable_value, scaleRation))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]

        return True, {"x": result[1][0], "y": result[1][1], "width": result[1][2], "height": result[1][3]}

    def show_toast(self, toast_type, content, duration, position=0, fontSize=0):
        """
            在ios设备上显示吐司

            ：param type：烤面包的类型。
            ：param content：吐司的内容
            ：param duration：烤面包的持续时间
            ：param position：烤面包的位置。顶部为0，底部为1
            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_SHOW_TOAST, toast_type, content, duration, position,
                                                   fontSize))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def pick_color(self, x, y):
        """
            从屏幕获取rgb值。返回的格式为（红色，绿色，蓝色）

            ：param x：屏幕上点的x坐标
            ：param y：屏幕上点的y坐标
            ：return：结果元组：（成功？，存储结果的error_message / dictionary）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_COLOR_PICKER, x, y))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]

        return True, {"red": result[1][0], "green": result[1][1], "blue": result[1][2]}

    def show_keyboard(self):
        """
            显示键盘

            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(
            datahandler.format_socket_data(tasktypes.TASK_KEYBOARDIMPL, kbdtasktypes.KEYBOARD_VIRTUAL_KEYBOARD, 2))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def hide_keyboard(self):
        """
            隐藏键盘

            ：return：结果元组：（成功？，error_message /返回值）
        """
        self.s.send(
            datahandler.format_socket_data(tasktypes.TASK_KEYBOARDIMPL, kbdtasktypes.KEYBOARD_VIRTUAL_KEYBOARD, 1))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def insert_text(self, text):
        """
            将文字插入文字栏位

            ：param text：要插入的文本
            ：返回：
        """
        for i, ch in enumerate(text):
            if ch == "\b":
                self.s.send(
                    datahandler.format_socket_data(tasktypes.TASK_KEYBOARDIMPL, kbdtasktypes.KEYBOARD_DELETE_CHARACTERS,
                                                   1))
                datahandler.decode_socket_data(self.s.recv(1024))
            else:
                self.s.send(
                    datahandler.format_socket_data(tasktypes.TASK_KEYBOARDIMPL, kbdtasktypes.KEYBOARD_INSERT_TEXT, ch))
                datahandler.decode_socket_data(self.s.recv(1024))
        return (True, "")

    def move_cursor(self, offset):
        """
            在文本字段上移动光标

            ：param offset：要移动的相关位置。要向左移动，偏移量应为负。对于向右移动，它应该是积极的。
            ：返回：
        """
        self.s.send(
            datahandler.format_socket_data(tasktypes.TASK_KEYBOARDIMPL, kbdtasktypes.KEYBOARD_MOVE_CURSOR, offset))
        return datahandler.decode_socket_data(self.s.recv(1024))

    def get_screen_size(self):
        """
            获取以像素为单位的屏幕尺寸

            ：return：结果元组：（成功？，存储结果的error_message / dictionary）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_GET_DEVICE_INFO,
                                                   deviceinfotasktypes.DEVICE_INFO_TASK_GET_SCREEN_SIZE))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]
        return True, {"width": result[1][0], "height": result[1][1]}

    def get_screen_orientation(self):
        """
            获取屏幕方向

            ：return：结果元组：（成功？，error_message /屏幕方向（str，可以转换为int））
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_GET_DEVICE_INFO,
                                                   deviceinfotasktypes.DEVICE_INFO_TASK_GET_SCREEN_ORIENTATION))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]
        return True, result[1][0]

    def get_screen_scale(self):
        """
            获取屏幕比例

            ：return：结果元组：（成功？，error_message / screen scale（str，可以转换为int））
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_GET_DEVICE_INFO,
                                                   deviceinfotasktypes.DEVICE_INFO_TASK_GET_SCREEN_SCALE))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]
        return True, result[1][0]

    def get_device_info(self):
        """
            获取设备信息

            ：return：结果元组：（成功？，存储设备信息的error_message / dictionary）
        """
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_GET_DEVICE_INFO,
                                                   deviceinfotasktypes.DEVICE_INFO_TASK_GET_DEVICE_INFO))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]
        return True, {"name": result[1][0], "system_name": result[1][1], "system_version": result[1][2],
                      "model": result[1][3], "identifier_for_vendor": result[1][4]}

    def get_battery_info(self):
        self.s.send(datahandler.format_socket_data(tasktypes.TASK_GET_DEVICE_INFO,
                                                   deviceinfotasktypes.DEVICE_INFO_TASK_GET_BATTERY_INFO))
        result = datahandler.decode_socket_data(self.s.recv(1024))
        if not result[0]:
            return False, result[1]
        battery_state_return = int(result[1][0])
        battery_state_list = ["Unknown", "Unplugged", "Charging", "Full"]

        return True, {"battery_state": result[1][0], "battery_level": str(int(float(result[1][1]))),
                      "battery_state_string": battery_state_list[battery_state_return]}  # state: 0 unknown, 1 unplegged, 2 charging, 3 full

    def disconnect(self):
        self.s.close()


if __name__ == '__main__':
    dd = zxtouch("192.168.1.68")
    # print(dd.touch(1, 1, 600, 700))
    print(dd.run_shell_command("cd /var/mobile/&&python3 ocrtra.py"))
    # print(dd.switch_to_app('com.omz-software.Pythonista3'))
    print(dd.accurate_usleep(100000000))
    # print(dd.switch_to_app('com.omz-software.Pythonista3'))
    # dd.start_touch_recording()
import time
from datetime import date, timedelta
from PIL import Image, ImageFont, ImageDraw

from code.QQ_Email import fasong

ziti = 'D:/code/qd_script/image/iOS字体.ttf'  # 字体
image = 'D:/code/qd_script/image/chu.jpg'  # 消除的图片


def addText(image_path):
    try:
        text = time.strftime('%H:%M', time.localtime(time.time()))
        img = Image.open(image_path)  # 打开图像
        img2 = Image.open(image)  # 遮挡图片
        img2 = img2.crop((0, 0, 170, 50))
        img.paste(img2, (490, 0))  # 删除坐标上的时间

        vv = 337  # 位置变量
        i = 0  # 日期变量
        while i < 5:  # 在图片上画日期
            img.paste(img2, (891, vv))  # 删除坐标上的日期
            vv += 345
            i += 1

        width, height = img.size
        ttfont = ImageFont.truetype(ziti, int(height / 55))  # 设置字体
        draw = ImageDraw.Draw(img)  # 创建画画对象
        draw.text((int(width / 2 - 45), 4), text, (0, 0, 0), font=ttfont)  # 在新建的对象 上坐标（50,50）处开始画出时间文本

        vv = 337  # 位置变量
        i = 0  # 日期变量
        ttfont = ImageFont.truetype(ziti, int(height / 68))  # 设置字体
        while i < 5:  # 在图片上画日期
            t = date.today() + timedelta(-i)
            text = t.strftime('%Y-%m-%d')
            draw.text((891, vv), text, (170, 170, 170), font=ttfont)  # 在新建的对象 上坐标（50,50）处开始画出日期文本
            vv += 345
            i += 1
        img.save(image_path)
        print('图片修改完成')
        # img.show()
    except Exception as e:
        fasong('图片添加失败，快去重发签到照片！' + str(e))  # 发给qq邮箱
        # print('图片添加失败，快去重发签到照片！' + str(e))

# addText('D:/code/qd_script/image/12.jpg')

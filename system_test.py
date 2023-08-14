import base64
import os.path

import psutil
import platform
import math
import httpx
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import time
import io

font_path = "plugins/qchat_system_status/SimHei.ttf"
# 模拟启动时间变量
qchat_time = time.time()


class Status:
    def __init__(self, percent, name, text):
        self.percent = percent  # 百分比
        self.name = name  # 名称
        self.text = text  # 文本信息


def get_random_bg():
    try:
        session = httpx.Client()
        url = "https://api.yimian.xyz/img?type=moe"
        image_io = io.BytesIO(session.get(url, follow_redirects=True).content)
        return image_io
    except Exception as e:
        return "", e


def getavataricon(qq_num):
    try:
        session = httpx.Client()
        url = f"https://q4.qlogo.cn/g?b=qq&nk={qq_num}&s=640"
        return session.get(url).content
    except Exception as e:
        return "", e


def getnickname(qq):
    try:
        session = httpx.Client()
        url = f"https://users.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={qq}"
        text = session.get(url).content
        # .replace("portraitCallBack", "").encode('gbk').decode('utf-8')
        print(text)
        v = eval(text)

        return v[str(qq)][6]
    except Exception as e:
        return "", e


def botruntime():
    try:
        boot_time = psutil.boot_time()
        now = time.time()
        sys_uptime_seconds = int(now - boot_time) % 60
        sys_uptime_minutes = int(now - boot_time) // 60 % 60
        sys_uptime_hours = int(now - boot_time) // 60 // 60 % 60
        sys_uptime_days = int(now - boot_time) // 60 // 60 // 60 % 24
        qchat_uptime_seconds = int(now - qchat_time) % 60
        qchat_uptime_minutes = int(now - qchat_time) // 60 % 60
        qchat_uptime_hours = int(now - qchat_time) // 60 // 60 % 60
        qchat_uptime_days = int(now - qchat_time) // 60 // 60 // 60 % 24
        return f"QChatGPT 已运行 {int(qchat_uptime_days)} 天 {qchat_uptime_hours}:{qchat_uptime_minutes}:{qchat_uptime_seconds} | 系统运行 {int(sys_uptime_days)} 天 {sys_uptime_hours}:{sys_uptime_minutes}:{sys_uptime_seconds}"
    except Exception as e:
        return "", e


def botstatus():
    try:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
        return f"{current_time} | 由 Python {platform.python_version()} 运行 | {platform.system()}"
    except Exception as e:
        return "", e


def basicstate():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)  # 获取 CPU 使用率
        cpu_freq = psutil.cpu_freq()  # 获取 CPU 频率
        cpu_times = f"最大 {cpu_freq.max / 1000}Ghz"  # CPU 频率的最大值
        vm = psutil.virtual_memory()  # 获取内存信息
        swap = psutil.swap_memory()  # 获取交换空间信息

        return [
            Status(
                math.ceil(cpu_percent), "CPU", [f"{psutil.cpu_count()} 核心", cpu_times]
            ),
            Status(
                math.ceil(vm.percent),
                "RAM",
                [
                    f"总共 {vm.total / 1024 / 1024 / 1024:.2f}GB",
                    f"已用 {vm.used / 1024 / 1024 / 1024:.2f}GB",
                    f"剩余 {vm.available / 1024 / 1024 / 1024:.2f}GB",
                ],
            ),
            Status(
                math.ceil(swap.percent),
                "SWAP",
                [
                    f"总共 {swap.total / 1024 / 1024 / 1024:.2f}GB",
                    f"已用 {swap.used / 1024 / 1024 / 1024:.2f}GB",
                    f"剩余 {swap.free / 1024 / 1024 / 1024:.2f}GB",
                ],
            ),
        ]
    except Exception as e:
        return [], e


def diskstate():
    try:
        stateinfo = []
        for part in psutil.disk_partitions():
            usage = psutil.disk_usage(part.mountpoint)  # 获取磁盘使用情况
            stateinfo.append(
                Status(
                    math.ceil(usage.percent),
                    part.mountpoint,
                    [
                        f"{usage.used / 1024 / 1024 / 1024:.1f}GB/{usage.total / 1024 / 1024 / 1024:.1f}GB"
                    ],
                )
            )
        return stateinfo
    except Exception as e:
        return [], e


def moreinfo():
    try:
        hostinfo = platform.uname()  # 获取主机信息
        cpuinfo = platform.processor()  # 获取 CPU 信息
        from pkg.plugin.host import __plugins__

        stateinfo = [
            Status(None, "OS", [hostinfo.system]),  # 操作系统
            Status(None, "CPU", [cpuinfo]),  # CPU
            Status(None, "Version", [hostinfo.version]),  # 操作系统版本
            Status(
                None, "Plugin", ["共 " + str(len(__plugins__)) + " 个插件"]
            )
        ]
        return stateinfo
    except Exception as e:
        return [], e


def drawstatus(qq="", img_path="", nickname="", create_by=True):
    try:
        disk_state = [(i.name, i.text, i.percent) for i in diskstate()]
    except Exception as err:
        return None, err
    diskcardh = 40 + (30 + 70) * len(disk_state) + 40
    try:
        more_info = [(i.name, i.text, i.percent) for i in moreinfo()]
    except Exception as err:
        return None, err

    moreinfocardh = 30 + (30 + 45) * len(more_info) + 30 - 10
    if img_path != 0 and os.path.exists(img_path):
        background_image = Image.open(img_path)
    else:
        background_image = Image.open(get_random_bg())
    background_image = background_image.filter(ImageFilter.GaussianBlur(radius=6))
    canvas = Image.new(
        "RGBA",
        (
            1280,
            int(70 + 250 + 40 + 380 + diskcardh + 40 + moreinfocardh + 40 + 70 + 30),
        ),
        (255, 255, 255, 255),
    )
    bh, bw, ch, cw = (
        background_image.height,
        background_image.width,
        canvas.height,
        canvas.width,
    )
    if bh / bw < ch / cw:
        scaled_width = int(bw * ch / bh)
        scaled_height = int(bh * ch / bh)
        back = background_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        canvas.paste(
            back,
            (
                canvas.width // 2 - scaled_width // 2,
                canvas.height // 2 - scaled_height // 2,
            ),
        )
    else:
        scaled_width = int(bw * cw / bw)
        scaled_height = int(bh * cw / bw)
        back = background_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        canvas.paste(back, (0, 0))

    cardw = canvas.width - 70 - 70
    titlecardh = 250
    titlecard = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    titledraw = ImageDraw.Draw(titlecard, "RGBA")
    titledraw.rounded_rectangle(
        ((70, 70), (70 + cardw, 70 + titlecardh)),
        radius=20,
        width=1,
        outline=(255, 255, 255, 160),
        fill=(255, 255, 255, 140),
    )
    if qq != "":
        avatar = Image.open(io.BytesIO(getavataricon(qq)))
    else:
        avatar = Image.new("RGBA", (640, 640), (255, 255, 255, 255))
    avatar = avatar.resize((titlecardh - 20 - 20, titlecardh - 20 - 20), Image.LANCZOS)
    avatar_w, _ = avatar.size
    avatar_alpha_layer = Image.new("L", (avatar_w, avatar_w), 0)
    avatar_draw = ImageDraw.Draw(avatar_alpha_layer)
    avatar_draw.ellipse((0, 0, avatar_w, avatar_w), fill=255)
    circle_avatar = Image.new("RGBA", avatar.size)
    circle_avatar.paste(avatar, mask=avatar_alpha_layer)
    avatar_distance = (titlecardh - avatar.height) // 2
    titlecard.paste(
        circle_avatar,
        (70 + avatar_distance, 70 + avatar_distance),
        mask=avatar_alpha_layer,
    )
    font = ImageFont.truetype(font_path, 80)
    text = nickname
    nick_x, nick_y = (70 + avatar_distance * 2 + avatar_w, 90)
    font_color = (0, 0, 0)
    titledraw.text((nick_x - 2, nick_y), text, font=font, fill=font_color)
    titledraw.text((nick_x + 2, nick_y), text, font=font, fill=font_color)
    line_x = 70 + avatar_distance * 2 + avatar_w
    line_y = 70 + avatar_distance + avatar_w // 2
    titledraw.line((line_x, line_y, line_x + 700, line_y), width=3, fill=font_color)
    font = ImageFont.truetype(font_path, 28)
    runtime_x, runtime_y = (line_x, line_y + 25)
    titledraw.multiline_text(
        text=botruntime() + "\n" + botstatus(),
        xy=(runtime_x, runtime_y),
        font=font,
        fill=font_color,
    )

    ######################################################
    basiccardh = 440
    basiccard = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    basicdraw = ImageDraw.Draw(basiccard, "RGBA")
    basicdraw.rounded_rectangle(
        ((70, 70 + titlecardh + 50), (70 + cardw, 70 + titlecardh + 30 + basiccardh)),
        radius=30,
        width=1,
        outline=(255, 255, 255, 160),
        fill=(255, 255, 255, 140),
    )
    basic_text = basicstate()
    cpu_basic_item = ""
    ram_basic_item = ""
    swap_basic_item = ""
    for i in basic_text[0].text:
        cpu_basic_item += i + "\n"
    for i in basic_text[1].text:
        ram_basic_item += i + "\n"
    for i in basic_text[2].text:
        swap_basic_item += i + "\n"
    name_font = ImageFont.truetype(font_path, 55)
    basic_font = ImageFont.truetype(font_path, 30)

    def draw_ellipse(draw, xy_range, fill_color):
        draw.ellipse(xy_range, fill=fill_color)

    def draw_text_bold(draw, xy, text, font, fill, anchor=None, align=None):
        draw.text(
            xy=(xy[0] + 1, xy[1]),
            text=text,
            font=font,
            fill=fill,
            anchor=anchor,
            align=align,
        )
        draw.text(
            xy=(xy[0] - 1, xy[1]),
            text=text,
            font=font,
            fill=fill,
            anchor=anchor,
            align=align,
        )

    def draw_multiline_text(draw, xy, text, font, fill, anchor="mm", align="left"):
        draw.multiline_text(
            xy=xy, text=text, font=font, fill=fill, anchor=anchor, align=align
        )

    def get_percent_color(precent):
        if int(precent) > 90:
            color = (255, 70, 0, 255)
        elif int(precent) > 70:
            color = (255, 165, 0, 255)
        else:
            color = (145, 240, 145, 255)
        return color

    draw_ellipse(
        basicdraw,
        [
            (175 + 10, 50 + 70 + titlecardh + 20),
            (435 - 10, 50 + 70 + titlecardh + 50 + 230 - 20),
        ],
        (235, 235, 235, 255),
    )
    draw_ellipse(
        basicdraw,
        [
            (205 + 10, 50 + 70 + titlecardh + 50),
            (405 - 10, 50 + 70 + titlecardh + 50 + 200 - 20),
        ],
        "white",
    )
    basicdraw.text(
        xy=(
            (175 + 435) // 2,
            (50 + 70 + titlecardh + 50 + 70 + titlecardh + 50 + 230) // 2,
        ),
        text=str(basic_text[0].percent) + "%",
        font=name_font,
        anchor="mm",
        fill=(205, 205, 205, 255),
    )
    draw_ellipse(
        basicdraw,
        [
            (175 + 10 + 200 + 135, 50 + 70 + titlecardh + 20),
            (435 - 10 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 - 20),
        ],
        (235, 235, 235, 255),
    )
    draw_ellipse(
        basicdraw,
        [
            (205 + 10 + 200 + 135, 50 + 70 + titlecardh + 50),
            (405 - 10 + 200 + 135, 50 + 70 + titlecardh + 50 + 200 - 20),
        ],
        "white",
    )
    basicdraw.text(
        xy=(
            (175 + 200 + 135 + 435 + 200 + 135) // 2,
            (50 + 70 + titlecardh + 50 + 70 + titlecardh + 50 + 230) // 2,
        ),
        text=str(basic_text[1].percent) + "%",
        font=name_font,
        anchor="mm",
        fill=(205, 205, 205, 255),
    )
    draw_ellipse(
        basicdraw,
        [
            (175 + 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 20),
            (435 - 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 50 + 230 - 20),
        ],
        (235, 235, 235, 255),
    )
    draw_ellipse(
        basicdraw,
        [
            (205 + 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 50),
            (405 - 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 50 + 200 - 20),
        ],
        "white",
    )
    basicdraw.text(
        xy=(
            (205 + 10 + 200 + 200 + 135 + 135 + 405 - 10 + 200 + 200 + 135 + 135) // 2,
            (50 + 70 + titlecardh + 50 + 50 + 70 + titlecardh + 50 + 200 - 20) // 2,
        ),
        text=str(basic_text[2].percent) + "%",
        font=name_font,
        anchor="mm",
        fill=(205, 205, 205, 255),
    )
    draw_text_bold(
        basicdraw,
        (305, 50 + 70 + titlecardh + 50 + 230 + 10),
        basic_text[0].name,
        name_font,
        font_color,
        anchor="mm",
    )
    draw_multiline_text(
        basicdraw,
        (307, 50 + 70 + titlecardh + 50 + 230 + 90),
        cpu_basic_item,
        basic_font,
        font_color,
        align="center",
    )
    draw_text_bold(
        basicdraw,
        (305 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 + 10),
        basic_text[1].name,
        name_font,
        font_color,
        anchor="mm",
    )
    draw_multiline_text(
        basicdraw,
        (307 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 + 95),
        ram_basic_item,
        basic_font,
        font_color,
        align="center",
    )
    draw_text_bold(
        basicdraw,
        (305 + 200 + 135 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 + 10),
        basic_text[2].name,
        name_font,
        font_color,
        anchor="mm",
    )
    draw_multiline_text(
        basicdraw,
        (307 + 200 + 135 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 + 95),
        swap_basic_item,
        basic_font,
        font_color,
        align="center",
    )
    basicdraw.arc(
        (
            (175 + 10, 50 + 70 + titlecardh + 20),
            (435 - 10, 50 + 70 + titlecardh + 50 + 230 - 20),
        ),
        start=-90,
        end=270 * basic_text[0].percent // 100 - 90,
        fill=get_percent_color(basic_text[0].percent),
        width=30,
    )
    basicdraw.arc(
        (
            (175 + 10 + 200 + 135, 50 + 70 + titlecardh + 20),
            (435 - 10 + 200 + 135, 50 + 70 + titlecardh + 50 + 230 - 20),
        ),
        start=-90,
        end=270 * basic_text[1].percent // 100 - 90,
        fill=get_percent_color(basic_text[1].percent),
        width=30,
    )
    basicdraw.arc(
        (
            (175 + 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 20),
            (435 - 10 + 200 + 200 + 135 + 135, 50 + 70 + titlecardh + 50 + 230 - 20),
        ),
        start=-90,
        end=270 * basic_text[2].percent // 100 - 90,
        fill=get_percent_color(basic_text[2].percent),
        width=30,
    )

    #######################################################
    def diskdraw_rounded_rectangle(
        draw, xy_range, fill_color, radius, font_color, font, info, index
    ):
        if int(info[2]) > 90:
            over_color = (255, 70, 0, 255)
        elif int(info[2]) > 70:
            over_color = (255, 165, 0, 255)
        else:
            over_color = (145, 240, 145, 255)
        draw.rounded_rectangle(
            xy=(
                (xy_range[0][0], xy_range[0][1] + (70 + 30) * index),
                (xy_range[1][0] + 990, xy_range[1][1] + (70 + 30) * index),
            ),
            radius=radius,
            fill=fill_color,
        )
        draw.rounded_rectangle(
            xy=(
                (xy_range[0][0], xy_range[0][1] + (70 + 30) * index),
                (
                    xy_range[1][0] + 990 * (int(info[2]) / 100),
                    xy_range[1][1] + (70 + 30) * index,
                ),
            ),
            radius=radius,
            fill=over_color,
        )
        draw_text_bold(
            draw,
            xy=(
                xy_range[0][0] + 70,
                (
                    (xy_range[0][1] + (70 + 30) * index)
                    + (xy_range[1][1] + (70 + 30) * index)
                )
                // 2,
            ),
            text=info[0],
            fill=font_color,
            font=font,
            anchor="mm",
        )
        draw_text_bold(
            draw,
            xy=(
                xy_range[0][0] + 970,
                (
                    (xy_range[0][1] + (70 + 30) * index)
                    + (xy_range[1][1] + (70 + 30) * index)
                )
                // 2,
            ),
            text=info[1][0],
            fill=font_color,
            font=font,
            anchor="rm",
        )
        draw_text_bold(
            draw,
            xy=(
                70 + cardw - 15,
                (
                    (xy_range[0][1] + (70 + 30) * index)
                    + (xy_range[1][1] + (70 + 30) * index)
                )
                // 2,
            ),
            text=str(info[2]) + "%",
            fill=font_color,
            font=font,
            anchor="rm",
        )

    diskcard = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    diskdraw = ImageDraw.Draw(diskcard, "RGBA")
    diskdraw.rounded_rectangle(
        (
            (70, 70 + titlecardh + 50 + basiccardh + 30),
            (70 + cardw, 70 + titlecardh + 30 + basiccardh + 30 + diskcardh),
        ),
        radius=30,
        width=1,
        outline=(255, 255, 255, 160),
        fill=(255, 255, 255, 140),
    )

    for i, index in zip(disk_state, range(len(disk_state))):
        diskdraw_rounded_rectangle(
            draw=diskdraw,
            xy_range=[
                (70 + 40, 70 + titlecardh + 50 + basiccardh + 30 + 40),
                (70 + 40, 70 + titlecardh + 50 + basiccardh + 30 + 40 + 70),
            ],
            radius=20,
            fill_color=(211, 211, 211, 255),
            font_color=(0, 0, 0, 255),
            font=ImageFont.truetype(font_path, 45),
            info=i,
            index=index,
        )

    #######################################################
    def draw_more_info(draw, xy_range, font_color, font, info, index):
        draw_text_bold(
            draw,
            xy=(xy_range[0], xy_range[1] + (30 + 45) * index),
            text=info[0],
            fill=font_color,
            font=font,
            anchor="lm",
        )
        draw_text_bold(
            draw,
            xy=(70 + cardw - 20, xy_range[1] + (30 + 45) * index),
            text=info[1][0],
            fill=font_color,
            font=font,
            anchor="rm",
        )

    moreinfocard = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    moreinfodraw = ImageDraw.Draw(moreinfocard, "RGBA")
    moreinfodraw.rounded_rectangle(
        (
            (70, 70 + titlecardh + 50 + basiccardh + 30 + diskcardh + 30),
            (
                70 + cardw,
                70 + titlecardh + 30 + basiccardh + 30 + diskcardh + 30 + moreinfocardh,
            ),
        ),
        radius=30,
        width=1,
        outline=(255, 255, 255, 160),
        fill=(255, 255, 255, 140),
    )
    for i, index in zip(more_info, range(len(more_info))):
        draw_more_info(
            moreinfodraw,
            xy_range=(
                70 + 20,
                70 + titlecardh + 50 + basiccardh + 30 + diskcardh + 30 + 60,
            ),
            font=ImageFont.truetype(font_path, 45),
            info=i,
            index=index,
            font_color=(0, 0, 0, 255),
        )
    #######################################################
    if create_by:
        ctreat_by = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        ctreat_by_draw = ImageDraw.Draw(ctreat_by, "RGBA")
        text = "Created By QchatSystemStatus V0.0.1"
        draw_text_bold(
            ctreat_by_draw,
            (canvas.width / 2, canvas.height - 40),
            text,
            ImageFont.truetype(font_path, 38),
            (255, 255, 255, 255),
            anchor="mm",
            align="center",
        )
        canvas.alpha_composite(ctreat_by)
    #######################################################
    canvas.alpha_composite(titlecard)
    canvas.alpha_composite(basiccard)
    canvas.alpha_composite(diskcard)
    canvas.alpha_composite(moreinfocard)
    # canvas.show()
    image_io = io.BytesIO()
    canvas.save(image_io, "PNG")
    image_data = image_io.getvalue()
    img_base64 = base64.b64encode(image_data).decode("utf-8")
    return img_base64


if __name__ == "__main__":
    print(drawstatus())

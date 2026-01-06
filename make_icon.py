from PIL import Image, ImageDraw

def create_icon():
    # 创建一个 256x256 的蓝色背景
    size = (256, 256)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 画一个蓝色的圆角矩形作为底色
    draw.rounded_rectangle([20, 40, 236, 216], radius=20, fill=(33, 150, 243))
    
    # 画一个简单的文件夹形状
    draw.rectangle([60, 80, 196, 170], fill="white")
    draw.polygon([(60, 80), (100, 60), (140, 80)], fill="white")

    # 保存为 ico 格式
    image.save('app.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print("图标 app.ico 已生成")

if __name__ == "__main__":
    create_icon()
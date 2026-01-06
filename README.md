## AI生成代码
 将txt需求说明发给 AI Gemini

 自动生成 main.py 和make_icon.py
## 生成图标
### 安装pillow 用于图标生成
pip install pyinstaller pillow
### 生成图片 CMD
python make_icon.py

## 打包 CMD
  pyinstaller --onefile --console --icon=app.ico --name "项目归档生成器" main.py

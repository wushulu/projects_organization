## AI生成代码
 将'项目归档.txt'需求说明发给 AI Gemini

 自动生成 main.py 和make_icon.py
## 生成图标
### 安装pillow 用于图标生成 CMD
<pre><code id="code-block">
pip install pyinstaller pillow
</code></pre>
<button onclick="copyCode()"></button>

### 生成图片 CMD
<pre><code id="code-block">
python make_icon.py
</code></pre>
<button onclick="copyCode()"></button>

## 打包 CMD
  
<pre><code id="code-block">
pyinstaller --onefile --console --icon=app.ico --name "项目归档生成器" main.py
</code></pre>
<button onclick="copyCode()"></button>

# app.py 內容
from flask import Flask

app = Flask(__name__)

# 定義一個根路徑 / 的處理程序
@app.route("/")
def index():
    # 這是服務器回傳給請求的內容
    return "Hello, Cloud Run Test! I'm running and doing nothing useful."

# 為了與 Gunicorn 配合，我們不需要在這裡運行 app.run()
# Gunicorn 會調用 app:app 來啟動應用程式

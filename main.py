# main.py - FastAPI Application
from fastapi import FastAPI
import os

# 創建 FastAPI 實例
app = FastAPI(
    title="CGCG Auth Service",
    version="1.0.0",
    description="Minimal FastAPI application for Cloud Run testing."
)

# 獲取 PORT 變數，用於日誌輸出或驗證
PORT = os.environ.get('PORT', '8080')

# 定義一個簡單的根路徑
@app.get("/")
def read_root():
    """
    健康檢查和基本資訊端點。
    """
    return {
        "message": "Hello from FastAPI on Cloud Run!",
        "status": "Running",
        "port": PORT
    }

# 提示：Uvicorn 在 Dockerfile 的 CMD 中會被調用，它將啟動 app 實例。
# 在這個文件中不需要額外調用 uvicorn.run(app, ...)。

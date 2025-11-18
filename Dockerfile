# --- 階段一：依賴項構建 (Builder Stage) ---
# 使用 python:3.11-slim 作為構建環境
FROM python:3.11-slim as builder

# 設置工作目錄
WORKDIR /app

# 複製依賴文件並安裝到 /install 目錄
# 這是確保依賴項在最終環境中存在的關鍵步驟
COPY requirements.txt .

# 運行 pip 安裝所有依賴項到指定的 /install 目錄
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --target=/install -r requirements.txt

# --- 階段二：最終運行映像檔 (Runtime Stage) ---
# 使用相同的 python:3.11-slim，但只包含必要的組件
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 從第一階段複製安裝好的依賴項到最終映像檔的 Python 路徑
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# 複製您的應用程式程式碼
# 我們假設您的應用程式入口文件是 main.py
COPY main.py .

# 暴露端口 (僅供記錄)
EXPOSE 8080

# 設置 Cloud Run 必須監聽的端口（雖然 Cloud Run 會自動設置）
# ENV PORT 8080 # 這裡不需要設置，但您可以在這裡檢查確保它沒有被錯誤地設置

# ***最終啟動命令：使用 Uvicorn (Shell 格式)***
# 確保 $PORT 變數被正確展開。
# main:app 指向 main.py 檔案中的 app 實例。
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}

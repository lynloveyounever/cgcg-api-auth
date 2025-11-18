# 使用最小的 Linux 基礎映像檔，以保持映像檔尺寸最小
FROM python:3.11-alpine

# 安裝一個輕量級的 Web 服務器 Gunicorn
RUN pip install gunicorn

# 定義 Cloud Run 服務必須監聽的端口（預設為 8080）
ENV PORT 8080

# 複製一個最小的 Python 檔案作為 Web 應用程式
COPY app.py .

# 暴露端口 (非必需，但有助於文件記錄)
EXPOSE 8080

# 啟動 Gunicorn，監聽 0.0.0.0:$PORT，並運行 app.py 裡的應用程式
CMD gunicorn --bind 0.0.0.0:$PORT app:app

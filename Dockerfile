FROM python:3.10-slim

# 安裝 Tesseract OCR 系統套件（含繁體中文與英文包）
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案原始碼
COPY . .

# 啟動網頁服務
CMD ["python", "app.py"]

from flask import Flask, render_template_string, request, redirect, jsonify
import pytesseract
from PIL import Image
import io
import json
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
DATA_FILE = "products.json"
SUBSCRIBERS_FILE = "subscribers.json"

GMAIL = "g9607111@gmail.com"
import os
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

import os
from pymongo import MongoClient

# 1. 初始化資料庫連線 (這段放在 import 下方)
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client['saver_db']  # 明確指定資料庫名稱為 'saver_db'
products_col = db.products

# 2. 修改 load_products 函式 (取代原本的第 12-16 行)
def load_products():
    # 改為從 MongoDB 撈取資料
    return list(products_col.find({}, {"_id": 0}))

# 3. 修改 save_products 函式 (取代原本的第 18-20 行)
def save_products(products):
    # 先清空資料庫內的舊資料，再存入新的
    products_col.delete_many({})
    if products:
        products_col.insert_many(products)
# 1. 在程式碼上方宣告 collection (緊接在 products_col 後面)
subscribers_col = db.subscribers

# 1. 宣告 subscribers collection
subscribers_col = db.subscribers

# 2. 修改 load_subscribers 函式
def load_subscribers():
    # 從 MongoDB 撈取資料，回傳 email 列表
    subscribers = list(subscribers_col.find({}, {"_id": 0}))
    return [s['email'] for s in subscribers] if subscribers else []

# 3. 修改 save_subscribers 函式
def save_subscribers(subscriber_list):
    # 先清空資料庫內的舊資料
    subscribers_col.delete_many({})
    # 存入新的訂閱者列表
    if subscriber_list:
        data_to_insert = [{"email": email} for email in subscriber_list]
        subscribers_col.insert_many(data_to_insert)
        
def send_email_to_all(product):
    if product.get('discount', 0) < 15:
        return
    subscribers = load_subscribers()
    for email in subscribers:
        try:
            msg = MIMEMultipart()
            msg["From"] = GMAIL
            msg["To"] = email
            msg["Subject"] = f"🚨【省錢獵人】發現破盤好貨：{product['name']}"
            body = f"商品：{product['name']}\n特價：{product['sale_price']}\n連結：{product['affiliate_link']}"
            msg.attach(MIMEText(body, "plain", "utf-8"))
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(GMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL, email, msg.as_string())
            server.quit()
        except Exception as e:
            # 這樣在 Render 的 Logs 中，你就會看到具體的錯誤訊息
            print(f"🚨 發信給 {email} 失敗，錯誤原因：{e}")

import requests
from bs4 import BeautifulSoup

crawl_threads()
def crawl_shopee():
    print("🛒 獵人正在搜尋蝦皮商品...")
    findings = []
    
    # 這裡示範使用 API 獲取資料 (請替換為真實 API 或邏輯)
    # 你可以去 RapidAPI 找免費的 Shopee API 來替換這裡的 URL
    try:
        # 這是一個範例架構，你需要替換成實際運作的 API 連結
        # response = requests.get("https://api.shopee-example.com/search?keyword=二手")
        # data = response.json()
        
        # 為了讓你現在能看到效果，我們先模擬抓到的資料
        findings.append({
            "name": "【蝦皮自動偵測】二手精選商品",
            "market_price": 1200,
            "sale_price": 900,
            "discount": 25,
            "description": "來自蝦皮的優惠商品",
            "affiliate_link": "https://shopee.tw"
        })
    except Exception as e:
        print(f"蝦皮爬蟲發生錯誤: {e}")
        
    return findings
        
def run_scraping_job():
    print("📢 獵人出動：開始全平台搜尋...")
    
    # 合併兩個平台的資料
    new_findings = crawl_threads() + crawl_shopee()
    
    if new_findings:
        all_products = load_products()
        all_products.extend(new_findings)
        save_products(all_products)
        # 如果有多個商品，可以選擇性地分別發送 Email
        for p in new_findings:
            send_email_to_all(p)
        print(f"✅ 狩獵成功！本次新增 {len(new_findings)} 件商品。")
    else:
        print("⚠️ 本次巡邏未發現新商品。")
# --- HTML 模板介面優化 ---
TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>省錢獵人 Saver Hunter</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f0f2f5; }
  .header { background: linear-gradient(135deg, #2c3e50, #2980b9); color: white; padding: 30px 20px; text-align: center; }
  .header h1 { font-size: 32px; font-weight: bold; }
  .header p { opacity: 0.9; margin-top: 8px; font-size: 15px; }
  .container { max-width: 900px; margin: 20px auto; padding: 0 15px; }
  .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .stats { display: flex; gap: 15px; margin-bottom: 20px; }
  .stat { flex: 1; background: white; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .stat h2 { color: #2980b9; font-size: 28px; }
  .stat p { color: #666; font-size: 14px; }
  .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; }
  .product-card { background: white; border-radius: 12px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 4px solid #2980b9; position: relative;}
  .product-card h3 { font-size: 15px; margin-bottom: 10px; color: #333; }
  .original-price { color: #999; text-decoration: line-through; font-size: 14px; }
  .sale-price { color: #e74c3c; font-size: 22px; font-weight: bold; }
  .badge { display: inline-block; background: #e74c3c; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; margin: 8px 0; font-weight: bold; }
  .btn { display: block; text-align: center; background: #2980b9; color: white; padding: 10px; border-radius: 8px; text-decoration: none; margin-top: 10px; font-weight: bold; }
  .btn:hover { background: #2471a3; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; font-weight: bold; color: #444; }
  input[type=email] { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
  .submit-btn { background: #e74c3c; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }
  .admin-link { text-align: right; margin-bottom: 10px; }
  .admin-link a { color: #999; font-size: 13px; }
  .success { background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
</style>
</head>
<body>
<div class="header">
  <h1>🏹 省錢獵人 Saver Hunter</h1>
  <p>💡 AI 24h 跨平台巡邏｜精準圖文 OCR 識圖｜低於市價 15% 自動秒發警示</p>
</div>

<div class="container">
  {% if success %}
  <div class="success">✅ {{ success }}</div>
  {% endif %}

  <div class="stats">
    <div class="stat">
      <h2>{{ products|length }}</h2>
      <p>🤖 巡邏監控中商品</p>
    </div>
    <div class="stat">
      <h2>{{ subscriber_count }}</h2>
      <p>📧 警示接收人數</p>
    </div>
    <div class="stat">
      <h2>AI 即時</h2>
      <p>手寫與折價券偵測速度</p>
    </div>
  </div>

  {% if products %}
  <h2 style="margin-bottom:15px">📦 24H 巡邏發現好貨</h2>
  <div class="product-grid">
    {% for p in products %}
    <div class="product-card">
      <h3>{{ p.name }}</h3>
      <div class="original-price">市場均價 NT$ {{ p.market_price }}</div>
      <div class="sale-price">NT$ {{ p.sale_price }}</div>
      <span class="badge" style="background: {% if p.discount >= 15 %}#e74c3c{% else %}#f39c12{% endif %};">
        🔥 低於市價 {{ p.discount }}% {% if p.discount >= 15 %}(已觸發警示){% endif %}
      </span>
      <p style="font-size:13px;color:#666;margin:8px 0">{{ p.description }}</p>
      <a href="{{ p.affiliate_link }}" class="btn" target="_blank">👉 立即搶購</a>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="card" style="text-align:center;color:#999;padding:40px">
    <p style="font-size:40px">🔍</p>
    <p>AI 全天候巡邏中，目前暫無新貼文好貨，請稍後再來！</p>
  </div>
  {% endif %}

  <br>
  <div class="card">
    <h2 style="margin-bottom:15px">🔔 訂閱 15% 破盤秒發通知</h2>
    <p style="color:#666;margin-bottom:15px">當 AI 識圖偵測到低於市場均價 15% 的暴跌好貨時，立刻發信通知你！</p>
    <form method="POST" action="/subscribe">
      <div class="form-group">
        <label>接收通知 Email</label>
        <input type="email" name="email" placeholder="請輸入您的電子信箱" required>
      </div>
      <button class="submit-btn">開啟 AI 破盤警示 🔔</button>
    </form>
  </div>

  <div class="admin-link"><a href="/admin">AI 管理與手動錄入後台</a></div>
</div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>省錢獵人控制台</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 0 15px; background: #f4f6f7; }
  h1 { color: #2c3e50; margin-bottom: 10px; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; font-weight: bold; }
  input { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
  button { background: #2980b9; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }
  .back { display: inline-block; margin-bottom: 20px; color: #2980b9; text-decoration: none; }
  .item { background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
  .delete-btn { background: #e74c3c; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; width: auto; margin: 0; }
  .success { background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
  .ocr-box { background: #eaf2f8; border: 2px dashed #2980b9; border-radius: 12px; padding: 20px; margin-bottom: 25px; text-align: center; }
</style>
</head>
<body>
<a class="back" href="/">← 返回省錢獵人首頁</a>
<h1>🛠 省錢獵人控制中心</h1>
<p style="color:#666;margin-bottom:20px">當前訂閱：<strong>{{ subscriber_count }} 人</strong></p>

<div class="ocr-box">
  <h3 style="color: #2980b9; margin-bottom: 5px;">📸 功能二：AI 貼文與手寫價格識圖 (OCR)</h3>
  <p style="font-size: 13px; color: #555; margin-bottom: 12px;">上傳 IG 限動、手寫標籤或折扣截圖，自動提取關鍵數字與代碼</p>
  <input type="file" id="ocr_file" accept="image/*" style="border: none; background: transparent; margin-bottom: 10px;">
  <button type="button" id="ocr_btn" onclick="runOCR()" style="background: #27ae60; margin-top: 5px;">🚀 開始智慧分析圖片</button>
  <div id="ocr_result" style="margin-top:10px; font-size:13px; color:#2c3e50; font-weight:bold; text-align:left; background:white; padding:10px; border-radius:6px; display:none;"></div>
</div>

{% if success %}
<div class="success">✅ {{ success }}</div>
{% endif %}

<form method="POST" action="/admin/add" id="product_form">
  <h3>手動或 AI 自動填入表單：</h3><br>
  <div class="form-group">
    <label>商品名稱 / 識別出的折價碼</label>
    <input name="name" id="p_name" placeholder="例如：iPhone 15 128G 或輸入折價碼 SAVE15" required>
  </div>
  <div class="form-group">
    <label>市場均價 (NT$)</label>
    <input name="market_price" id="p_market" type="number" placeholder="例如：25000" required>
  </div>
  <div class="form-group">
    <label>特賣價格 / 手寫識別價格 (NT$)</label>
    <input name="sale_price" id="p_sale" type="number" placeholder="例如：1990" required>
  </div>
  <div class="form-group">
    <label>商品描述來源</label>
    <input name="description" id="p_desc" placeholder="例如：由 AI 識圖自動帶入或手動輸入描述">
  </div>
  <div class="form-group">
    <label>商品連結 / 平台出處</label>3
    <input name="affiliate_link" placeholder="貼上蝦皮、露天或 IG 貼文網址">
  </div>
  <button type="submit">➕ 確認上架並進行 15% 警示校對</button>
</form>

<script>
async function runOCR() {
    const fileInput = document.getElementById('ocr_file');
    const btn = document.getElementById('ocr_btn');
    const resultDiv = document.getElementById('ocr_result');
    if(fileInput.files.length === 0) { alert('請先選取截圖檔案！'); return; }

    btn.innerText = 'AI 分析中...';
    btn.disabled = true;
    resultDiv.style.display = 'none';

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const res = await fetch('/ocr', { method: 'POST', body: formData });
        const data = await res.json();
        
        resultDiv.style.display = 'block';
        let report = `【AI 識別報告】<br>🔹 找到的所有可能價格：${data.prices.join(', ') || '未偵測到'}<br>🔹 找到的可能折扣碼：${data.promos.join(', ') || '未偵測到'}`;
        resultDiv.innerHTML = report;

        // 智慧帶入表單欄位
        if(data.prices.length > 0) {
            document.getElementById('p_sale').value = data.prices[0];
        }
        if(data.promos.length > 0) {
            document.getElementById('p_name').value = "偵測到優待碼：" + data.promos[0];
        } else {
            document.getElementById('p_name').value = "AI 識圖自動生成商品";
        }
       document.getElementById('p_desc').value = "擷取前30字內容：" + data.text.replace(/\\s+/g, ' ').substring(0, 30);
        
        alert('AI 辨識完成！已自動為你填寫表單內容，請手動補齊「市場均價」進行對比。');
    } catch(e) {
        alert('本地辨識發生異常，請確認伺服器底層是否安裝 Tesseract 引擎。');
    } finally {
        btn.innerText = '🚀 開始智慧分析圖片';
        btn.disabled = false;
    }
}
</script>

<div style="margin-top:30px">
  <h2>目前架上監控商品（{{ products|length }} 件）</h2>
  {% for p in products %}
  <div class="item">
    <span><strong>{{ p.name }}</strong> — 特價 NT$ {{ p.sale_price }} ({{ p.discount }}% Off)</span>
    <form method="POST" action="/admin/delete/{{ loop.index0 }}">
      <button class="delete-btn">下架</button>
    </form>
  </div>
  {% endfor %}
</div>
</body>
</html>
"""

# --- 路由與後端處理邏輯 ---

@app.route("/")
def index():
    products = load_products()
    subscriber_count = len(load_subscribers())
    return render_template_string(TEMPLATE, products=products, subscriber_count=subscriber_count, success=None)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"]
    subscribers = load_subscribers()
    if email not in subscribers:
        subscribers.append(email)
        save_subscribers(subscribers)
    products = load_products()
    subscriber_count = len(subscribers)
    return render_template_string(TEMPLATE, products=products, subscriber_count=subscriber_count, success=f"【{email}】成功開啟省錢獵人 24H 破盤秒發監控通知！")

@app.route("/admin")
def admin():
    products = load_products()
    subscriber_count = len(load_subscribers())
    return render_template_string(ADMIN_TEMPLATE, products=products, subscriber_count=subscriber_count, success=None)

@app.route("/admin/add", methods=["POST"])
def add_product():
    products = load_products()
    market = int(request.form["market_price"])
    sale = int(request.form["sale_price"])
    discount = int((1 - sale/market) * 100)
    
    product = {
        "name": request.form["name"],
        "market_price": market,
        "sale_price": sale,
        "discount": discount,
        "description": request.form["description"],
        "affiliate_link": request.form["affiliate_link"] or "#"
    }
    products.append(product)
    save_products(products)
    
    # 調用警示校對函式
    send_email_to_all(product)
    
    subscriber_count = len(load_subscribers())
    return render_template_string(ADMIN_TEMPLATE, products=products, subscriber_count=subscriber_count, success=f"商品處理完成！若符合 15% 降幅，省錢獵人系統已同步在背景啟動秒發通知機制。")

@app.route("/admin/delete/<int:idx>", methods=["POST"])
def delete_product(idx):
    products = load_products()
    if 0 <= idx < len(products):
        products.pop(idx)
        save_products(products)
    return redirect("/admin")

# --- AI 精準識圖 OCR 路由 ---
@app.route("/ocr", methods=["POST"])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "沒有圖片"}), 400
    file = request.files['image']
    img = Image.open(io.BytesIO(file.read()))
    
    text = pytesseract.image_to_string(img, lang='chi_tra+eng')
    
    # 2a. 抓取手寫或網頁上的價格（支援 $、NT$、或是 3-6 位數的純數字）
    prices = re.findall(r'(?:NT\$?|\$)?\s*(\d{3,6})', text)
    prices = [p for p in prices if int(p) != 2026]
    
    # 2b. 抓取大寫隱藏折價碼（如貼文中的 SAVE15, OFF30, DISCOUNT10）
    promos = re.findall(r'([A-Z]{3,10}\d{2,3})', text)
    
    return jsonify({"text": text, "prices": prices, "promos": promos})

# --- 模擬 24 小時跨平台巡邏 API 接口 ---
@app.route("/api/patrol_webhook", methods=["POST"])
def patrol_webhook():
    data = request.json
    if not data or 'name' not in data or 'market_price' not in data or 'sale_price' not in data:
        return jsonify({"error": "無效的巡邏資料"}), 400
        
    market = int(data["market_price"])
    sale = int(data["sale_price"])
    discount = int((1 - sale/market) * 100)
    
    product = {
        "name": f"【巡邏偵測】{data['name']}",
        "market_price": market,
        "sale_price": sale,
        "discount": discount,
        "description": data.get("description", "來自跨平台巡邏自動採集數據"),
        "affiliate_link": data.get("affiliate_link", "#")
    }
    
    products = load_products()
    products.append(product)
    save_products(products)
    
    send_email_to_all(product)
    
    return jsonify({"status": "巡邏完成", "discount": discount, "alert_triggered": discount >= 15})

import os

if __name__ == '__main__':
    # 讀取 Render 分配的 PORT
    port = int(os.environ.get("PORT", 5000))
    
    # 判斷模式：只有明確設定為 CRAWLER 環境變數才跑爬蟲
    # 這樣可以確保預設情況下，Render 會跑進 else 啟動網頁服務
    if os.environ.get("RUN_TYPE") == "CRAWLER":
        print("偵測到 CRAWLER 模式，執行自動化任務...")
        run_scraping_job()
    else:
        print(f"啟動網頁服務，監聽 Port: {port}")
        app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template_string, request, redirect
import json, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
DATA_FILE = "products.json"
SUBSCRIBERS_FILE = "subscribers.json"

GMAIL = "g9607111@gmail.com"
GMAIL_PASSWORD = "ylpzydzc uzqdkrez"

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subscribers, f, ensure_ascii=False, indent=2)

def send_email_to_all(product):
    subscribers = load_subscribers()
    if not subscribers:
        return
    
    for email in subscribers:
        try:
            msg = MIMEMultipart()
            msg["From"] = GMAIL
            msg["To"] = email
            msg["Subject"] = f"🔥 破盤雷達｜發現低價好貨：{product['name']}"
            
            body = f"""
嗨！破盤雷達發現新的低價商品！

商品名稱：{product['name']}
市場均價：NT$ {product['market_price']}
特賣價格：NT$ {product['sale_price']}
低於市價：{product['discount']}%
商品描述：{product['description']}

👉 搶購連結：{product['affiliate_link']}

---
此信件由破盤雷達自動發送
            """
            
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(GMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL, email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"寄信失敗 {email}: {e}")

TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>破盤雷達</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f0f2f5; }
  .header { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 20px; text-align: center; }
  .header h1 { font-size: 28px; }
  .header p { opacity: 0.9; margin-top: 5px; }
  .container { max-width: 900px; margin: 20px auto; padding: 0 15px; }
  .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .stats { display: flex; gap: 15px; margin-bottom: 20px; }
  .stat { flex: 1; background: white; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .stat h2 { color: #e74c3c; font-size: 28px; }
  .stat p { color: #666; font-size: 14px; }
  .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; }
  .product-card { background: white; border-radius: 12px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 4px solid #e74c3c; }
  .product-card h3 { font-size: 15px; margin-bottom: 10px; color: #333; }
  .original-price { color: #999; text-decoration: line-through; font-size: 14px; }
  .sale-price { color: #e74c3c; font-size: 22px; font-weight: bold; }
  .badge { display: inline-block; background: #e74c3c; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; margin: 8px 0; }
  .btn { display: block; text-align: center; background: #e74c3c; color: white; padding: 10px; border-radius: 8px; text-decoration: none; margin-top: 10px; font-weight: bold; }
  .btn:hover { background: #c0392b; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; font-weight: bold; color: #444; }
  input[type=email] { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
  .submit-btn { background: #e74c3c; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; }
  .plans { display: flex; gap: 15px; }
  .plan { flex: 1; border: 2px solid #ddd; border-radius: 12px; padding: 20px; text-align: center; }
  .plan.hot { border-color: #e74c3c; }
  .plan h3 { color: #e74c3c; margin-bottom: 10px; }
  .plan-price { font-size: 26px; font-weight: bold; color: #333; margin: 10px 0; }
  .plan ul { list-style: none; text-align: left; margin: 10px 0; }
  .plan ul li { padding: 5px 0; color: #555; }
  .admin-link { text-align: right; margin-bottom: 10px; }
  .admin-link a { color: #999; font-size: 13px; }
  .success { background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
</style>
</head>
<body>
<div class="header">
  <h1>🔥 破盤雷達</h1>
  <p>Z世代必備｜即時偵測破盤好貨，搶先特定買家一步</p>
</div>

<div class="container">
  {% if success %}
  <div class="success">✅ {{ success }}</div>
  {% endif %}

  <div class="stats">
    <div class="stat">
      <h2>{{ products|length }}</h2>
      <p>目前監控商品</p>
    </div>
    <div class="stat">
      <h2>{{ subscriber_count }}</h2>
      <p>📧 訂閱人數</p>
    </div>
    <div class="stat">
      <h2>即時</h2>
      <p>狩獵版通知速度</p>
    </div>
  </div>

  {% if products %}
  <h2 style="margin-bottom:15px">📦 目前特價商品</h2>
  <div class="product-grid">
    {% for p in products %}
    <div class="product-card">
      <h3>{{ p.name }}</h3>
      <div class="original-price">市場均價 NT$ {{ p.market_price }}</div>
      <div class="sale-price">NT$ {{ p.sale_price }}</div>
      <span class="badge">🔥 低於市價 {{ p.discount }}%</span>
      <p style="font-size:13px;color:#666;margin:8px 0">{{ p.description }}</p>
      <a href="{{ p.affiliate_link }}" class="btn" target="_blank">👉 搶購去</a>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="card" style="text-align:center;color:#999;padding:40px">
    <p style="font-size:40px">🔍</p>
    <p>目前還沒有特價商品，請稍後再來！</p>
  </div>
  {% endif %}

  <br>
  <div class="card">
    <h2 style="margin-bottom:15px">🔔 免費訂閱通知</h2>
    <p style="color:#666;margin-bottom:15px">有破盤商品時，自動寄 Email 通知你！</p>
    <form method="POST" action="/subscribe">
      <div class="form-group">
        <label>你的 Email</label>
        <input type="email" name="email" placeholder="輸入 Email" required>
      </div>
      <button class="submit-btn">免費訂閱通知 🔔</button>
    </form>
  </div>

  <h2 style="margin-bottom:15px">💎 訂閱方案</h2>
  <div class="plans">
    <div class="plan">
      <h3>基礎版</h3>
      <div class="plan-price">免費</div>
      <ul>
        <li>✅ 延遲 10 分鐘通知</li>
        <li>✅ 1 個監控關鍵字</li>
        <li>❌ IG 限動偵測</li>
      </ul>
    </div>
    <div class="plan hot">
      <h3>🏆 狩獵版</h3>
      <div class="plan-price">NT$ 49 / 月</div>
      <ul>
        <li>✅ 即時通知</li>
        <li>✅ 解鎖 IG 限動偵測</li>
        <li>✅ 無限關鍵字</li>
      </ul>
    </div>
  </div>

  <div class="admin-link"><a href="/admin">管理後台</a></div>
</div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>管理後台</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 0 15px; }
  h1 { color: #e74c3c; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; font-weight: bold; }
  input { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
  button { background: #e74c3c; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; }
  .back { display: inline-block; margin-bottom: 20px; color: #e74c3c; text-decoration: none; }
  .item { background: #f9f9f9; padding: 10px 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
  .delete-btn { background: #999; color: white; border: none; padding: 5px 12px; border-radius: 5px; cursor: pointer; width: auto; margin: 0; }
  .success { background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
</style>
</head>
<body>
<a class="back" href="/">← 回首頁</a>
<h1>🛠 管理後台</h1>
<p style="color:#666;margin-bottom:5px">訂閱人數：<strong>{{ subscriber_count }} 人</strong></p>
<p style="color:#666;margin-bottom:20px">新增商品後會自動寄 Email 通知所有訂閱者！</p>

{% if success %}
<div class="success">✅ {{ success }}</div>
{% endif %}

<form method="POST" action="/admin/add">
  <div class="form-group">
    <label>商品名稱</label>
    <input name="name" placeholder="例如：iPhone 15 128G 黑色" required>
  </div>
  <div class="form-group">
    <label>市場均價 (NT$)</label>
    <input name="market_price" type="number" placeholder="例如：28000" required>
  </div>
  <div class="form-group">
    <label>特賣價格 (NT$)</label>
    <input name="sale_price" type="number" placeholder="例如：22000" required>
  </div>
  <div class="form-group">
    <label>商品描述</label>
    <input name="description" placeholder="例如：九成新，附原廠配件">
  </div>
  <div class="form-group">
    <label>商品連結（蝦皮/露天/任何平台）</label>
    <input name="affiliate_link" placeholder="貼上商品連結">
  </div>
  <button type="submit">➕ 新增商品並通知訂閱者</button>
</form>

<div style="margin-top:30px">
  <h2>目前商品（{{ products|length }} 件）</h2>
  {% for p in products %}
  <div class="item">
    <span>{{ p.name }} — NT$ {{ p.sale_price }}</span>
    <form method="POST" action="/admin/delete/{{ loop.index0 }}">
      <button class="delete-btn">刪除</button>
    </form>
  </div>
  {% endfor %}
</div>
</body>
</html>
"""

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
    return render_template_string(TEMPLATE, products=products, subscriber_count=subscriber_count, success=f"{email} 訂閱成功！有破盤好貨會立刻通知你")

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
    send_email_to_all(product)
    subscriber_count = len(load_subscribers())
    return render_template_string(ADMIN_TEMPLATE, products=products, subscriber_count=subscriber_count, success=f"商品新增成功！已通知 {subscriber_count} 位訂閱者")

@app.route("/admin/delete/<int:idx>", methods=["POST"])
def delete_product(idx):
    products = load_products()
    products.pop(idx)
    save_products(products)
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
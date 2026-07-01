from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import math
import random
from datetime import datetime, timedelta

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="food_app"
)
cursor = db.cursor()

 # Haversine formula to calculate distance between two lat/lng points

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c

    return round(distance,2)

# ---------------- HELPER FUNCTION ----------------
def get_cart_count(user_id):
    cursor.execute("SELECT IFNULL(SUM(quantity),0) FROM cart WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

@app.route("/spicehub")
def spicehub():
    return render_template("spicehub.html")


# Pizza Palace
@app.route("/pizza")
def pizza():
    return render_template("pizza.html")


# Burger Town
@app.route("/burger")
def burger():
    return render_template("burger.html")


# South Delight
@app.route("/southdelight")
def southdelight():
    return render_template("southdelight.html")


# Chinese Corner
@app.route("/chinese")
def chinese():
    return render_template("chinese.html")


# Punjabi Dhaba
@app.route("/punjabidhaba")
def punjabidhaba():
    return render_template("punjabidhaba.html")

# ================= HOME =================
@app.route('/')
def home():
    cart_count = 0
    if 'user_id' in session:
        cart_count = get_cart_count(session['user_id'])
    return render_template("home.html", cart_count=cart_count)


# ================= SIGNUP =================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = generate_password_hash(request.form['password'])

        cursor.execute("SELECT * FROM Userdetails WHERE name=%s", (name,))
        if cursor.fetchone():
            return render_template("register.html", error="User already exists")

        cursor.execute("""
            INSERT INTO Userdetails (name, Email, Mobile, Password)
            VALUES (%s,%s,%s,%s)
        """, (name, email, mobile, password))
        db.commit()

        return redirect(url_for('login'))

    return render_template("register.html")


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        cursor.execute("SELECT * FROM Userdetails WHERE name=%s", (name,))
        user = cursor.fetchone()

        if user and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('restaurants'))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# DELIVERY PARTNER LOGOUT

# ================= PARTNER LOGOUT =================

@app.route('/partner_logout')
def partner_logout():

    session.pop('partner_id', None)

    session.pop('partner_name', None)

    return redirect(
        url_for('home')
    )

# ================= RESTAURANTS =================
@app.route('/restaurants')
def restaurants():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_count = get_cart_count(session['user_id'])
    return render_template("home.html", cart_count=cart_count)


# ================= INDIVIDUAL RESTAURANT =================
@app.route('/restaurants/<restaurant_name>')
def restaurant_page(restaurant_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_count = get_cart_count(session['user_id'])

    template_map = {
        "pizza-palace": "pizza.html",
        "south-delight": "South.html",
        "spice-hub": "Spice.html",
        "burger-town": "Burger.html",
        "punjabi-dhaba": "Panjabi.html",
        "chinese-corner": "Chinese.html",
        "Tandoori": "Tandoori.html"
    }

    template = template_map.get(restaurant_name)

    if not template:
        return "Restaurant not found", 404

    return render_template(template, cart_count=cart_count)


# ================= ADD TO CART =================
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    item_name = request.form['item_name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    cursor.execute("""
        SELECT cart_id, quantity FROM cart
        WHERE user_id=%s AND item_name=%s
    """, (user_id, item_name))

    existing = cursor.fetchone()

    if existing:

        new_quantity = existing[1] + quantity
        new_subtotal = new_quantity * price

        cursor.execute("""
            UPDATE cart
            SET quantity=%s, subtotal=%s
            WHERE cart_id=%s
        """, (new_quantity, new_subtotal, existing[0]))

    else:

        subtotal = price * quantity

        cursor.execute("""
            INSERT INTO cart (user_id, item_name, price, quantity, subtotal)
            VALUES (%s,%s,%s,%s,%s)
        """, (user_id, item_name, price, quantity, subtotal))

    db.commit()

    return redirect(request.referrer)


@app.route('/update_cart', methods=['POST'])
def update_cart():

    cart_id = request.form['cart_id']
    action = request.form['action']

    cursor.execute(
        "SELECT quantity, price FROM cart WHERE cart_id=%s",
        (cart_id,)
    )

    item = cursor.fetchone()

    quantity = item[0]
    price = item[1]

    if action == "increase":
        quantity += 1

    elif action == "decrease":
        quantity -= 1

        if quantity <= 0:
            cursor.execute(
                "DELETE FROM cart WHERE cart_id=%s",
                (cart_id,)
            )
            db.commit()
            return redirect(url_for('order'))

    subtotal = quantity * price

    cursor.execute("""
        UPDATE cart
        SET quantity=%s,
            subtotal=%s
        WHERE cart_id=%s
    """, (quantity, subtotal, cart_id))

    db.commit()

    return redirect(url_for('order'))


# ================= VIEW CART =================
@app.route('/order')
def order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    cursor.execute("SELECT * FROM cart WHERE user_id=%s", (user_id,))
    cart_items = cursor.fetchall()

    total = sum(item[5] for item in cart_items)
    cart_count = get_cart_count(user_id)

    return render_template("order.html",
                           cart_items=cart_items,
                           total=total,
                           cart_count=cart_count)


# ================= CHECKOUT =================
@app.route('/checkout')
def checkout():

    otp = random.randint(1000,9999)

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get cart items
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s",
        (user_id,)
    )

    cart_items = cursor.fetchall()

    if not cart_items:
        return redirect(url_for('order'))

    # Calculate total
    total = sum(item[5] for item in cart_items)

    # Create Order
    cursor.execute("""
        INSERT INTO orders
        (user_id, total_amount, order_status, delivery_otp)

        VALUES (%s, %s, %s, %s)
    """, (
        user_id,
        total,
        "Pending",
        otp
    ))

    db.commit()

    order_id = cursor.lastrowid

    # Insert Order Items
    for item in cart_items:

        cursor.execute("""
            INSERT INTO order_items
            (order_id, item_name, price, quantity, subtotal)

            VALUES (%s, %s, %s, %s, %s)
        """, (
            order_id,
            item[2],
            item[3],
            item[4],
            item[5]
        ))

    db.commit()

    # Clear Cart

    cursor.execute(
        "DELETE FROM cart WHERE user_id=%s",
        (user_id,)
    )

    db.commit()

    return redirect(
        url_for('payment')
    )
# ================= MY ORDERS =================
@app.route('/my_orders')
def my_orders():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get ALL orders of this user
    cursor.execute("""

    SELECT orders.order_id,
           orders.total_amount,
           orders.order_status,
           orders.created_at,
           delivery_partners.name,
           orders.partner_id,
           orders.delivery_otp

    FROM orders

    LEFT JOIN delivery_partners
    ON orders.partner_id = delivery_partners.partner_id

    WHERE orders.user_id=%s

    ORDER BY orders.created_at DESC

    """, (user_id,))

    orders = cursor.fetchall()

    all_orders = []

    for order in orders:

        order_id = order[0]

        cursor.execute("""
            SELECT item_name,
                   price,
                   quantity,
                   subtotal

            FROM order_items

            WHERE order_id=%s
        """, (order_id,))

        items = cursor.fetchall()

        all_orders.append({

            "order_id": order[0],
            "total": order[1],
            "status": order[2],
            "date": order[3],
            "partner": order[4],
            "partner_id": order[5],
            "otp": order[6],
            "items": items

        })

    return render_template(
        "my_orders.html",
        all_orders=all_orders
    )
# ================= ADMIN LOGIN & DASHBOARD =================

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s",(username,password))
        admin = cursor.fetchone()

        if admin:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid Admin Login"

    return render_template("admin_login.html")

@app.route('/admin_dashboard')
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # FILTER

    status = request.args.get('status')

    query = """

    SELECT
    orders.order_id,
    Userdetails.name,
    orders.total_amount,
    orders.order_status

    FROM orders

    JOIN Userdetails
    ON orders.user_id = Userdetails.Id

    """

    values = []

    if status:

        query += """
        WHERE orders.order_status=%s
        """

        values.append(status)

    query += """
    ORDER BY orders.order_id DESC
    """

    cursor.execute(query, values)

    orders = cursor.fetchall()

    # DELIVERY PARTNERS

    cursor.execute("""
    SELECT partner_id, name
    FROM delivery_partners
    """)

    partners = cursor.fetchall()

    # TOTAL ORDERS

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    """)

    total_orders = cursor.fetchone()[0]

    # PENDING ORDERS

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE order_status='Pending'
    """)

    pending_orders = cursor.fetchone()[0]

    # ACTIVE ORDERS

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE order_status='Active'
    """)

    active_orders = cursor.fetchone()[0]

    # DELIVERED ORDERS

    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE order_status='Delivered'
    """)

    delivered_orders = cursor.fetchone()[0]

    # TOTAL SUBSCRIPTIONS

    cursor.execute("""
    SELECT COUNT(*)
    FROM subscriptions
    """)

    total_subscriptions = cursor.fetchone()[0]

    # WEEKLY SUBSCRIPTIONS

    cursor.execute("""
    SELECT COUNT(*)
    FROM subscriptions
    WHERE plan_type='Weekly'
    """)

    weekly_subscriptions = cursor.fetchone()[0]

    # MONTHLY SUBSCRIPTIONS

    cursor.execute("""
    SELECT COUNT(*)
    FROM subscriptions
    WHERE plan_type='Monthly'
    """)

    monthly_subscriptions = cursor.fetchone()[0]

    return render_template(

        'admin_dashboard.html',

        orders=orders,
        partners=partners,

        total_orders=total_orders,
        pending_orders=pending_orders,
        active_orders=active_orders,
        delivered_orders=delivered_orders,

        total_subscriptions=total_subscriptions,
        weekly_subscriptions=weekly_subscriptions,
        monthly_subscriptions=monthly_subscriptions
    )

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):

    status = request.form['status']

    cursor.execute("""
        UPDATE orders
        SET order_status=%s
        WHERE order_id=%s
    """,(status,order_id))

    db.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/accept_order/<int:order_id>')
def accept_order(order_id):

    cursor.execute("""
        UPDATE orders
        SET order_status='Accepted'
        WHERE order_id=%s
    """,(order_id,))

    db.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_logout')
def admin_logout():

    session.pop('admin',None)

    return redirect(url_for('home'))
# ================= ASSIGN PARTNER =================admin_login
@app.route('/assign_partner/<int:order_id>', methods=['POST'])
def assign_partner(order_id):

    partner_id = request.form['partner_id']

    cursor.execute("""
    SELECT order_status FROM orders
    WHERE order_id=%s
    """,(order_id,))

    status = cursor.fetchone()

    if status and status[0] != "Cancelled":

        cursor.execute("""
        UPDATE orders
        SET partner_id=%s, order_status='Active'
        WHERE order_id=%s
        """,(partner_id,order_id))

        db.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/partner_login', methods=['GET','POST'])
def partner_login():

    if request.method == 'POST':

        phone = request.form['phone']

        cursor.execute("SELECT * FROM delivery_partners WHERE phone=%s",(phone,))
        partner = cursor.fetchone()

        if partner:
            session['partner_id'] = partner[0]
            session['partner_name'] = partner[1]
            return redirect(url_for('partner_dashboard'))

    return render_template("partner_login.html")

@app.route('/partner_dashboard')
def partner_dashboard():

    if 'partner_id' not in session:
        return redirect(url_for('partner_login'))

    partner_id = session['partner_id']

    cursor.execute("""
SELECT 
orders.order_id,
orders.user_id,
orders.total_amount,
orders.order_status,
address.full_name,
address.mobile,
address.address,
address.city,
address.pincode,
address.landmark

FROM orders

JOIN address
ON orders.user_id = address.user_id

WHERE orders.partner_id=%s

ORDER BY orders.order_id DESC
""", (partner_id,))

    orders = cursor.fetchall()

    return render_template("partner_dashboard.html",orders=orders)

@app.route('/mark_delivered/<int:order_id>')
def mark_delivered(order_id):

    cursor.execute("""
    UPDATE orders
    SET order_status='Delivered'
    WHERE order_id=%s
    """,(order_id,))

    db.commit()

    return redirect(url_for('partner_dashboard'))
# ================= UPDATE PARTNER LOCATION =================

@app.route('/update_location', methods=['POST'])
def update_location():

    if 'partner_id' not in session:
        return "Unauthorized"

    lat = request.form['lat']
    lng = request.form['lng']

    cursor.execute("""
    UPDATE delivery_partners
    SET latitude=%s, longitude=%s
    WHERE partner_id=%s
    """, (lat, lng, session['partner_id']))

    db.commit()

    return "Location Updated"

@app.route('/get_partner_location')
def get_partner_location():

    cursor.execute("""
    SELECT latitude,longitude
    FROM delivery_partners
    WHERE partner_id=1
    """)

    loc = cursor.fetchone()

    return {
        "latitude":loc[0],
        "longitude":loc[1]
    }
# ================= CANCEL ORDER =================
@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check if partner assigned
    cursor.execute("""
    SELECT partner_id FROM orders
    WHERE order_id=%s AND user_id=%s
    """,(order_id, session['user_id']))

    order = cursor.fetchone()

    if order and order[0] is None:

        cursor.execute("""
        UPDATE orders
        SET order_status='Cancelled'
        WHERE order_id=%s
        """,(order_id,))

        db.commit()

    return redirect(url_for('my_orders'))
# ================= TRACK ORDER =================

@app.route('/track_order/<int:order_id>')
def track_order(order_id):
    return render_template("track_order.html",order_id=order_id)

@app.route('/distance/<int:order_id>')
def distance(order_id):

    cursor.execute("""
    SELECT Userdetails.latitude, Userdetails.longitude,
           delivery_partners.latitude, delivery_partners.longitude
    FROM orders
    JOIN Userdetails ON orders.user_id = Userdetails.Id
    JOIN delivery_partners ON orders.partner_id = delivery_partners.partner_id
    WHERE orders.order_id=%s
    """, (order_id,))

    data = cursor.fetchone()

    if data is None:
        return "Location not available yet"

    user_lat, user_lng, partner_lat, partner_lng = data

    dist = calculate_distance(user_lat, user_lng, partner_lat, partner_lng)

    return f"Distance: {dist} KM"
# ================= ADDRESS MANAGEMENT =================
@app.route('/address', methods=['GET', 'POST'])
def address():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        full_name = request.form['full_name']
        mobile = request.form['mobile']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']
        landmark = request.form['landmark']

        cursor.execute("""
        INSERT INTO address
        (user_id, full_name, mobile, address, city, pincode, landmark)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            full_name,
            mobile,
            address,
            city,
            pincode,
            landmark
        ))
        db.commit()

        return redirect(url_for('checkout'))
    
    return render_template('address.html')

# ================= PAYMENT PAGE =================
@app.route('/payment')
def payment():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT order_id, total_amount
        FROM orders
        WHERE user_id=%s
        ORDER BY order_id DESC
        LIMIT 1
    """, (session['user_id'],))

    order = cursor.fetchone()

    if not order:
        return "No order found"

    return render_template(
        'payment.html',
        order_id=order[0],
        total=order[1]
    )

# ================= VERIFY DELIVERY =================

@app.route('/verify_delivery/<int:order_id>', methods=['POST'])
def verify_delivery(order_id):

    entered_otp = request.form['otp']

    cursor.execute("""
    SELECT delivery_otp
    FROM orders
    WHERE order_id=%s
    """, (order_id,))

    real_otp = cursor.fetchone()

    if real_otp and entered_otp == real_otp[0]:

        cursor.execute("""
        UPDATE orders
        SET order_status='Delivered'
        WHERE order_id=%s
        """, (order_id,))

        db.commit()

        return redirect(url_for('partner_dashboard'))

    return "Invalid OTP"
# ================= ORDER STATUS =================
@app.route('/order_status/<int:order_id>')
def order_status(order_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("""
    SELECT order_id,
           total_amount,
           order_status,
           partner_id,
           delivery_otp

    FROM orders
    WHERE order_id=%s
    """, (order_id,))

    order = cursor.fetchone()

    return render_template(
        "order_status.html",
        order=order
    )
# ================= SUBSCRIPTION =================
@app.route('/subscription', methods=['GET', 'POST'])
def subscription():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        restaurant = request.form.get('restaurant')

        food_name = request.form.get('food_name')

        price = request.form.get('price')

        plan_type = request.form.get('plan_type')

        delivery_time = request.form.get('delivery_time')

        address = request.form.get('address')

        start_date = datetime.now().date()

        if plan_type == "Weekly":

            end_date = start_date + timedelta(days=7)

        else:

            end_date = start_date + timedelta(days=30)

        cursor.execute("""

        INSERT INTO subscriptions
        (
            user_id,
            restaurant_name,
            food_name,
            price,
            plan_type,
            delivery_time,
            delivery_address,
            start_date,
            end_date,
            subscription_status
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """, (

            session['user_id'],
            restaurant,
            food_name,
            price,
            plan_type,
            delivery_time,
            address,
            start_date,
            end_date,
            "Active"

        ))

        db.commit()

        return redirect(url_for('my_subscriptions'))

    return render_template('subscription.html')
# ================= MY SUBSCRIPTIONS =================
@app.route('/my_subscriptions')
def my_subscriptions():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("""

    SELECT *
    FROM subscriptions

    WHERE user_id=%s

    ORDER BY subscription_id DESC

    """, (session['user_id'],))

    subscriptions = cursor.fetchall()

    return render_template(
        'my_subscriptions.html',
        subscriptions=subscriptions
    )
# ================= ADMIN SUBSCRIPTIONS =================
@app.route('/admin_subscriptions')
def admin_subscriptions():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # GET FILTER VALUE

    plan =request.args.get('plan')

    # BASE QUERY

    query = """

    SELECT

    subscriptions.subscription_id,

    Userdetails.name,

    subscriptions.restaurant_name,

    subscriptions.food_name,

    subscriptions.price,

    subscriptions.plan_type,

    subscriptions.delivery_time,

    subscriptions.start_date,

    subscriptions.end_date,

    subscriptions.subscription_status

    FROM subscriptions

    JOIN Userdetails

    ON subscriptions.user_id = Userdetails.Id

    """

    values = []

    # FILTER

    if plan:

        query += """

        WHERE subscriptions.plan_type=%s

        """

        values.append(plan)

    # ORDER

    query += """

    ORDER BY subscriptions.subscription_id DESC

    """

    cursor.execute(query, values)

    subscriptions = cursor.fetchall()

    return render_template(
        'admin_subscriptions.html',
        subscriptions=subscriptions
    )

# ================= AI RECOMMENDATION =================
@app.route('/ai_recommendation')
def ai_recommendation():

    # CURRENT TIME

    hour = datetime.now().hour

    recommendation = []

    # MORNING

    if hour < 11:

        recommendation = [
            "Upma",
            "Idli",
            "Dosa",
            "Poha",
            "Tea"

        ]

    # AFTERNOON

    elif hour < 17:

        recommendation = [

            "Veg Biryani",
            "Paneer Curry",
            "Thali",
            "Fried Rice"

        ]

    # NIGHT

    else:

        recommendation = [
            "Chicken Biryani",
            "Pizza",
            "Burger",
            "Pasta",
            "Noodles"

        ]

    return render_template(

        'ai_recommendation.html',

        recommendation=recommendation
    )

# ================= CHATBOT =================
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():

    reply = ""

    if request.method == 'POST':

        message = request.form['message'].lower()

        # LOGIN CHECK

        if 'user_id' not in session:

            reply = "⚠ Please login first."

            return render_template(
                'chatbot.html',
                reply=reply
            )

        user_id = session['user_id']

        # =========================================
        # WHERE IS MY ORDER
        # =========================================

        if "where is my order" in message \
        or "track order" in message \
        or "my order" in message:

            cursor.execute("""

            SELECT order_id,
                   order_status

            FROM orders

            WHERE user_id=%s

            ORDER BY order_id DESC

            LIMIT 1

            """, (user_id,))

            order = cursor.fetchone()

            if order:

                reply = f"""

📦 Latest Order

Order ID: #{order[0]}

Current Status:
{order[1]}

"""

            else:

                reply = "❌ No order found."

        # =========================================
        # CANCEL ORDER
        # =========================================

        elif "cancel order" in message:

            cursor.execute("""

            SELECT order_id,
                   order_status

            FROM orders

            WHERE user_id=%s

            ORDER BY order_id DESC

            LIMIT 1

            """, (user_id,))

            order = cursor.fetchone()

            if order:

                if order[1] == "Pending":

                    cursor.execute("""

                    UPDATE orders

                    SET order_status='Cancelled'

                    WHERE order_id=%s

                    """, (order[0],))

                    db.commit()

                    reply = f"""

❌ Order Cancelled Successfully

Order ID:
#{order[0]}

"""

                else:

                    reply = """

⚠ Order cannot be cancelled.

Delivery already started.

"""

            else:

                reply = "❌ No order found."

    # PAYMENT ISSUE

        elif "payment" in message \
        or "refund" in message:

            reply = """

💳 Payment Support

• Refund within 3-5 days
• Check UPI/Card details
• Contact support for failed payment

"""
        # DELIVERY TIME
        elif "delivery time" in message \
        or "when will my order arrive" in message:

            reply = """

🚴 Estimated Delivery Time:

20 - 35 Minutes

"""
        # SUBSCRIPTION

        elif "subscription" in message:

            cursor.execute("""

            SELECT food_name,
                   plan_type,
                   delivery_time

            FROM subscriptions

            WHERE user_id=%s

            ORDER BY subscription_id DESC

            LIMIT 1

            """, (user_id,))

            sub = cursor.fetchone()

            if sub:

                reply = f"""

🍴 Your Subscription

Food:
{sub[0]}

Plan:
{sub[1]}

Delivery Time:
{sub[2]}

"""

            else:

                reply = """

❌ No active subscription found.

"""
# =============== Delivery Partner ===========================

        elif "delivery partner" in message:

            cursor.execute("""

            SELECT delivery_partners.name

            FROM orders

            JOIN delivery_partners

            ON orders.partner_id =
            delivery_partners.partner_id

            WHERE orders.user_id=%s

            ORDER BY orders.order_id DESC

            LIMIT 1

            """, (user_id,))

            partner = cursor.fetchone()

            if partner:

                reply = f"""

🚴 Delivery Partner

{partner[0]}

"""

            else:

                reply = """

⚠ Delivery partner not assigned yet.

"""
        elif "otp" in message:

            cursor.execute("""

            SELECT delivery_otp

            FROM orders

            WHERE user_id=%s

            ORDER BY order_id DESC

            LIMIT 1

            """, (user_id,))

            otp = cursor.fetchone()

            if otp:

                reply = f"""

🔐 Your Delivery OTP

{otp[0]}

Share with delivery partner only.

"""
            else:

                reply = "❌ OTP not found."

        elif "pizza" in message:

            reply = """

🍕 Recommended:

• Margherita Pizza
• Cheese Pizza
• Farmhouse Pizza

"""

        elif "burger" in message:

            reply = """

🍔 Recommended:

• Veg Burger
• Cheese Burger
• Double Patty Burger

"""

        elif "healthy" in message:

            reply = """

🥗 Healthy Food:

• Salad
• Soup
• Veg Thali

"""

        elif "spicy" in message:

            reply = """

🌶 Spicy Food:

• Paneer Tikka
• Biryani
• Manchurian

"""
        else:

            reply = """

🤖 I can help you with:
• Where is my order
• Cancel order
• Delivery time
• Payment issue
• Subscription
• Delivery partner
• OTP
• Pizza
• Burger
• Healthy food
• Spicy food
• South Indian food
"""

    return render_template(
        'chatbot.html',
        reply=reply
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os
import traceback

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_12345'

# بيانات المسؤول
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

# إعادة إنشاء قاعدة البيانات من الصفر
def init_db():
    try:
        # حذف قاعدة البيانات القديمة إذا كانت موجودة
        if os.path.exists('delivery_orders.db'):
            os.remove('delivery_orders.db')
            print("🗑️ تم حذف قاعدة البيانات القديمة")
        
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        
        # إنشاء الجدول مع جميع الحقول المطلوبة
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      whatsapp TEXT NOT NULL,
                      delivery_type TEXT NOT NULL,
                      start_date TEXT NOT NULL,
                      delivery_duration TEXT NOT NULL,
                      location TEXT NOT NULL,
                      current_location TEXT NOT NULL,
                      amount_paid REAL DEFAULT 0,
                      status TEXT DEFAULT 'pending',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        print("✅ تم إنشاء قاعدة البيانات بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {str(e)}")
        print(traceback.format_exc())

init_db()

# دالة للتحقق من تسجيل الدخول
def login_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('❌ يرجى تسجيل الدخول أولاً', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def order_form():
    return render_template('order_form.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    conn = None
    try:
        print("🔄 بدء استلام طلب جديد...")
        
        # التحقق من أن الطلب هو POST
        if request.method != 'POST':
            flash('❌ طريقة الإرسال غير صحيحة', 'error')
            return redirect(url_for('order_form'))
        
        # جمع البيانات من النموذج
        whatsapp = request.form.get('whatsapp', '').strip()
        delivery_type = request.form.get('delivery_type', '').strip()
        start_date = request.form.get('start_date', '').strip()
        delivery_duration = request.form.get('delivery_duration', '').strip()
        location = request.form.get('location', '').strip()
        current_location = request.form.get('current_location', '').strip()
        amount_paid = request.form.get('amount_paid', '0').strip()

        print(f"📊 البيانات المستلمة:")
        print(f"   📱 الواتساب: {whatsapp}")
        print(f"   🚚 نوع التوصيل: {delivery_type}")
        print(f"   📅 التاريخ: {start_date}")
        print(f"   ⏰ المدة: {delivery_duration}")
        print(f"   📍 الموقع الحالي: {current_location}")
        print(f"   🎯 موقع التوصيل: {location}")
        print(f"   💰 المبلغ: {amount_paid}")

        # التحقق من الحقول المطلوبة
        required_fields = {
            'whatsapp': whatsapp,
            'delivery_type': delivery_type,
            'start_date': start_date,
            'delivery_duration': delivery_duration,
            'location': location,
            'current_location': current_location
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            flash(f'❌ يرجى ملء جميع الحقول المطلوبة: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('order_form'))

        # استخدام رقم الواتساب كاسم افتراضي
        name = f"عميل {whatsapp}"
        
        # تحويل المبلغ إلى رقم
        try:
            amount_paid_float = float(amount_paid) if amount_paid else 0.0
        except ValueError:
            amount_paid_float = 0.0
            print("⚠️ تحذير: تم تعيين المبلغ إلى 0 بسبب خطأ في التحويل")

        # حفظ الطلب في قاعدة البيانات
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO orders 
                    (name, whatsapp, delivery_type, start_date, delivery_duration, location, current_location, amount_paid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (name, whatsapp, delivery_type, start_date, delivery_duration, location, current_location, amount_paid_float))
        
        conn.commit()
        order_id = c.lastrowid
        conn.close()
        conn = None
        
        print(f"✅ تم حفظ الطلب رقم {order_id} في قاعدة البيانات")
        
        # رسالة نجاح
        flash('✅ تم استلام طلبك بنجاح! سنتواصل معك عبر واتساب قريباً.', 'success')
        return redirect(url_for('order_form'))
        
    except Exception as e:
        print(f"❌ خطأ في إرسال الطلب: {str(e)}")
        print("🔍 تفاصيل الخطأ:")
        print(traceback.format_exc())
        
        # إغلاق الاتصال إذا كان مفتوحاً
        if conn:
            try:
                conn.close()
            except:
                pass
        
        flash('❌ حدث خطأ أثناء إرسال الطلب. يرجى المحاولة مرة أخرى.', 'error')
        return redirect(url_for('order_form'))

# صفحة تسجيل الدخول للإدارة
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('view_orders'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['logged_in'] = True
            session['username'] = username
            flash('✅ تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('view_orders'))
        else:
            flash('❌ اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('admin_login.html')

# تسجيل الخروج
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('✅ تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('admin_login'))

# عرض الطلبات (محمية)
@app.route('/admin/orders')
@login_required
def view_orders():
    try:
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        c.execute('SELECT * FROM orders ORDER BY created_at DESC')
        orders = c.fetchall()
        conn.close()
        
        print(f"📋 تم تحميل {len(orders)} طلب")
        return render_template('admin_orders.html', orders=orders)
        
    except Exception as e:
        print(f"❌ خطأ في عرض الطلبات: {str(e)}")
        flash('❌ حدث خطأ في تحميل الطلبات', 'error')
        return render_template('admin_orders.html', orders=[])

# تحديث حالة الطلب والمبلغ المدفوع (محمية)
@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@login_required
def update_order(order_id):
    try:
        new_status = request.form.get('status', 'pending')
        amount_paid = request.form.get('amount_paid', '0')
        
        try:
            amount_paid_float = float(amount_paid) if amount_paid else 0.0
        except ValueError:
            amount_paid_float = 0.0
        
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        c.execute('UPDATE orders SET status = ?, amount_paid = ? WHERE id = ?', 
                  (new_status, amount_paid_float, order_id))
        conn.commit()
        conn.close()
        
        flash('✅ تم تحديث بيانات الطلب بنجاح', 'success')
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الطلب: {str(e)}")
        flash('❌ حدث خطأ أثناء تحديث الطلب', 'error')
    
    return redirect(url_for('view_orders'))

# حذف طلب (محمية)
@app.route('/admin/order/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    try:
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
        
        flash('✅ تم حذف الطلب بنجاح', 'success')
            
    except Exception as e:
        print(f"❌ خطأ في حذف الطلب: {str(e)}")
        flash('❌ حدث خطأ أثناء حذف الطلب', 'error')
    
    return redirect(url_for('view_orders'))

# حذف جميع الطلبات المكتملة (محمية)
@app.route('/admin/orders/delete_completed', methods=['POST'])
@login_required
def delete_completed_orders():
    try:
        conn = sqlite3.connect('delivery_orders.db')
        c = conn.cursor()
        c.execute('DELETE FROM orders WHERE status = ?', ('completed',))
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        
        flash(f'✅ تم حذف {deleted_count} طلب مكتمل بنجاح', 'success')
        
    except Exception as e:
        print(f"❌ خطأ في حذف الطلبات المكتملة: {str(e)}")
        flash('❌ حدث خطأ أثناء حذف الطلبات المكتملة', 'error')
    
    return redirect(url_for('view_orders'))

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق تاكسي وصلني...")
    print("📍 الرابط: http://localhost:5000")
    print("📍 لوحة التحكم: http://localhost:5000/admin/login")
    app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

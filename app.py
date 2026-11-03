import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ---------------------------------------------------------
# 1. إعداد قاعدة البيانات وتأسيس الجداول
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect('faisal_school.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT,
                    name TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT UNIQUE
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    class_name TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    student_name TEXT,
                    class_name TEXT,
                    status TEXT,
                    date TEXT,
                    recorded_by TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    student_name TEXT,
                    class_name TEXT,
                    violation_type TEXT,
                    action TEXT,
                    date TEXT,
                    recorded_by TEXT
                )''')
    
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, name) VALUES ('admin', '121345', 'admin', 'مدير النظام')")
    
    default_classes = [f"خامس/{i}" for i in range(1, 5)] + \
                      [f"سادس/{i}" for i in range(1, 5)] + \
                      [f"سابع/{i}" for i in range(1, 5)]
    for cls in default_classes:
        c.execute("INSERT OR IGNORE INTO classes (class_name) VALUES (?)", (cls,))
        
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 2. الهوية البصرية الرسمية المتميزة (مدرسة السلطان فيصل بن تركي 5-7)
# ---------------------------------------------------------
st.set_page_config(page_title="مدرسة السلطان فيصل بن تركي (5-7)", layout="wide", page_icon="🇴🇲")

st.markdown("""
    <style>
    .stApp {
        background-color: #fcfbf7;
        color: #2c3e50;
    }
    .header-box {
        background: linear-gradient(135deg, #1b4d3e 0%, #0f2e24 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-subtitle {
        font-size: 1.1rem;
        color: #a3e6d5;
    }
    .login-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border-top: 5px solid #1b4d3e;
        border-right: 1px solid #eaeaea;
        border-left: 1px solid #eaeaea;
        border-bottom: 1px solid #eaeaea;
    }
    .stButton>button {
        background-color: #1b4d3e;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #14382d;
        color: white;
    }
    div[data-testid="stSidebar"] {
        background-color: #f4f8f6;
        border-left: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول الرسمية
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("""
        <div class='header-box'>
            <div class='header-title'>🏫 مدرسة السلطان فيصل بن تركي للتعليم الأساسي (5-7)</div>
            <div class='header-subtitle'>بوابة شؤون الطلاب، الحضور والمتابعة السلوكية • سلطنة عمان</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #1b4d3e; margin-bottom: 20px;'>🔐 تسجيل دخول الكادر التعليمي</h3>", unsafe_allow_html=True)
        
        username_input = st.text_input("اسم المستخدم")
        password_input = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول للنظام"):
            conn = sqlite3.connect('faisal_school.db')
            c = conn.cursor()
            c.execute("SELECT username, role, name FROM users WHERE username=? AND password=?", (username_input, password_input))
            user = c.fetchone()
            conn.close()
            
            if user:
                st.session_state.logged_in = True
                st.session_state.user = {"username": user[0], "role": user[1], "name": user[2]}
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. داخل النظام بعد تسجيل الدخول
# ---------------------------------------------------------
else:
    user = st.session_state.user
    st.sidebar.markdown(f"### 👨‍🏫 مرحباً، {user['name']}")
    st.sidebar.info(f"الصلاحية: {'مدير النظام' if user['role'] == 'admin' else 'معلم المادة'}")
    
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    menu_options = ["📋 رصد الغياب والحضور", "⚠️ تسجيل المخالفات السلوكية", "📚 إضافة صفوف وطلاب"]
    if user['role'] == 'admin':
        menu_options.extend(["👥 إدارة المعلمين", "📊 التقارير العامة"])

    choice = st.sidebar.radio("📌 القائمة الرئيسية", menu_options)

    conn = sqlite3.connect('faisal_school.db')

    if choice == "📚 إضافة صفوف وطلاب":
        st.header("📚 إدارة الصفوف والطلاب")
        tab1, tab2 = st.tabs(["إضافة صف/شعبة جديد", "إضافة طالب جديد"])
        
        with tab1:
            st.subheader("إضافة شعبة أو صف جديد")
            new_class = st.text_input("اسم الصف/الشعبة (مثال: سادس/5)")
            if st.button("حفظ الصف"):
                if new_class:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO classes (class_name) VALUES (?)", (new_class,))
                        conn.commit()
                        st.success(f"تمت إضافة الصف {new_class} بنجاح!")
                    except:
                        st.warning("هذا الصف موجود بالفعل.")
                else:
                    st.error("يرجى إدخال اسم الصف.")
                    
        with tab2:
            st.subheader("إضافة طالب إلى صف")
            df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
            selected_class = st.selectbox("اختر الصف", df_classes['class_name'] if not df_classes.empty else [])
            student_name = st.text_input("اسم الطالب الثلاثي/الرباعي")
            if st.button("إضافة الطالب"):
                if student_name and selected_class:
                    c = conn.cursor()
                    c.execute("INSERT INTO students (name, class_name) VALUES (?, ?)", (student_name, selected_class))
                    conn.commit()
                    st.success(f"تم إضافة الطالب {student_name} إلى الصف {selected_class}")
                else:
                    st.error("يرجى ملء جميع البيانات.")

    elif choice == "📋 رصد الغياب والحضور":
        st.header("📋 تسجيل ورصد الحضور والغياب اليومي")
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("اختر الصف لرصد الغياب", df_classes['class_name'] if not df_classes.empty else [])
        att_date = st.date_input("تاريخ اليوم", date.today())
        
        if selected_class:
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            if df_students.empty:
                st.info("لا يوجد طلاب في هذا الصف بعد.")
            else:
                st.subheader(f"طلاب صف {selected_class}")
                records = []
                for _, row in df_students.iterrows():
                    col1, col2 = st.columns([3, 2])
                    col1.write(row['name'])
                    status = col2.selectbox("الحالة", ["حاضر", "غائب", "متأخر", "غائب بعذر"], key=f"att_{row['id']}")
                    records.append((row['id'], row['name'], selected_class, status, str(att_date), user['name']))
                
                if st.button("حفظ سجل الغياب"):
                    c = conn.cursor()
                    for r in records:
                        c.execute("INSERT INTO attendance (student_id, student_name, class_name, status, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?)", r)
                    conn.commit()
                    st.success("تم حفظ الغياب بنجاح والمزامنة فورية!")

    elif choice == "⚠️ تسجيل المخالفات السلوكية":
        st.header("⚠️ تسجيل مخالفة سلوكية")
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("اختر الصف", df_classes['class_name'] if not df_classes.empty else [])
        
        if selected_class:
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            if not df_students.empty:
                student_tuple = st.selectbox("اختر الطالب", options=df_students.itertuples(), format_func=lambda x: x.name)
                v_type = st.selectbox("نوع المخالفة", ["عدم إحضار أدوات/كتب", "استخدام الهاتف", "التأخر عن الحصة", "إثارة الشغب", "الهروب من الحصة", "سلوك غير لائق"])
                v_action = st.text_input("الإجراء المتخذ (تنبيه شفوي/استدعاء ولي أمر...)")
                v_date = st.date_input("التاريخ", date.today())
                
                if st.button("تسجيل المخالفة"):
                    c = conn.cursor()
                    c.execute("INSERT INTO violations (student_id, student_name, class_name, violation_type, action, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (student_tuple.id, student_tuple.name, selected_class, v_type, v_action, str(v_date), user['name']))
                    conn.commit()
                    st.success(f"تم تسجيل المخالفة للطالب {student_tuple.name}")

    elif choice == "👥 إدارة المعلمين" and user['role'] == 'admin':
        st.header("👥 إدارة حسابات المعلمين")
        
        with st.form("add_teacher_form"):
            t_name = st.text_input("اسم المعلم الكامل")
            t_username = st.text_input("اسم المستخدم (Username)")
            t_password = st.text_input("كلمة المرور (Password)")
            submit = st.form_submit_button("إضافة معلم جديد")
            
            if submit:
                if t_name and t_username and t_password:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'teacher', ?)", (t_username, t_password, t_name))
                        conn.commit()
                        st.success(f"تم إنشاء حساب للمعلم {t_name} بنجاح!")
                    except:
                        st.error("اسم المستخدم هذا مستخدم بالفعل.")
                else:
                    st.error("يرجى ملء جميع الحقول.")

        st.subheader("قائمة الحسابات المسجلة")
        df_users = pd.read_sql_query("SELECT id, name, username, role FROM users", conn)
        st.dataframe(df_users, use_container_width=True)

    elif choice == "📊 التقارير العامة" and user['role'] == 'admin':
        st.header("📊 التقارير والإحصائيات الشاملة")
        
        tab_att, tab_viol = st.tabs(["سجل الغياب العام", "سجل المخالفات العام"])
        
        with tab_att:
            df_att = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC", conn)
            st.dataframe(df_att, use_container_width=True)
            
        with tab_viol:
            df_viol = pd.read_sql_query("SELECT * FROM violations ORDER BY date DESC", conn)
            st.dataframe(df_viol, use_container_width=True)

    conn.close()
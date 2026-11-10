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
        c.execute("INSERT INTO users (username, password, role, name) VALUES ('admin', '121345', 'admin', 'Administrator')")
    
    default_classes = ["سادس/1", "سادس/2", "سابع/1", "سابع/2"]
    for cls in default_classes:
        c.execute("INSERT OR IGNORE INTO classes (class_name) VALUES (?)", (cls,))
        
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 2. الهوية البصرية المطابقة تماماً لمنصة نور (تصميم ثنائي متناسق)
# ---------------------------------------------------------
st.set_page_config(page_title="مدرسة السلطان فيصل بن تركي (5-7) | نور", layout="wide", page_icon="🏫")

st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .noor-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.9) 100%), 
                    url('https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1200&q=80');
        background-size: cover;
        background-position: center;
        padding: 60px 40px;
        border-radius: 20px;
        color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .login-card-noor {
        background: #ffffff;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        background-color: #5b46d4;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1rem;
        width: 100%;
        box-shadow: 0 4px 12px rgba(91, 70, 212, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4c37bc;
        color: white;
    }
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #ffffff;
    }
    div[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول بتصميم منصة نور الثنائي
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.3, 1], gap="large")
    
    with col_left:
        st.markdown("""
            <div class='noor-banner'>
                <div style='font-size: 2rem; font-weight: bold; margin-bottom: 10px; color: #38bdf8;'>noor نور</div>
                <h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 20px; line-height: 1.3;'>أهلاً بك في المتعة الحقيقية للتعلم الذكي</h1>
                <p style='font-size: 1.2rem; color: #cbd5e1; margin-bottom: 30px;'>مدرسة السلطان فيصل بن تركي للتعليم الأساسي (5-7)<br>بوابة شؤون الطلاب والمتابعة السلوكية</p>
                <div style='display: flex; gap: 15px; align-items: center;'>
                    <span style='background: rgba(56, 189, 248, 0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; border: 1px solid #38bdf8;'>وزارة التربية والتعليم</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown("<div class='login-card-noor'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #1e293b; margin-bottom: 5px; font-weight: 700;'>تسجيل الدخول</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; margin-bottom: 25px; font-size: 0.95rem;'>أدخل بيانات حساب الكادر التعليمي للمتابعة</p>", unsafe_allow_html=True)
        
        username_input = st.text_input("اسم الدخول (Username)", placeholder="أدخل اسم المستخدم")
        password_input = st.text_input("كلمة المرور (Password)", type="password", placeholder="أدخل كلمة المرور")
        
        st.markdown("<div style='margin: 10px 0 20px 0;'><a href='#' style='color: #5b46d4; text-decoration: none; font-size: 0.9rem;'>أنسيت بيانات الدخول؟</a></div>", unsafe_allow_html=True)
        
        if st.button("تسجيل الدخول", use_container_width=True):
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
        
        st.markdown("<hr style='margin: 25px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>منصة نور التعليمية الذكية</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. داخل النظام (اللوحة والخدمات الكاملة دون أي حذف)
# ---------------------------------------------------------
else:
    user = st.session_state.user
    st.sidebar.markdown(f"### 👋 Welcome")
    st.sidebar.markdown(f"**{user['name']}**")
    st.sidebar.info(f"Permissions: {user['role']}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Main Menu")
    menu_options = ["📋 رصد الغياب والحضور", "⚠️ تسجيل المخالفات السلوكية", "📚 إضافة صفوف وطلاب", "👥 إدارة المعلمين", "📊 التقارير العامة"]
    choice = st.sidebar.radio("Navigation", menu_options, label_visibility="collapsed")

    conn = sqlite3.connect('faisal_school.db')

    if choice == "📋 رصد الغياب والحضور":
        st.markdown("<div class='main-header'>🏫 تسجيل ورصد الحضور والغياب اليومي</div>", unsafe_allow_html=True)
        
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("Class select edition", df_classes['class_name'] if not df_classes.empty else [])
        att_date = st.date_input("Date", date.today())
        
        if selected_class:
            st.markdown(f"### طلاب صف {selected_class}")
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            
            if df_students.empty:
                st.info("لا يوجد طلاب مسجلين في هذا الصف حالياً. قم بإضافتهم من قسم (إضافة صفوف وطلاب).")
            else:
                records = []
                for _, row in df_students.iterrows():
                    col1, col2 = st.columns([3, 2])
                    col1.write(row['name'])
                    status = col2.selectbox("Status", ["حاضر", "غائب", "متأخر", "غائب بعذر"], key=f"att_{row['id']}")
                    records.append((row['id'], row['name'], selected_class, status, str(att_date), user['name']))
                
                if st.button("حفظ سجل الغياب"):
                    c = conn.cursor()
                    for r in records:
                        c.execute("INSERT INTO attendance (student_id, student_name, class_name, status, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?)", r)
                    conn.commit()
                    st.success("تم حفظ الحضور والغياب بنجاح تام!")

    elif choice == "⚠️ تسجيل المخالفات السلوكية":
        st.markdown("<div class='main-header'>⚠️ تسجيل ومتابعة المخالفات السلوكية</div>", unsafe_allow_html=True)
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("اختر الصف", df_classes['class_name'] if not df_classes.empty else [])
        
        if selected_class:
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            if not df_students.empty:
                student_tuple = st.selectbox("اختر الطالب", options=df_students.itertuples(), format_func=lambda x: x.name)
                v_type = st.selectbox("نوع المخالفة", ["عدم إحضار أدوات/كتب", "استخدام الهاتف", "التأخر عن الحصة", "إثارة الشغب", "سلوك غير لائق"])
                v_action = st.text_input("الإجراء المتخذ (تنبيه شفوي / استدعاء ولي أمر...)")
                v_date = st.date_input("تاريخ المخالفة", date.today())
                
                if st.button("توثيق المخالفة"):
                    c = conn.cursor()
                    c.execute("INSERT INTO violations (student_id, student_name, class_name, violation_type, action, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (student_tuple.id, student_tuple.name, selected_class, v_type, v_action, str(v_date), user['name']))
                    conn.commit()
                    st.success(f"تم تسجيل المخالفة للطالب {student_tuple.name} بنجاح.")

    elif choice == "📚 إضافة صفوف وطلاب":
        st.markdown("<div class='main-header'>📚 إدارة الصفوف والطلاب</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["إضافة صف/شعبة", "إضافة طالب جديد"])
        
        with tab1:
            new_class = st.text_input("اسم الصف/الشعبة (مثال: سادس/1)")
            if st.button("حفظ الصف الجديد"):
                if new_class:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO classes (class_name) VALUES (?)", (new_class,))
                        conn.commit()
                        st.success(f"تمت إضافة الصف {new_class} بنجاح!")
                    except:
                        st.warning("هذا الصف مسجل مسبقاً.")
                else:
                    st.error("الرجاء إدخال اسم الصف.")
                    
        with tab2:
            df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
            selected_class = st.selectbox("اختر الصف لإضافة الطالب", df_classes['class_name'] if not df_classes.empty else [])
            student_name = st.text_input("اسم الطالب الثلاثي")
            if st.button("تسجيل الطالب"):
                if student_name and selected_class:
                    c = conn.cursor()
                    c.execute("INSERT INTO students (name, class_name) VALUES (?, ?)", (student_name, selected_class))
                    conn.commit()
                    st.success(f"تم تسجيل الطالب {student_name} بنجاح!")
                else:
                    st.error("الرجاء إكمال البيانات.")

    elif choice == "👥 إدارة المعلمين":
        st.markdown("<div class='main-header'>👥 إدارة حسابات الكادر التعليمي</div>", unsafe_allow_html=True)
        with st.form("add_teacher"):
            t_name = st.text_input("اسم المعلم الكامل")
            t_username = st.text_input("اسم المستخدم للدخول")
            t_password = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة حساب معلم"):
                if t_name and t_username and t_password:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'teacher', ?)", (t_username, t_password, t_name))
                        conn.commit()
                        st.success(f"تم إنشاء حساب المعلم {t_name} بنجاح!")
                    except:
                        st.error("اسم المستخدم مسجل مسبقاً.")
                else:
                    st.error("يرجى ملء كافة الحقول.")
        
        st.subheader("قائمة المعلمين")
        df_users = pd.read_sql_query("SELECT id, name, username, role FROM users", conn)
        st.dataframe(df_users, use_container_width=True)

    elif choice == "📊 التقارير العامة":
        st.markdown("<div class='main-header'>📊 التقارير والسجلات المدرسية</div>", unsafe_allow_html=True)
        tab_att, tab_viol = st.tabs(["سجل الحضور والغياب", "سجل المخالفات السلوكية"])
        with tab_att:
            df_att = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC", conn)
            st.dataframe(df_att, use_container_width=True)
        with tab_viol:
            df_viol = pd.read_sql_query("SELECT * FROM violations ORDER BY date DESC", conn)
            st.dataframe(df_viol, use_container_width=True)

    conn.close()
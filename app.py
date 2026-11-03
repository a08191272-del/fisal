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
    
    default_classes = [f"سادس/{i}" for i in range(1, 5)] + \
                      [f"سابع/{i}" for i in range(1, 5)] + \
                      [f"ثامن/{i}" for i in range(1, 5)] + \
                      [f"تاسع/{i}" for i in range(1, 10)]
    for cls in default_classes:
        c.execute("INSERT OR IGNORE INTO classes (class_name) VALUES (?)", (cls,))
        
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 2. الهوية البصرية المضيئة والعصرية (مطابقة للصورة)
# ---------------------------------------------------------
st.set_page_config(page_title="مدرسة فيصل بن تركي - إدارة الطلاب", layout="wide", page_icon="🏫")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    .main-title {
        text-align: center;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 5px;
        text-shadow: 0 2px 10px rgba(56, 189, 248, 0.3);
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .login-card {
        background: rgba(30, 41, 59, 0.75);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
        color: white;
        border-radius: 12px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #075985 100%);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-left: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول بتصميم عصري مضيء
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🏫 صرح مدرسة فيصل بن تركي التعليمي</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>بوابة شؤون الطلاب، الحضور والمتابعة السلوكية</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #38bdf8; margin-bottom: 20px;'>🔐 تسجيل دخول الكادر التعليمي</h3>", unsafe_allow_html=True)
        
        username_input = st.text_input("اسم المستخدم")
        password_input = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول للنظام", use_container_width=True):
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
    st.sidebar.info(f"الصلاحية: {'مدير النظام' if user['role'] == 'admin' else 'معلم'}")
    
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
            new_class = st.text_input("اسم الصف/الشعبة (مثال: تاسع/10)")
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
        st.header("📋 تسجیل ورصد الحضور والغياب")
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
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
# 2. إعداد واجهة Streamlit والهوية البصرية المشرقة
# ---------------------------------------------------------
st.set_page_config(page_title="مدرسة فيصل بن تركي - إدارة الطلاب", layout="wide", page_icon="🏫")

# تصميم بصري مبهج ومريح للعين يعكس أجواء المدرسة والنشاط
st.markdown("""
    <style>
    .main { background-color: #f0fdf4; }
    .stButton>button { background-color: #059669; color: white; border-radius: 10px; font-weight: bold; border: none; padding: 0.5rem 1rem; }
    .stButton>button:hover { background-color: #047857; color: white; }
    h1, h2, h3 { color: #065f46; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: right; }
    div[data-testid="stSidebar"] { background-color: #ecfdf5; border-left: 2px solid #d1fae5; }
    .school-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0.2,0.1,0.05); margin-bottom: 20px; border-right: 5px solid #059669; }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------------------------------------------------
# 3. شاشة تسجيل الدخول بتصميم مشرق
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🏫 صرح مدرسة فيصل بن تركي التعليمي</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #047857;'>بوابة شؤون الطلاب، الحضور والمتابعة السلوكية</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="school-card">', unsafe_allow_html=True)
        st.subheader("🔐 تسجيل دخول الكادر التعليمي")
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
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة، تأكد من البيانات.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. داخل النظام بعد تسجيل الدخول
# ---------------------------------------------------------
else:
    user = st.session_state.user
    st.sidebar.markdown(f"### 👨‍🏫 مرحباً بك، {user['name']}")
    st.sidebar.info(f"الصلاحية: {'مدير النظام العام' if user['role'] == 'admin' else 'معلم المادة/الصف'}")
    
    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    menu_options = ["📋 رصد الغياب والحضور", "⚠️ تسجيل المخالفات السلوكية", "📚 إضافة صفوف وطلاب جدد"]
    if user['role'] == 'admin':
        menu_options.extend(["👥 إدارة المعلمين", "📊 التقارير والإحصائيات الشاملة"])

    choice = st.sidebar.radio("📌 لوحة التحكم المدرسية", menu_options)

    conn = sqlite3.connect('faisal_school.db')

    if choice == "📚 إضافة صفوف وطلاب جدد":
        st.header("📚 سجل إضافات الصفوف والطلاب")
        tab1, tab2 = st.tabs(["إضافة شعبة أو صف دراسي", "تسجيل طالب جديد"])
        
        with tab1:
            st.subheader("إضافة صف جديد للمدرسة")
            new_class = st.text_input("اسم الصف والشعبة (مثال: تاسع/10 أو سابع/5)")
            if st.button("حفظ الصف الجديد"):
                if new_class:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO classes (class_name) VALUES (?)", (new_class,))
                        conn.commit()
                        st.success(f"تم اعتماد وإضافة الصف {new_class} بنجاح!")
                    except:
                        st.warning("هذا الصف مسجل مسبقاً في النظام.")
                else:
                    st.error("الرجاء كتابة اسم الصف.")
                    
        with tab2:
            st.subheader("إضافة طالب إلى الصفوف")
            df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
            selected_class = st.selectbox("اختر الصف الدراسي", df_classes['class_name'] if not df_classes.empty else [])
            student_name = st.text_input("اسم الطالب كاملاً")
            if st.button("تسجيل الطالب"):
                if student_name and selected_class:
                    c = conn.cursor()
                    c.execute("INSERT INTO students (name, class_name) VALUES (?, ?)", (student_name, selected_class))
                    conn.commit()
                    st.success(f"تم تسجيل الطالب {student_name} بنجاح في صف {selected_class}")
                else:
                    st.error("الرجاء إكمال كافة بيانات الطالب.")

    elif choice == "📋 رصد الغياب والحضور":
        st.header("📋 دفتر رصد الحضور والغياب اليومي")
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("اختر الصف الدراسي للمتابعة", df_classes['class_name'] if not df_classes.empty else [])
        att_date = st.date_input("تاريخ اليوم الدراسي", date.today())
        
        if selected_class:
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            if df_students.empty:
                st.info("لا يوجد طلاب مسجلين في هذا الصف حتى الآن.")
            else:
                st.subheader(f"قائمة طلاب صف: {selected_class}")
                records = []
                for _, row in df_students.iterrows():
                    col1, col2 = st.columns([3, 2])
                    col1.markdown(f"**{row['name']}**")
                    status = col2.selectbox("الحالة", ["حاضر", "غائب", "متأخر", "غائب بعذر"], key=f"att_{row['id']}")
                    records.append((row['id'], row['name'], selected_class, status, str(att_date), user['name']))
                
                if st.button("💾 حفظ وتثبيت سجل الحضور"):
                    c = conn.cursor()
                    for r in records:
                        c.execute("INSERT INTO attendance (student_id, student_name, class_name, status, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?)", r)
                    conn.commit()
                    st.success("تم حفظ الغياب بنجاح ومزامنته مع قاعدة بيانات المدرسة!")

    elif choice == "⚠️ تسجيل المخالفات السلوكية":
        st.header("⚠️ سجل متابعة وتوثيق المخالفات السلوكية")
        df_classes = pd.read_sql_query("SELECT class_name FROM classes", conn)
        selected_class = st.selectbox("اختر الصف", df_classes['class_name'] if not df_classes.empty else [])
        
        if selected_class:
            df_students = pd.read_sql_query("SELECT id, name FROM students WHERE class_name=?", conn, params=(selected_class,))
            if not df_students.empty:
                student_tuple = st.selectbox("اختر الطالب المعني", options=df_students.itertuples(), format_func=lambda x: x.name)
                v_type = st.selectbox("نوع المخالفة السلوكية", ["عدم إحضار أدوات/كتب", "استخدام الهاتف", "التأخر عن الحصة", "إثارة الشغب", "الهروب من الحصة", "سلوك غير لائق"])
                v_action = st.text_input("الإجراء التربوي المتخذ (تنبيه شفوي / استدعاء ولي أمر / تعهد...)")
                v_date = st.date_input("تاريخ المخالفة", date.today())
                
                if st.button("تسجيل وتوثيق المخالفة"):
                    c = conn.cursor()
                    c.execute("INSERT INTO violations (student_id, student_name, class_name, violation_type, action, date, recorded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (student_tuple.id, student_tuple.name, selected_class, v_type, v_action, str(v_date), user['name']))
                    conn.commit()
                    st.success(f"تم توثيق المخالفة للطالب {student_tuple.name} بنجاح.")

    elif choice == "👥 إدارة المعلمين" and user['role'] == 'admin':
        st.header("👥 إدارة حسابات الكادر التعليمي")
        
        with st.form("add_teacher_form"):
            t_name = st.text_input("اسم المعلم الثلاثي")
            t_username = st.text_input("اسم المستخدم للدخول (Username)")
            t_password = st.text_input("كلمة المرور (Password)")
            submit = st.form_submit_button("إضافة حساب معلم جديد")
            
            if submit:
                if t_name and t_username and t_password:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'teacher', ?)", (t_username, t_password, t_name))
                        conn.commit()
                        st.success(f"تم إنشاء حساب المعلم {t_name} بنجاح!")
                    except:
                        st.error("اسم المستخدم مستخدم مسبقاً، اختر اسماً آخر.")
                else:
                    st.error("يرجى تعبئة كافة الحقول المطلوبة.")

        st.subheader("سجل المعلمين المسجلين بالنظام")
        df_users = pd.read_sql_query("SELECT id, name, username, role FROM users", conn)
        st.dataframe(df_users, use_container_width=True)

    elif choice == "📊 التقارير والإحصائيات الشاملة" and user['role'] == 'admin':
        st.header("📊 التقارير والسجلات المدرسية العامة")
        
        tab_att, tab_viol = st.tabs(["سجل الحضور والغياب العام", "سجل المخالفات السلوكية العام"])
        
        with tab_att:
            df_att = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC", conn)
            st.dataframe(df_att, use_container_width=True)
            
        with tab_viol:
            df_viol = pd.read_sql_query("SELECT * FROM violations ORDER BY date DESC", conn)
            st.dataframe(df_viol, use_container_width=True)

    conn.close()
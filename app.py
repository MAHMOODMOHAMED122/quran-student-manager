import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام إدارة حلقة القرآن", layout="wide")

# --- دالة إدارة البيانات (JSON) ---
FILENAME = 'students_data.json'

def load_data():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# تحميل البيانات في ذاكرة التطبيق
if 'students' not in st.session_state:
    st.session_state.students = load_data()

students = st.session_state.students

# --- واجهة التطبيق ---
st.title("🕋 نظام إدارة طلاب حلقة القرآن")

# القائمة الجانبية
menu = ["📊 لوحة التحكم", "📝 تسجيل الحضور والإنجاز", "➕ إضافة طالب", "⚙️ إدارة المسؤوليات"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# --- 1. لوحة التحكم ---
if choice == "📊 لوحة التحكم":
    st.subheader("📊 إحصائيات عامة")
    if students:
        total_students = len(students)
        completed = sum(1 for s in students.values() if s['current_part'] >= 30)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("عدد الطلاب", total_students)
        col2.metric("المختمين", completed)
        col3.metric("نسبة الإنجاز الجماعي", f"{(completed/total_students)*100:.1f}%" if total_students > 0 else "0%")

        st.markdown("---")
        st.subheader("📋 قائمة الطلاب")
        
        data_list = []
        for name, info in students.items():
            data_list.append({
                "الاسم": name,
                "الجزء الحالي": info['current_part'],
                "المتبقي": 30 - info['current_part'],
                "المسؤولية": info['role'],
                "عدد أيام الحضور": len(info['attendance'])
            })
        
        df = pd.DataFrame(data_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد طلاب مسجلون حالياً. ابدأ بإضافة طالب.")

# --- 2. تسجيل الحضور والإنجاز ---
elif choice == "📝 تسجيل الحضور والإنجاز":
    st.subheader("📝 تحديث يومي")
    if not students:
        st.warning("يرجى إضافة طلاب أولاً.")
    else:
        name = st.selectbox("اختر الطالب", list(students.keys()))
        col1, col2 = st.columns(2)
        
        with col1:
            current_part = st.number_input("الجزء الذي وصل إليه", 0, 30, value=students[name]['current_part'])
            mark_present = st.checkbox("تسجيل حضور اليوم")
        
        with col2:
            note = st.text_area("ملاحظات (نقاط القوة أو التعديلات)")
        
        if st.button("حفظ التحديث"):
            # تحديث الجزء
            students[name]['current_part'] = current_part
            # تسجيل الحضور
            if mark_present:
                today = datetime.now().strftime('%Y-%m-%d')
                if today not in students[name]['attendance']:
                    students[name]['attendance'].append(today)
            # إضافة الملاحظات
            if note:
                students[name]['notes'].append({"date": str(datetime.now()), "content": note})
            
            # ترقية تلقائية للمسؤولية
            remaining = 30 - current_part
            if remaining <= 2 and students[name]['role'] == 'طالب':
                students[name]['role'] = 'مساعد مراجع'
                st.balloons()
                st.success(f"🎊 تمت ترقية {name} إلى 'مساعد مراجع'!")
            
            save_data(students)
            st.success(f"تم تحديث بيانات {name}")

# --- 3. إضافة طالب ---
elif choice == "➕ إضافة طالب":
    st.subheader("➕ إضافة طالب جديد")
    with st.form("add_student"):
        new_name = st.text_input("اسم الطالب")
        start_part = st.number_input("بدأ من الجزء رقم", 0, 30, 0)
        submit = st.form_submit_button("إضافة الطالب")
        
        if submit:
            if new_name and new_name not in students:
                students[new_name] = {
                    'current_part': start_part,
                    'attendance': [],
                    'notes': [],
                    'role': 'طالب'
                }
                save_data(students)
                st.success(f"تمت إضافة {new_name} بنجاح!")
            else:
                st.error("الاسم موجود مسبقاً أو غير صالح.")

# --- 4. إدارة المسؤوليات ---
elif choice == "⚙️ إدارة المسؤوليات":
    st.subheader("⚙️ تعيين مسؤوليات خاصة")
    if students:
        name = st.selectbox("اختر الطالب لتغيير مسؤوليته", list(students.keys()))
        roles_list = ['طالب', 'مساعد مراجع', 'قائد مجموعة', 'مراقب صلاة', 'مسؤول حضور']
        current_role = students[name]['role']
        new_role = st.selectbox(f"المسؤولية الحالية: {current_role}", roles_list)
        
        if st.button("تحديث المسؤولية"):
            students[name]['role'] = new_role
            save_data(students)
            st.success(f"تم تغيير دور {name} إلى {new_role}")
    else:
        st.info("لا يوجد طلاب.")

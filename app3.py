import streamlit as st
import json
import os
from datetime import datetime
from collections import defaultdict
import pandas as pd

# إعدادات الصفحة
st.set_page_config(
    page_title="🕌 نظام إدارة طلاب القرآن",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل CSS مخصص
st.markdown("""
    <style>
    * {
        direction: rtl;
        text-align: right;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: bold;
        padding: 10px 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# قائمة جميع 114 سورة
SURAHS = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال",
    "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء",
    "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء",
    "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
    "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر",
    "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة",
    "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات",
    "عبس", "التكوير", "الإنفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى",
    "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", 
    "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر",
    "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص",
    "الفلق", "الناس"
]

BEHAVIORS = {"ممتاز": 5, "جيد جداً": 4, "جيد": 3, "متوسط": 2, "ضعيف": 1}

class QuranManager:
    def __init__(self, filename='students_data.json'):
        self.filename = filename
        self.students = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, indent=2, ensure_ascii=False)
    
    def add_student(self, name):
        if name in self.students: return False, f"❌ الطالب '{name}' موجود!"
        self.students[name] = {
            'completed_surahs': [], 'next_memorization': '',
            'behavior': 'جيد', 'level': 3, 'attendance_days': [],
            'notes': [], 'date_added': datetime.now().isoformat()
        }
        self.save_data()
        return True, f"✅ تم إضافة الطالب '{name}'!"

    def add_surah(self, name, surah):
        if surah not in self.students[name]['completed_surahs']:
            self.students[name]['completed_surahs'].append(surah)
            self.save_data()
            return True, "✅ تم التسجيل"
        return False, "❌ مسجلة مسبقاً"

    def delete_surah(self, name, surah):
        self.students[name]['completed_surahs'].remove(surah)
        self.save_data()
        return True, "✅ تم الحذف"

    def set_next_memorization(self, name, surah):
        self.students[name]['next_memorization'] = surah
        self.save_data()
        return True, "✅ تم التعيين"

    def set_behavior_and_level(self, name, behavior, level):
        self.students[name]['behavior'] = behavior
        self.students[name]['level'] = level
        self.save_data()
        return True, "✅ تم التحديث"

    def add_attendance_day(self, name, date_str):
        if date_str not in self.students[name]['attendance_days']:
            self.students[name]['attendance_days'].append(date_str)
            self.save_data()
            return True, "✅ تم تسجيل الحضور"
        return False, "❌ مسجل مسبقاً"

    def add_note(self, name, note):
        self.students[name]['notes'].append({'content': note, 'date': datetime.now().isoformat()})
        self.save_data()
        return True, "✅ تمت إضافة الملاحظة"

    def remove_student(self, name):
        del self.students[name]
        self.save_data()
        return True, "✅ تم حذف الطالب"

    def get_all_students(self):
        return sorted(self.students.keys())

    def get_student_data(self, name):
        return self.students.get(name)

if 'manager' not in st.session_state:
    st.session_state.manager = QuranManager()
manager = st.session_state.manager

st.markdown('<h1 style="text-align: center;">🕌 نظام إدارة طلاب القرآن</h1>', unsafe_allow_html=True)

# التبويبات
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 لوحة المراقبة", "➕ إضافة طالب", "📖 السور المحفوظة", "📝 التحفيظ القادم", 
    "👤 السلوك", "📅 الحضور", "👁️ ملف الطالب", "🗑️ حذف طالب"
])

all_students = manager.get_all_students()

with tab1:
    if all_students:
        cols = st.columns(4)
        cols[0].metric("👥 الطلاب", len(all_students))
        st.dataframe(pd.DataFrame([{"الاسم": s, "السور": len(manager.students[s]['completed_surahs']), "المستوى": manager.students[s]['level']} for s in all_students]), use_container_width=True)
    else: st.warning("لا يوجد طلاب")

with tab2:
    name = st.text_input("اسم الطالب الجديد")
    if st.button("إضافة"):
        if name:
            s, m = manager.add_student(name)
            if s: st.success(m); st.rerun()
            else: st.error(m)

with tab3:
    if all_students:
        s_name = st.selectbox("اختر الطالب", all_students, key="tab3_s")
        surah = st.selectbox("اختر السورة", SURAHS)
        if st.button("تسجيل السورة"):
            manager.add_surah(s_name, surah)
            st.rerun()
        st.write("السور المحفوظة:", manager.students[s_name]['completed_surahs'])

with tab4:
    if all_students:
        s_name = st.selectbox("اختر الطالب", all_students, key="tab4_s")
        next_s = st.selectbox("السورة القادمة", SURAHS)
        if st.button("تعيين"):
            manager.set_next_memorization(s_name, next_s)
            st.rerun()

with tab5:
    if all_students:
        s_name = st.selectbox("اختر الطالب", all_students, key="tab5_s")
        beh = st.radio("السلوك", list(BEHAVIORS.keys()))
        lvl = st.slider("المستوى", 1, 5)
        if st.button("حفظ التقييم"):
            manager.set_behavior_and_level(s_name, beh, lvl)
            st.rerun()

with tab6:
    if all_students:
        s_name = st.selectbox("اختر الطالب", all_students, key="tab6_s")
        date = st.date_input("التاريخ")
        if st.button("تسجيل الحضور"):
            manager.add_attendance_day(s_name, str(date))
            st.success("تم")
        note = st.text_area("ملاحظة")
        if st.button("إضافة ملاحظة"):
            manager.add_note(s_name, note)
            st.success("تم")

with tab7:
    if all_students:
        s_name = st.selectbox("اختر الطالب", all_students, key="tab7_s")
        data = manager.get_student_data(s_name)
        st.json(data)

with tab8:
    if all_students:
        s_name = st.selectbox("حذف الطالب", all_students, key="tab8_s")
        if st.button("تأكيد الحذف"):
            manager.remove_student(s_name)
            st.rerun()

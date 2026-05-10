import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Configuration
st.set_page_config(
    page_title="🕌 نظام إدارة طلاب القرآن",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arabic styling
st.markdown("""
    <style>
        body {
            direction: rtl;
        }
        .main {
            direction: rtl;
        }
        h1, h2, h3, h4, h5, h6 {
            text-align: right;
        }
        .stButton > button {
            width: 100%;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# All 114 Surahs
SURAHS = {
    1: "الفاتحة",
    2: "البقرة",
    3: "آل عمران",
    4: "النساء",
    5: "المائدة",
    6: "الأنعام",
    7: "الأعراف",
    8: "الأنفال",
    9: "التوبة",
    10: "يونس",
    11: "هود",
    12: "يوسف",
    13: "الرعد",
    14: "إبراهيم",
    15: "الحجر",
    16: "النحل",
    17: "الإسراء",
    18: "الكهف",
    19: "مريم",
    20: "طه",
    21: "الأنبياء",
    22: "الحج",
    23: "المؤمنون",
    24: "النور",
    25: "الفرقان",
    26: "الشعراء",
    27: "النمل",
    28: "القصص",
    29: "العنكبوت",
    30: "الروم",
    31: "لقمان",
    32: "السجدة",
    33: "الأحزاب",
    34: "سبأ",
    35: "فاطر",
    36: "يس",
    37: "الصافات",
    38: "ص",
    39: "الزمر",
    40: "غافر",
    41: "فصلت",
    42: "الشورى",
    43: "الزخرف",
    44: "الدخان",
    45: "الجاثية",
    46: "الأحقاف",
    47: "محمد",
    48: "الفتح",
    49: "الحجرات",
    50: "ق",
    51: "الذاريات",
    52: "الطور",
    53: "النجم",
    54: "القمر",
    55: "الرحمن",
    56: "الواقعة",
    57: "الحديد",
    58: "المجادلة",
    59: "الحشر",
    60: "الممتحنة",
    61: "الصف",
    62: "الجمعة",
    63: "المنافقون",
    64: "التغابن",
    65: "الطلاق",
    66: "التحريم",
    67: "الملك",
    68: "القلم",
    69: "الحاقة",
    70: "المعارج",
    71: "نوح",
    72: "الجن",
    73: "المزمل",
    74: "المدثر",
    75: "القيامة",
    76: "الإنسان",
    77: "المرسلات",
    78: "النبأ",
    79: "النازعات",
    80: "عبس",
    81: "التكوير",
    82: "الانفطار",
    83: "المطففين",
    84: "الانشقاق",
    85: "البروج",
    86: "الطارق",
    87: "الأعلى",
    88: "الغاشية",
    89: "الفجر",
    90: "البلد",
    91: "الشمس",
    92: "الليل",
    93: "الضحى",
    94: "الشرح",
    95: "التين",
    96: "العلق",
    97: "القدر",
    98: "البينة",
    99: "الزلزلة",
    100: "العاديات",
    101: "القارعة",
    102: "التكاثر",
    103: "العصر",
    104: "الهمزة",
    105: "الفيل",
    106: "قريش",
    107: "الماعون",
    108: "الكوثر",
    109: "الكافرون",
    110: "النصر",
    111: "المسد",
    112: "الإخلاص",
    113: "الفلق",
    114: "الناس"
}

BEHAVIOR_OPTIONS = {
    "ممتاز": 5,
    "جيد جداً": 4,
    "جيد": 3,
    "متوسط": 2,
    "ضعيف": 1
}

class QuranStudentManager:
    def __init__(self, filename='students_data.json'):
        self.filename = filename
        self.students = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, indent=2, ensure_ascii=False)
    
    def add_student(self, name):
        if name.lower() in [s.lower() for s in self.students]:
            return False, f"❌ الطالب '{name}' موجود بالفعل!"
        
        self.students[name] = {
            'completed_surahs': [],
            'current_surah': None,
            'next_memorization': None,
            'behavior': "جيد",
            'level': 3,
            'attendance': [],
            'notes': [],
            'date_added': datetime.now().isoformat()
        }
        self.save_data()
        return True, f"✅ تم إضافة الطالب '{name}' بنجاح!"
    
    def add_completed_surah(self, name, surah_number):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        if surah_number in self.students[name]['completed_surahs']:
            return False, f"⚠️ السورة '{SURAHS[surah_number]}' محفوظة بالفعل!"
        
        self.students[name]['completed_surahs'].append(surah_number)
        self.students[name]['completed_surahs'].sort()
        self.save_data()
        return True, f"✅ تم تسجيل سورة '{SURAHS[surah_number]}' للطالب '{name}'"
    
    def set_next_memorization(self, name, surah_number):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        self.students[name]['next_memorization'] = surah_number
        self.save_data()
        return True, f"✅ تم تعيين السورة التالية '{SURAHS[surah_number]}' للطالب '{name}'"
    
    def update_behavior_and_level(self, name, behavior, level):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        self.students[name]['behavior'] = behavior
        self.students[name]['level'] = level
        self.save_data()
        return True, f"✅ تم تحديث السلوك والمستوى للطالب '{name}'"
    
    def mark_attendance(self, name, date=None):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date in self.students[name]['attendance']:
            return False, f"⚠️ الطالب '{name}' محسوب الحضور في '{date}' بالفعل!"
        
        self.students[name]['attendance'].append(date)
        self.save_data()
        return True, f"✅ تم تسجيل حضور الطالب '{name}' في '{date}'"
    
    def add_note(self, name, note):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        self.students[name]['notes'].append({
            'content': note,
            'date': datetime.now().isoformat()
        })
        self.save_data()
        return True, f"✅ تم إضافة ملاحظة للطالب '{name}'"
    
    def get_student_profile(self, name):
        if name not in self.students:
            return None
        
        student = self.students[name]
        completed_count = len(student['completed_surahs'])
        
        return {
            'name': name,
            'completed_surahs': student['completed_surahs'],
            'completed_count': completed_count,
            'next_memorization': student['next_memorization'],
            'behavior': student['behavior'],
            'level': student['level'],
            'attendance_count': len(student['attendance']),
            'notes': student['notes'],
            'date_added': student['date_added'][:10],
            'remaining': 114 - completed_count
        }
    
    def get_summary(self):
        if not self.students:
            return []
        
        data = []
        for name, student in sorted(self.students.items()):
            completed = len(student['completed_surahs'])
            next_surah = SURAHS.get(student['next_memorization'], "لم يتم التحديد") if student['next_memorization'] else "لم يتم التحديد"
            
            data.append({
                'الاسم': name,
                'السور المحفوظة': completed,
                'المتبقي': 114 - completed,
                'النسبة المئوية': f"{(completed/114)*100:.1f}%",
                'الحضور': len(student['attendance']),
                'السلوك': student['behavior'],
                'المستوى': f"{'⭐' * student['level']}",
                'التحفيظ القادم': next_surah
            })
        
        return data
    
    def get_statistics(self):
        if not self.students:
            return {
                'total_students': 0,
                'avg_surahs': 0,
                'avg_level': 0,
                'completed_quran': 0
            }
        
        total_students = len(self.students)
        avg_surahs = sum(len(s['completed_surahs']) for s in self.students.values()) / total_students
        avg_level = sum(s['level'] for s in self.students.values()) / total_students
        completed_quran = sum(1 for s in self.students.values() if len(s['completed_surahs']) >= 114)
        
        return {
            'total_students': total_students,
            'avg_surahs': f"{avg_surahs:.1f}",
            'avg_level': f"{avg_level:.1f}",
            'completed_quran': completed_quran
        }
    
    def remove_student(self, name):
        if name not in self.students:
            return False, f"❌ الطالب '{name}' غير موجود!"
        
        del self.students[name]
        self.save_data()
        return True, f"✅ تم حذف الطالب '{name}' بنجاح"
    
    def get_all_students(self):
        return sorted(self.students.keys())

# Initialize manager
manager = QuranStudentManager()

# Main app
st.title("🕌 نظام إدارة طلاب القرآن الكريم")
st.markdown("### بسم الله الرحمن الرحيم")

# Sidebar
with st.sidebar:
    st.title("🎓 القائمة الرئيسية")
    page = st.radio(
        "اختر العملية:",
        [
            "📊 لوحة المراقبة",
            "➕ إضافة طالب جديد",
            "📖 السور المحفوظة",
            "📝 التحفيظ القادم",
            "👤 السلوك والمستوى",
            "📅 الحضور والملاحظات",
            "👁️ ملف الطالب",
            "🗑️ حذف طالب"
        ]
    )

# Page 1: Dashboard
if page == "📊 لوحة المراقبة":
    st.header("📊 لوحة المراقبة")
    
    stats = manager.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 إجمالي الطلاب", stats['total_students'])
    with col2:
        st.metric("📖 متوسط السور", stats['avg_surahs'])
    with col3:
        st.metric("⭐ متوسط المستوى", stats['avg_level'])
    with col4:
        st.metric("✅ أكملوا القرآن", stats['completed_quran'])
    
    st.divider()
    
    summary = manager.get_summary()
    if summary:
        df = pd.DataFrame(summary)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 لا توجد بيانات حتى الآن. ابدأ بإضافة طالب جديد!")

# Page 2: Add Student
elif page == "➕ إضافة طالب جديد":
    st.header("➕ إضافة طالب جديد")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_student = st.text_input("🎓 اسم الطالب:", placeholder="أدخل اسم الطالب...")
    with col2:
        if st.button("✅ إضافة الطالب", use_container_width=True):
            if new_student:
                success, message = manager.add_student(new_student)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("❌ يرجى إدخال اسم الطالب!")

# Page 3: Add Completed Surah
elif page == "📖 السور المحفوظة":
    st.header("📖 تسجيل السور المحفوظة")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns(2)
        with col1:
            selected_student = st.selectbox("🎓 اختر الطالب:", students)
        with col2:
            surah_names = {SURAHS[i]: i for i in range(1, 115)}
            selected_surah_name = st.selectbox("📖 اختر السورة:", list(surah_names.keys()))
            selected_surah_number = surah_names[selected_surah_name]
        
        if st.button("✅ تسجيل السورة", use_container_width=True):
            success, message = manager.add_completed_surah(selected_student, selected_surah_number)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        st.divider()
        
        profile = manager.get_student_profile(selected_student)
        if profile and profile['completed_surahs']:
            st.subheader(f"📖 السور المحفوظة لـ {selected_student}:")
            completed_names = [SURAHS[num] for num in profile['completed_surahs']]
            for i, surah in enumerate(completed_names, 1):
                st.write(f"{i}. {surah}")
            
            st.info(f"✅ عدد السور المحفوظة: {profile['completed_count']}/114 ({(profile['completed_count']/114)*100:.1f}%)")
    else:
        st.warning("⚠️ لا توجد طلاب. يرجى إضافة طالب أولاً!")

# Page 4: Set Next Memorization
elif page == "📝 التحفيظ القادم":
    st.header("📝 تعيين التحفيظ القادم")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns(2)
        with col1:
            selected_student = st.selectbox("🎓 اختر الطالب:", students)
        with col2:
            surah_names = {SURAHS[i]: i for i in range(1, 115)}
            selected_surah_name = st.selectbox("📖 اختر السورة التالية:", list(surah_names.keys()))
            selected_surah_number = surah_names[selected_surah_name]
        
        if st.button("✅ تعيين التحفيظ", use_container_width=True):
            success, message = manager.set_next_memorization(selected_student, selected_surah_number)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.warning("⚠️ لا توجد طلاب. يرجى إضافة طالب أولاً!")

# Page 5: Behavior and Level
elif page == "👤 السلوك والمستوى":
    st.header("👤 تقييم السلوك والمستوى")
    
    students = manager.get_all_students()
    if students:
        selected_student = st.selectbox("🎓 اختر الطالب:", students)
        
        col1, col2 = st.columns(2)
        with col1:
            behavior = st.selectbox(
                "👣 تقييم السلوك:",
                list(BEHAVIOR_OPTIONS.keys()),
                index=1
            )
        with col2:
            level = st.slider("⭐ المستوى (من 5 نجوم):", 1, 5, 3)
        
        if st.button("✅ حفظ التقييم", use_container_width=True):
            success, message = manager.update_behavior_and_level(selected_student, behavior, level)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        st.divider()
        
        profile = manager.get_student_profile(selected_student)
        if profile:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👣 السلوك الحالي:", profile['behavior'])
            with col2:
                st.metric("⭐ المستوى الحالي:", f"{'⭐' * profile['level']}")
    else:
        st.warning("⚠️ لا توجد طلاب. يرجى إضافة طالب أولاً!")

# Page 6: Attendance and Notes
elif page == "📅 الحضور والملاحظات":
    st.header("📅 الحضور والملاحظات")
    
    students = manager.get_all_students()
    if students:
        tab1, tab2 = st.tabs(["📅 تسجيل الحضور", "📝 إضافة ملاحظة"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                student_att = st.selectbox("🎓 اختر الطالب:", students, key="attendance")
            with col2:
                att_date = st.date_input("📅 تاريخ الحضور:")
            
            if st.button("✅ تسجيل الحضور", use_container_width=True):
                success, message = manager.mark_attendance(student_att, att_date.strftime('%Y-%m-%d'))
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            col1, col2 = st.columns([3, 1])
            with col1:
                student_note = st.selectbox("🎓 اختر الطالب:", students, key="notes")
            
            note_text = st.text_area("📝 الملاحظة:", placeholder="أدخل الملاحظة هنا...")
            
            if st.button("✅ إضافة الملاحظة", use_container_width=True):
                if note_text:
                    success, message = manager.add_note(student_note, note_text)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ يرجى إدخال الملاحظة!")
    else:
        st.warning("⚠️ لا توجد طلاب. يرجى إضافة طالب أولاً!")

# Page 7: Student Profile
elif page == "👁️ ملف الطالب":
    st.header("👁️ ملف الطالب")
    
    students = manager.get_all_students()
    if students:
        selected_student = st.selectbox("🎓 اختر الطالب:", students)
        
        profile = manager.get_student_profile(selected_student)
        if profile:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📖 السور المحفوظة", f"{profile['completed_count']}/114")
            with col2:
                st.metric("📊 النسبة المئوية", f"{(profile['completed_count']/114)*100:.1f}%")
            with col3:
                st.metric("👣 السلوك", profile['behavior'])
            with col4:
                st.metric("⭐ المستوى", f"{'⭐' * profile['level']}")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📖 السور المحفوظة:")
                if profile['completed_surahs']:
                    for i, surah_num in enumerate(profile['completed_surahs'], 1):
                        st.write(f"{i}. {SURAHS[surah_num]}")
                else:
                    st.info("لم يحفظ أي سورة بعد")
                
                st.subheader("📝 التحفيظ القادم:")
                if profile['next_memorization']:
                    st.success(f"📖 {SURAHS[profile['next_memorization']]}")
                else:
                    st.info("لم يتم تحديد التحفيظ القادم")
            
            with col2:
                st.subheader("📅 معلومات الحضور:")
                st.metric("✅ أيام الحضور", profile['attendance_count'])
                st.metric("📆 تاريخ التسجيل", profile['date_added'])
                
                st.subheader("📝 الملاحظات:")
                if profile['notes']:
                    for note in profile['notes']:
                        note_date = note['date'][:10]
                        st.write(f"**{note_date}**: {note['content']}")
                else:
                    st.info("لا توجد ملاحظات")
    else:
        st.warning("⚠️ لا توجد طلاب. يرجى إضافة طالب أولاً!")

# Page 8: Remove Student
elif page == "🗑️ حذف طالب":
    st.header("🗑️ حذف طالب")
    
    students = manager.get_all_students()
    if students:
        selected_student = st.selectbox("🎓 اختر الطالب للحذف:", students)
        
        st.warning(f"⚠️ تحذير: سيتم حذف جميع بيانات الطالب '{selected_student}'!")
        
        if st.button("🗑️ تأكيد الحذف", use_container_width=True):
            success, message = manager.remove_student(selected_student)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.warning("⚠️ لا توجد طلاب للحذف!")

st.divider()
st.markdown("---")
st.markdown("<div style='text-align: center;'>🕌 نظام متخصص لإدارة طلاب القرآن الكريم | جميع الحقوق محفوظة</div>", unsafe_allow_html=True)

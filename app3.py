import streamlit as st
import json
import os
from datetime import datetime
from collections import defaultdict

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
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: bold;
        padding: 10px 20px;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
        text-align: right;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
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
    "الغاشية", "الفجر", "البلد", "الشمس", "القمر", "الرحمن", "النجم", "الرحمن", "الإنسان",
    "الواقعة", "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة",
    "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الإنفطار", "المطففين",
    "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد", "الشمس", "القمر",
    "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر",
    "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص",
    "الفلق", "الناس"
]

BEHAVIORS = {
    "ممتاز": 5,
    "جيد جداً": 4,
    "جيد": 3,
    "متوسط": 2,
    "ضعيف": 1
}

DAYS = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]

class QuranManager:
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
        if name in self.students:
            return False, f"❌ الطالب '{name}' موجود بالفعل!"
        
        self.students[name] = {
            'completed_surahs': [],
            'next_memorization': '',
            'behavior': 'جيد',
            'level': 3,
            'attendance_days': [],
            'notes': [],
            'date_added': datetime.now().isoformat()
        }
        self.save_data()
        return True, f"✅ تم إضافة الطالب '{name}' بنجاح!"
    
    def add_surah(self, name, surah):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if surah in self.students[name]['completed_surahs']:
            return False, f"❌ السورة '{surah}' مسجلة بالفعل!"
        
        self.students[name]['completed_surahs'].append(surah)
        self.save_data()
        return True, f"✅ تم تسجيل سورة '{surah}' للطالب '{name}'!"
    
    def delete_surah(self, name, surah):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if surah not in self.students[name]['completed_surahs']:
            return False, f"❌ السورة '{surah}' غير مسجلة!"
        
        self.students[name]['completed_surahs'].remove(surah)
        self.save_data()
        return True, f"✅ تم حذف سورة '{surah}' من بيانات الطالب '{name}'!"
    
    def set_next_memorization(self, name, surah):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        self.students[name]['next_memorization'] = surah
        self.save_data()
        return True, f"✅ تم تعيين السورة التالية '{surah}' للطالب '{name}'!"
    
    def delete_next_memorization(self, name):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        old_surah = self.students[name]['next_memorization']
        self.students[name]['next_memorization'] = ''
        self.save_data()
        return True, f"✅ تم حذف التحفيظ القادم '{old_surah}'!"
    
    def set_behavior_and_level(self, name, behavior, level):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        self.students[name]['behavior'] = behavior
        self.students[name]['level'] = level
        self.save_data()
        return True, f"✅ تم تحديث السلوك والمستوى للطالب '{name}'!"
    
    def add_attendance_day(self, name, day):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if day in self.students[name]['attendance_days']:
            return False, f"❌ اليوم '{day}' مسجل بالفعل!"
        
        self.students[name]['attendance_days'].append(day)
        self.save_data()
        return True, f"✅ تم إضافة '{day}' لحضور الطالب '{name}'!"
    
    def delete_attendance_day(self, name, day):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if day not in self.students[name]['attendance_days']:
            return False, f"❌ اليوم '{day}' غير مسجل!"
        
        self.students[name]['attendance_days'].remove(day)
        self.save_data()
        return True, f"✅ تم حذف '{day}' من حضور الطالب '{name}'!"
    
    def add_note(self, name, note):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        self.students[name]['notes'].append({
            'content': note,
            'date': datetime.now().isoformat()
        })
        self.save_data()
        return True, f"✅ تم إضافة ملاحظة للطالب '{name}'!"
    
    def delete_note(self, name, note_index):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if note_index >= len(self.students[name]['notes']):
            return False, "❌ الملاحظة غير موجودة!"
        
        self.students[name]['notes'].pop(note_index)
        self.save_data()
        return True, f"✅ تم حذف الملاحظة!"
    
    def remove_student(self, name):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        del self.students[name]
        self.save_data()
        return True, f"✅ تم حذف الطالب '{name}' بنجاح!"
    
    def get_all_students(self):
        return sorted(self.students.keys())
    
    def get_student_data(self, name):
        return self.students.get(name)

# تهيئة المدير
if 'manager' not in st.session_state:
    st.session_state.manager = QuranManager()

manager = st.session_state.manager

# الرأس
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 3em; margin-bottom: 10px;">🕌 نظام إدارة طلاب القرآن</h1>
    <p style="font-size: 1.2em; color: #666;">نظام متقدم لإدارة تحفيظ القرآن الكريم</p>
</div>
""", unsafe_allow_html=True)

# القائمة الجانبية
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    st.markdown("---")
    
    # إحصائيات سريعة
    st.markdown("### 📊 الإحصائيات")
    all_students = manager.get_all_students()
    
    if all_students:
        total_students = len(all_students)
        avg_surahs = sum(len(manager.students[s]['completed_surahs']) for s in all_students) / total_students
        avg_level = sum(manager.students[s]['level'] for s in all_students) / total_students
        completed = sum(1 for s in all_students if len(manager.students[s]['completed_surahs']) >= 114)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 إجمالي الطلاب", total_students)
            st.metric("⭐ متوسط المستوى", f"{avg_level:.1f}")
        with col2:
            st.metric("📖 متوسط السور", f"{avg_surahs:.1f}")
            st.metric("✅ أكملوا", completed)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 لوحة المراقبة",
    "➕ إضافة طالب جديد",
    "📖 السور المحفوظة",
    "📝 التحفيظ القادم",
    "👤 السلوك والمستوى",
    "📅 الحضور والملاحظات",
    "👁️ ملف الطالب",
    "🗑️ حذف طالب"
])

# التبويب 1: لوحة المراقبة
with tab1:
    st.markdown("## 📊 لوحة المراقبة")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    
    if all_students:
        # الإحصائيات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 الطلاب</h3>
                <h1>{}</h1>
            </div>
            """.format(len(all_students)), unsafe_allow_html=True)
        
        with col2:
            avg_surahs = sum(len(manager.students[s]['completed_surahs']) for s in all_students) / len(all_students)
            st.markdown("""
            <div class="metric-card">
                <h3>📖 متوسط السور</h3>
                <h1>{:.1f}</h1>
            </div>
            """.format(avg_surahs), unsafe_allow_html=True)
        
        with col3:
            avg_level = sum(manager.students[s]['level'] for s in all_students) / len(all_students)
            st.markdown("""
            <div class="metric-card">
                <h3>⭐ متوسط المستوى</h3>
                <h1>{:.1f}</h1>
            </div>
            """.format(avg_level), unsafe_allow_html=True)
        
        with col4:
            completed = sum(1 for s in all_students if len(manager.students[s]['completed_surahs']) >= 114)
            st.markdown("""
            <div class="metric-card">
                <h3>✅ أكملوا</h3>
                <h1>{}</h1>
            </div>
            """.format(completed), unsafe_allow_html=True)
        
        # الجدول الملخص
        st.markdown("### 📋 جدول ملخص الطلاب")
        
        table_data = []
        for student_name in all_students:
            student = manager.students[student_name]
            num_surahs = len(student['completed_surahs'])
            remaining = 114 - num_surahs
            percentage = (num_surahs / 114) * 100
            stars = "⭐" * student['level'] + "☆" * (5 - student['level'])
            
            table_data.append({
                "الاسم": student_name,
                "السور المحفوظة": num_surahs,
                "المتبقي": remaining,
                "النسبة": f"{percentage:.1f}%",
                "الحضور": len(student['attendance_days']),
                "السلوك": student['behavior'],
                "المستوى": stars,
                "التحفيظ القادم": student['next_memorization'] or "---"
            })
        
        import pandas as pd
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ لا يوجد طلاب حالياً. أضف طالب جديد للبدء!")

# التبويب 2: إضافة طالب جديد
with tab2:
    st.markdown("## ➕ إضافة طالب جديد")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_student_name = st.text_input("👤 اسم الطالب", placeholder="أدخل اسم الطالب كاملاً...")
    with col2:
        if st.button("✅ إضافة الطالب", key="add_student_btn"):
            if new_student_name:
                success, message = manager.add_student(new_student_name)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("❌ الرجاء إدخال اسم الطالب!")

# التبويب 3: السور المحفوظة
with tab3:
    st.markdown("## 📖 السور المحفوظة")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    
    if all_students:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_student = st.selectbox("👤 اختر الطالب", all_students, key="surah_student")
        
        with col2:
            selected_surah = st.selectbox("📖 اختر السورة", SURAHS, key="add_surah_select")
        
        with col3:
            if st.button("➕ تسجيل السورة", key="add_surah_btn"):
                success, message = manager.add_surah(selected_student, selected_surah)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        # عرض السور المحفوظة
        st.markdown("### 📚 السور المحفوظة للطالب")
        
        student_data = manager.get_student_data(selected_student)
        if student_data['completed_surahs']:
            completed_surahs = student_data['completed_surahs']
            num_surahs = len(completed_surahs)
            percentage = (num_surahs / 114) * 100
            
            st.info(f"عدد السور: {num_surahs} من 114 ({percentage:.1f}%)")
            
            # عرض السور في أعمدة
            col_size = 4
            cols = st.columns(col_size)
            
            for idx, surah in enumerate(completed_surahs):
                with cols[idx % col_size]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"✅ {surah}")
                    with col2:
                        if st.button("🗑️", key=f"delete_surah_{idx}"):
                            success, message = manager.delete_surah(selected_student, surah)
                            if success:
                                st.success(message)
                                st.rerun()
        else:
            st.warning("⚠️ لم يسجل الطالب أي سور حتى الآن!")
    else:
        st.warning("⚠️ لا يوجد طلاب! أضف طالب جديد أولاً.")

# التبويب 4: التحفيظ القادم
with tab4:
    st.markdown("## 📝 التحفيظ القادم")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    
    if all_students:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_student = st.selectbox("👤 اختر الطالب", all_students, key="next_student")
        
        with col2:
            selected_next_surah = st.selectbox("📖 اختر السورة التالية", SURAHS, key="next_surah_select")
        
        with col3:
            if st.button("✅ تعيين التحفيظ", key="set_next_btn"):
                success, message = manager.set_next_memorization(selected_student, selected_next_surah)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        # عرض التحفيظ القادم
        st.markdown("### 📋 التحفيظ القادم للطالب")
        
        student_data = manager.get_student_data(selected_student)
        next_surah = student_data['next_memorization']
        
        if next_surah:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📖 السورة التالية: {next_surah}")
            with col2:
                if st.button("🗑️ حذف", key="delete_next_btn"):
                    success, message = manager.delete_next_memorization(selected_student)
                    if success:
                        st.success(message)
                        st.rerun()
        else:
            st.warning("⚠️ لم يتم تعيين تحفيظ قادم للطالب!")
    else:
        st.warning("⚠️ لا يوجد طلاب! أضف طالب جديد أولاً.")

# التبويب 5: السلوك والمستوى
with tab5:
    st.markdown("## 👤 السلوك والمستوى")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    
    if all_students:
        selected_student = st.selectbox("👤 اختر الطالب", all_students, key="behavior_student")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_data = manager.get_student_data(selected_student)
            current_behavior = student_data['behavior']
            new_behavior = st.radio("💬 السلوك", list(BEHAVIORS.keys()), 
                                    index=list(BEHAVIORS.keys()).index(current_behavior),
                                    key="behavior_radio")
        
        with col2:
            current_level = student_data['level']
            new_level = st.slider("⭐ المستوى", 1, 5, current_level, key="level_slider")
            st.write(f"المستوى: {'⭐' * new_level}{'☆' * (5 - new_level)}")
        
        if st.button("✅ حفظ التقييم", key="save_behavior_btn"):
            success, message = manager.set_behavior_and_level(selected_student, new_behavior, new_level)
            if success:
                st.success(message)
                st.rerun()
    else:
        st.warning("⚠️ لا يوجد طلاب! أضف طالب جديد أولاً.")

# التبويب 6: الحضور والملاحظات
# --- أضف هذه الدالة داخل كلاس QuranManager ---
    def mark_attendance(self, name, date_str):
        if name not in self.students:
            return False, "❌ الطالب غير موجود!"
        
        if date_str in self.students[name]['attendance_days']:
            return False, f"❌ التاريخ '{date_str}' مسجل بالفعل لهذا الطالب!"
        
        self.students[name]['attendance_days'].append(date_str)
        self.save_data()
        return True, f"✅ تم تسجيل حضور الطالب '{name}' بتاريخ {date_str}"

# --- تصحيح التبويب السادس في واجهة Streamlit ---
with tab6:
    st.markdown("## 📅 الحضور والملاحظات")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    if all_students:
        sub_tab1, sub_tab2 = st.tabs(["📅 تسجيل الحضور", "📝 إضافة ملاحظة"])
        
        with sub_tab1:
            col1, col2 = st.columns(2)
            with col1:
                student_att = st.selectbox("🎓 اختر الطالب:", all_students, key="attendance_select")
            with col2:
                att_date = st.date_input("📅 تاريخ الحضور:", key="date_input")
            
            if st.button("✅ تسجيل الحضور", use_container_width=True, key="save_attendance_btn"):
                # تحويل التاريخ إلى نص لتخزينه في JSON
                success, message = manager.mark_attendance(student_att, att_date.strftime('%Y-%m-%d'))
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with sub_tab2:
            col1, col2 = st.columns([3, 1])
            with col1:
                student_note = st.selectbox("🎓 اختر الطالب:", all_students, key="notes_select")
            
            note_text = st.text_area("📝 الملاحظة:", placeholder="أدخل الملاحظة هنا...", key="note_area")
            
            if st.button("✅ إضافة الملاحظة", use_container_width=True, key="save_note_btn"):
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
# التبويب 7: ملف الطالب
with tab7:
    st.markdown("## 👁️ ملف الطالب")
    st.markdown("---")
    
    all_students = manager.get_all_students()
    
    if all_students:
        selected_student = st.selectbox("👤 اختر الطالب", all_students, key="profile_student")
        
        student_data = manager.get_student_data(selected_student)
        
        # معلومات عامة
        st.markdown(f"### 📋 ملف: {selected_student}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            num_surahs = len(student_data['completed_surahs'])
            st.metric("📖 السور المحفوظة", f"{num_surahs}/114")
        
        with col2:
            remaining = 114 - num_surahs
            st.metric("📚 المتبقي", remaining)
        
        with col3:
            percentage = (num_surahs / 114) * 100
            st.metric("📊 النسبة", f"{percentage:.1f}%")
        
        with col4:
            st.metric("⭐ المستوى", "⭐" * student_data['level'])
        
        # السور المحفوظة
        st.markdown("### ✅ السور المحفوظة")
        if student_data['completed_surahs']:
            col_size = 5
            cols = st.columns(col_size)
            for idx, surah in enumerate(student_data['completed_surahs']):
                with cols[idx % col_size]:
                    st.write(f"✅ {surah}")
        else:
            st.info("لم يسجل أي سور بعد")
        
        # التحفيظ القادم
        st.markdown("### 📝 التحفيظ القادم")
        if student_data['next_memorization']:
            st.info(f"📖 {student_data['next_memorization']}")
        else:
            st.info("لم يتم تعيين تحفيظ قادم")
        
        # السلوك والمستوى
        st.markdown("### 👤 السلوك والمستوى")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**السلوك:** {student_data['behavior']}")
        with col2:
            st.write(f"**المستوى:** {'⭐' * student_data['level']}")
        
        # الحضور
        st.markdown("### 📅 الحضور")
        if student_data['attendance_days']:
            st.write(f"**أيام الحضور:** {', '.join(student_data['attendance_days'])}")
            st.write(f"**عدد الأيام:** {len(student_data['attendance_days'])}")
        else:
            st.info("لم يسجل أي حضور بعد")
        
        # الملاحظات
        st.markdown("### 📝 الملاحظات")
        if student_data['notes']:
            for note in student_data['notes']:
                st.write(f"📌 {note['content']} *(التاريخ: {note['date'][:10]})*")
        else:
            st.info("لا توجد ملاحظات حتى الآن")
    else:
        st.warning("⚠️ لا يوجد طلاب! أضف طالب جديد أولاً.")

# التبويب 8: حذف طالب
with tab8:
    st.markdown("## 🗑️ حذف طالب")
    st.markdown("---")
    
    st.warning("⚠️ **تحذير:** هذا الإجراء لا يمكن التراجع عنه! سيتم حذف جميع بيانات الطالب!")
    
    all_students = manager.get_all_students()
    
    if all_students:
        selected_student = st.selectbox("👤 اختر الطالب للحذف", all_students, key="delete_student")
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("🗑️ حذف الطالب", key="delete_student_btn", type="secondary"):
                success, message = manager.remove_student(selected_student)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("ℹ️ لا يوجد طلاب للحذف!")

# الفوتر
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
    <p style="color: #666;">🕌 نظام إدارة طلاب القرآن - جميع الحقوق محفوظة</p>
    <p style="color: #999; font-size: 0.9em;">النسخة 2.0 - محدثة مع 114 سورة</p>
</div>
""", unsafe_allow_html=True) . فقط صحح الحضور

import streamlit as st
import json
import os
from datetime import datetime
from collections import defaultdict

st.set_page_config(
    page_title="🕌 نظام إدارة طلاب القرآن",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 16px; font-weight: bold; padding: 10px 20px; }
    h1, h2, h3 { color: #2c3e50; text-align: right; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 10px; }
    </style>
""", unsafe_allow_html=True)

# ✅ 114 سورة صحيحة بدون تكرار
SURAHS = [
    "الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال",
    "التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء",
    "الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء",
    "النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر",
    "يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية",
    "الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر",
    "الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة",
    "المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج",
    "نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات",
    "عبس","التكوير","الإنفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى",
    "الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق",
    "القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة",
    "الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص",
    "الفلق","الناس"
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
            'attendance_dates': [],
            'notes': [],
            'date_added': datetime.now().isoformat()
        }
        self.save_data()
        return True, f"✅ تم إضافة الطالب '{name}' بنجاح!"

    def add_surah(self, name, surah):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        if surah in self.students[name]['completed_surahs']: return False, f"❌ السورة '{surah}' مسجلة بالفعل!"
        self.students[name]['completed_surahs'].append(surah)
        self.save_data()
        return True, f"✅ تم تسجيل سورة '{surah}'!"

    def delete_surah(self, name, surah):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        if surah not in self.students[name]['completed_surahs']: return False, "❌ السورة غير مسجلة!"
        self.students[name]['completed_surahs'].remove(surah)
        self.save_data()
        return True, f"✅ تم حذف سورة '{surah}'!"

    def set_next_memorization(self, name, surah):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        self.students[name]['next_memorization'] = surah
        self.save_data()
        return True, f"✅ تم تعيين السورة التالية '{surah}'!"

    def delete_next_memorization(self, name):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        old = self.students[name]['next_memorization']
        self.students[name]['next_memorization'] = ''
        self.save_data()
        return True, f"✅ تم حذف التحفيظ القادم '{old}'!"

    def set_behavior_and_level(self, name, behavior, level):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        self.students[name]['behavior'] = behavior
        self.students[name]['level'] = level
        self.save_data()
        return True, f"✅ تم تحديث السلوك والمستوى!"

    # ✅ حضور بتاريخ محدد
    def get_attendance_dates(self, name):
        s = self.students.get(name, {})
        if 'attendance_dates' in s:
            return s['attendance_dates']
        return s.get('attendance_days', [])

    def add_attendance_date(self, name, date_str):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        if 'attendance_dates' not in self.students[name]:
            self.students[name]['attendance_dates'] = self.students[name].get('attendance_days', [])
        if date_str in self.students[name]['attendance_dates']:
            return False, f"❌ التاريخ '{date_str}' مسجل بالفعل!"
        self.students[name]['attendance_dates'].append(date_str)
        self.students[name]['attendance_dates'].sort()
        self.save_data()
        return True, f"✅ تم تسجيل الحضور بتاريخ {date_str}!"

    def delete_attendance_date(self, name, date_str):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        if 'attendance_dates' not in self.students[name]:
            self.students[name]['attendance_dates'] = self.students[name].get('attendance_days', [])
        if date_str not in self.students[name]['attendance_dates']:
            return False, "❌ التاريخ غير مسجل!"
        self.students[name]['attendance_dates'].remove(date_str)
        self.save_data()
        return True, f"✅ تم حذف تاريخ {date_str}!"

    def add_note(self, name, note):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        self.students[name]['notes'].append({'content': note, 'date': datetime.now().isoformat()})
        self.save_data()
        return True, "✅ تم إضافة الملاحظة!"

    def delete_note(self, name, idx):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        if idx >= len(self.students[name]['notes']): return False, "❌ الملاحظة غير موجودة!"
        self.students[name]['notes'].pop(idx)
        self.save_data()
        return True, "✅ تم حذف الملاحظة!"

    def remove_student(self, name):
        if name not in self.students: return False, "❌ الطالب غير موجود!"
        del self.students[name]
        self.save_data()
        return True, f"✅ تم حذف الطالب '{name}'!"

    def get_all_students(self):
        return sorted(self.students.keys())

    def get_student_data(self, name):
        return self.students.get(name)


if 'manager' not in st.session_state:
    st.session_state.manager = QuranManager()
manager = st.session_state.manager

st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 3em;">🕌 نظام إدارة طلاب القرآن</h1>
    <p style="font-size: 1.2em; color: #666;">نظام متقدم لإدارة تحفيظ القرآن الكريم</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ الإعدادات\n---\n### 📊 الإحصائيات")
    all_students = manager.get_all_students()
    if all_students:
        total_students = len(all_students)
        avg_surahs = sum(len(manager.students[s]['completed_surahs']) for s in all_students) / total_students
        avg_level = sum(manager.students[s]['level'] for s in all_students) / total_students
        completed = sum(1 for s in all_students if len(manager.students[s]['completed_surahs']) >= 114)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("👥 الطلاب", total_students)
            st.metric("⭐ متوسط المستوى", f"{avg_level:.1f}")
        with c2:
            st.metric("📖 متوسط السور", f"{avg_surahs:.1f}")
            st.metric("✅ أكملوا", completed)

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
    "📊 لوحة المراقبة","➕ إضافة طالب","📖 السور المحفوظة","📝 التحفيظ القادم",
    "👤 السلوك والمستوى","📅 الحضور والملاحظات","👁️ ملف الطالب","🗑️ حذف طالب"
])

# تبويب 1
with tab1:
    st.markdown("## 📊 لوحة المراقبة\n---")
    all_students = manager.get_all_students()
    if all_students:
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><h3>👥 الطلاب</h3><h1>{len(all_students)}</h1></div>', unsafe_allow_html=True)
        with c2:
            avg = sum(len(manager.students[s]['completed_surahs']) for s in all_students)/len(all_students)
            st.markdown(f'<div class="metric-card"><h3>📖 متوسط السور</h3><h1>{avg:.1f}</h1></div>', unsafe_allow_html=True)
        with c3:
            avgl = sum(manager.students[s]['level'] for s in all_students)/len(all_students)
            st.markdown(f'<div class="metric-card"><h3>⭐ متوسط المستوى</h3><h1>{avgl:.1f}</h1></div>', unsafe_allow_html=True)
        with c4:
            comp = sum(1 for s in all_students if len(manager.students[s]['completed_surahs'])>=114)
            st.markdown(f'<div class="metric-card"><h3>✅ أكملوا</h3><h1>{comp}</h1></div>', unsafe_allow_html=True)

        st.markdown("### 📋 جدول ملخص الطلاب")
        import pandas as pd
        rows = []
        for sn in all_students:
            sd = manager.students[sn]
            ns = len(sd['completed_surahs'])
            att = len(manager.get_attendance_dates(sn))
            rows.append({
                "الاسم": sn, "السور المحفوظة": ns, "المتبقي": 114-ns,
                "النسبة": f"{ns/114*100:.1f}%", "أيام الحضور": att,
                "السلوك": sd['behavior'], "المستوى": "⭐"*sd['level']+"☆"*(5-sd['level']),
                "التحفيظ القادم": sd['next_memorization'] or "---"
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.warning("⚠️ لا يوجد طلاب حالياً.")

# تبويب 2
with tab2:
    st.markdown("## ➕ إضافة طالب جديد\n---")
    c1,c2 = st.columns([3,1])
    with c1: name_in = st.text_input("👤 اسم الطالب", placeholder="أدخل اسم الطالب كاملاً...")
    with c2:
        if st.button("✅ إضافة", key="add_student_btn"):
            if name_in:
                ok,msg = manager.add_student(name_in)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()
            else: st.error("❌ الرجاء إدخال الاسم!")

# تبويب 3
with tab3:
    st.markdown("## 📖 السور المحفوظة\n---")
    all_students = manager.get_all_students()
    if all_students:
        c1,c2,c3 = st.columns(3)
        with c1: sel = st.selectbox("👤 الطالب", all_students, key="surah_student")
        with c2: sur = st.selectbox("📖 السورة", SURAHS, key="add_surah_select")
        with c3:
            if st.button("➕ تسجيل", key="add_surah_btn"):
                ok,msg = manager.add_surah(sel, sur)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()
        st.markdown("### 📚 السور المحفوظة")
        sd = manager.get_student_data(sel)
        if sd['completed_surahs']:
            ns = len(sd['completed_surahs'])
            st.info(f"عدد السور: {ns} من 114 ({ns/114*100:.1f}%)")
            cols = st.columns(4)
            for i,s in enumerate(sd['completed_surahs']):
                with cols[i%4]:
                    ca,cb = st.columns([3,1])
                    with ca: st.write(f"✅ {s}")
                    with cb:
                        if st.button("🗑️", key=f"ds_{i}"):
                            ok,msg = manager.delete_surah(sel,s)
                            (st.success if ok else st.error)(msg)
                            if ok: st.rerun()
        else: st.warning("⚠️ لم يسجل الطالب أي سور!")
    else: st.warning("⚠️ لا يوجد طلاب!")

# تبويب 4
with tab4:
    st.markdown("## 📝 التحفيظ القادم\n---")
    all_students = manager.get_all_students()
    if all_students:
        c1,c2,c3 = st.columns(3)
        with c1: sel = st.selectbox("👤 الطالب", all_students, key="next_student")
        with c2: ns = st.selectbox("📖 السورة التالية", SURAHS, key="next_surah_select")
        with c3:
            if st.button("✅ تعيين", key="set_next_btn"):
                ok,msg = manager.set_next_memorization(sel,ns)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()
        sd = manager.get_student_data(sel)
        nxt = sd['next_memorization']
        if nxt:
            c1,c2 = st.columns([3,1])
            with c1: st.info(f"📖 السورة التالية: {nxt}")
            with c2:
                if st.button("🗑️ حذف", key="del_next"):
                    ok,msg = manager.delete_next_memorization(sel)
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()
        else: st.warning("⚠️ لم يتم تعيين تحفيظ قادم!")
    else: st.warning("⚠️ لا يوجد طلاب!")

# تبويب 5
with tab5:
    st.markdown("## 👤 السلوك والمستوى\n---")
    all_students = manager.get_all_students()
    if all_students:
        sel = st.selectbox("👤 الطالب", all_students, key="behavior_student")
        sd = manager.get_student_data(sel)
        c1,c2 = st.columns(2)
        with c1:
            beh = st.radio("💬 السلوك", list(BEHAVIORS.keys()), index=list(BEHAVIORS.keys()).index(sd['behavior']), key="behavior_radio")
        with c2:
            lvl = st.slider("⭐ المستوى", 1, 5, sd['level'], key="level_slider")
            st.write(f"{'⭐'*lvl}{'☆'*(5-lvl)}")
        if st.button("✅ حفظ التقييم"):
            ok,msg = manager.set_behavior_and_level(sel,beh,lvl)
            (st.success if ok else st.error)(msg)
            if ok: st.rerun()
    else: st.warning("⚠️ لا يوجد طلاب!")

# ✅ تبويب 6: الحضور بالتاريخ
with tab6:
    st.markdown("## 📅 الحضور والملاحظات\n---")
    all_students = manager.get_all_students()
    if all_students:
        sel = st.selectbox("👤 الطالب", all_students, key="attendance_student")
        st.markdown("### 📅 تسجيل الحضور بالتاريخ")
        c1,c2 = st.columns([2,1])
        with c1:
            sel_date = st.date_input("📆 اختر التاريخ", value=datetime.today(), key="date_input")
        with c2:
            if st.button("➕ تسجيل الحضور", key="add_att_btn"):
                date_str = sel_date.strftime("%Y-%m-%d")
                ok,msg = manager.add_attendance_date(sel, date_str)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()

        dates = manager.get_attendance_dates(sel)
        if dates:
            # ✅ حساب عدد أيام الحضور
            st.info(f"📊 إجمالي أيام الحضور: **{len(dates)} يوم**")
            cols = st.columns(3)
            for i, ds in enumerate(sorted(dates, reverse=True)):
                with cols[i%3]:
                    ca,cb = st.columns([3,1])
                    with ca:
                        try: display = datetime.strptime(ds,"%Y-%m-%d").strftime("%d / %m / %Y")
                        except: display = ds
                        st.write(f"✅ {display}")
                    with cb:
                        if st.button("🗑️", key=f"dd_{i}"):
                            ok,msg = manager.delete_attendance_date(sel, ds)
                            (st.success if ok else st.error)(msg)
                            if ok: st.rerun()
        else:
            st.warning("⚠️ لم يسجل الطالب أي حضور حتى الآن!")

        st.markdown("---\n### 📝 الملاحظات")
        c1,c2 = st.columns([3,1])
        with c1: note_in = st.text_area("اكتب ملاحظة", placeholder="أدخل ملاحظتك هنا...")
        with c2:
            if st.button("➕ إضافة الملاحظة", key="add_note_btn"):
                if note_in:
                    ok,msg = manager.add_note(sel, note_in)
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()
                else: st.error("❌ الملاحظة فارغة!")
        sd = manager.get_student_data(sel)
        for i,n in enumerate(sd['notes']):
            with st.expander(f"📝 ملاحظة - {n['date'][:10]}"):
                ca,cb = st.columns([4,1])
                with ca: st.write(n['content'])
                with cb:
                    if st.button("🗑️", key=f"dn_{i}"):
                        ok,msg = manager.delete_note(sel,i)
                        (st.success if ok else st.error)(msg)
                        if ok: st.rerun()
    else: st.warning("⚠️ لا يوجد طلاب!")

# تبويب 7
with tab7:
    st.markdown("## 👁️ ملف الطالب\n---")
    all_students = manager.get_all_students()
    if all_students:
        sel = st.selectbox("👤 الطالب", all_students, key="profile_student")
        sd = manager.get_student_data(sel)
        dates = manager.get_attendance_dates(sel)
        st.markdown(f"### 📋 ملف: {sel}")
        ns = len(sd['completed_surahs'])
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("📖 السور", f"{ns}/114")
        with c2: st.metric("📚 المتبقي", 114-ns)
        with c3: st.metric("📊 النسبة", f"{ns/114*100:.1f}%")
        with c4: st.metric("⭐ المستوى", "⭐"*sd['level'])

        st.markdown("### ✅ السور المحفوظة")
        if sd['completed_surahs']:
            cols = st.columns(5)
            for i,s in enumerate(sd['completed_surahs']):
                with cols[i%5]: st.write(f"✅ {s}")
        else: st.info("لم يسجل أي سور بعد")

        st.markdown("### 📝 التحفيظ القادم")
        st.info(f"📖 {sd['next_memorization']}") if sd['next_memorization'] else st.info("لم يتم تعيين تحفيظ قادم")

        st.markdown("### 👤 السلوك والمستوى")
        c1,c2 = st.columns(2)
        with c1: st.write(f"**السلوك:** {sd['behavior']}")
        with c2: st.write(f"**المستوى:** {'⭐'*sd['level']}")

        # ✅ الحضور بالتواريخ وعدد الأيام
        st.markdown("### 📅 الحضور")
        if dates:
            st.metric("📊 إجمالي أيام الحضور", f"{len(dates)} يوم")
            fmt = []
            for d in sorted(dates):
                try: fmt.append(datetime.strptime(d,"%Y-%m-%d").strftime("%d/%m/%Y"))
                except: fmt.append(d)
            st.write(f"**التواريخ:** {' — '.join(fmt)}")
        else: st.info("لم يسجل أي حضور بعد")

        st.markdown("### 📝 الملاحظات")
        if sd['notes']:
            for n in sd['notes']: st.write(f"📌 {n['content']} *(التاريخ: {n['date'][:10]})*")
        else: st.info("لا توجد ملاحظات")
    else: st.warning("⚠️ لا يوجد طلاب!")

# تبويب 8
with tab8:
    st.markdown("## 🗑️ حذف طالب\n---")
    st.warning("⚠️ **تحذير:** لا يمكن التراجع عن الحذف!")
    all_students = manager.get_all_students()
    if all_students:
        sel = st.selectbox("👤 الطالب للحذف", all_students, key="delete_student")
        _,c2,_ = st.columns(3)
        with c2:
            if st.button("🗑️ حذف الطالب", key="del_student_btn", type="secondary"):
                ok,msg = manager.remove_student(sel)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()
    else: st.info("ℹ️ لا يوجد طلاب للحذف!")

st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:20px; background:#f8f9fa; border-radius:10px;">
    <p style="color:#666;">🕌 نظام إدارة طلاب القرآن</p>
    <p style="color:#999; font-size:0.9em;">النسخة 2.1 — 114 سورة صحيحة + حضور بالتاريخ</p>
</div>
""", unsafe_allow_html=True)

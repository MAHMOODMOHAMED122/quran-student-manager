import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="🕌 Quran School Manager",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

class QuranSchoolManager:
    """Manages Quran school student records and progress."""
    
    def __init__(self, filename='students_data.json'):
        self.filename = filename
        self.students = self.load_data()
        self.total_parts = 30
    
    def load_data(self):
        """Load students data from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save students data to JSON file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, indent=2, ensure_ascii=False)
    
    def add_student(self, name, total_parts=30):
        """Add a new student to the system."""
        if name.lower() in [s.lower() for s in self.students]:
            return False, f"❌ Student '{name}' already exists!"
        
        self.students[name] = {
            'total_parts': total_parts,
            'current_part': 0,
            'attendance': [],
            'notes': [],
            'role': 'Student',
            'date_added': datetime.now().isoformat()
        }
        self.save_data()
        return True, f"✅ Student '{name}' added successfully!"
    
    def mark_attendance(self, name, date=None):
        """Mark student attendance."""
        student = self._find_student(name)
        if not student:
            return False, f"❌ Student '{name}' not found."
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date in student['attendance']:
            return False, f"⚠️ {name} already marked present on {date}"
        
        student['attendance'].append(date)
        self.save_data()
        return True, f"✅ {name} marked present on {date}"
    
    def update_progress(self, name, new_part):
        """Update student's current part and check for role upgrade."""
        student = self._find_student(name)
        if not student:
            return False, f"❌ Student '{name}' not found."
        
        try:
            new_part = int(new_part)
        except:
            return False, "❌ Invalid part number."
        
        if new_part < 0 or new_part > student['total_parts']:
            return False, f"❌ Invalid part number. Must be between 0 and {student['total_parts']}"
        
        old_part = student['current_part']
        student['current_part'] = new_part
        
        message = f"✅ {name}'s progress updated: Part {old_part}→{new_part}/{student['total_parts']}"
        
        remaining = student['total_parts'] - new_part
        if remaining <= 2 and student['role'] == 'Student':
            student['role'] = 'Junior Assistant'
            message += f"\n🎉 {name} auto-upgraded to 'Junior Assistant'! (Only {remaining} parts left!)"
        
        self.save_data()
        return True, message
    
    def assign_role(self, name, role):
        """Assign a custom role to student."""
        student = self._find_student(name)
        if not student:
            return False, f"❌ Student '{name}' not found."
        
        valid_roles = ['Student', 'Junior Assistant', 'Group Leader', 'Prayer Monitor', 'Recitation Assistant']
        if role not in valid_roles:
            return False, f"❌ Invalid role. Choose from: {', '.join(valid_roles)}"
        
        old_role = student['role']
        student['role'] = role
        self.save_data()
        return True, f"✅ {name}'s role updated: {old_role} → {role}"
    
    def add_note(self, name, note_type, content):
        """Add a note about student's performance."""
        student = self._find_student(name)
        if not student:
            return False, f"❌ Student '{name}' not found."
        
        valid_types = ['Strengths', 'Modification', 'General', 'Attendance', 'Behavior']
        if note_type not in valid_types:
            return False, f"❌ Invalid note type. Choose from: {', '.join(valid_types)}"
        
        note = {
            'type': note_type,
            'content': content,
            'date': datetime.now().isoformat()
        }
        
        student['notes'].append(note)
        if len(student['notes']) > 10:
            student['notes'] = student['notes'][-10:]
        
        self.save_data()
        return True, f"✅ Note added for {name} ({note_type})"
    
    def view_profile(self, name):
        """Get student profile data."""
        student = self._find_student(name)
        if not student:
            return None
        
        remaining = student['total_parts'] - student['current_part']
        progress_pct = (student['current_part'] / student['total_parts']) * 100
        
        return {
            'name': name,
            'role': student['role'],
            'current_part': student['current_part'],
            'total_parts': student['total_parts'],
            'remaining': remaining,
            'progress': f"{progress_pct:.1f}",
            'attendance_count': len(student['attendance']),
            'date_added': student['date_added'][:10],
            'attendance': sorted(student['attendance'], reverse=True)[:5],
            'notes': student['notes'][-10:] if student['notes'] else []
        }
    
    def get_summary(self):
        """Get summary data for all students."""
        if not self.students:
            return []
        
        data = []
        for name, student in sorted(self.students.items()):
            current = student['current_part']
            total = student['total_parts']
            remaining = total - current
            progress = (current / total) * 100
            attendance = len(student['attendance'])
            role = student['role']
            
            data.append({
                'Name': name,
                'Current': current,
                'Total': total,
                'Remaining': remaining,
                'Progress %': f"{progress:.1f}",
                'Attendance': attendance,
                'Role': role
            })
        
        return data
    
    def get_statistics(self):
        """Get overall statistics."""
        if not self.students:
            return {
                'total_students': 0,
                'avg_progress': 0,
                'completed': 0,
                'junior_assistants': 0
            }
        
        total_students = len(self.students)
        avg_progress = sum(
            (s['current_part'] / s['total_parts']) * 100 
            for s in self.students.values()
        ) / total_students
        completed = sum(1 for s in self.students.values() if s['current_part'] >= s['total_parts'])
        junior_assistants = sum(1 for s in self.students.values() if s['role'] == 'Junior Assistant')
        
        return {
            'total_students': total_students,
            'avg_progress': f"{avg_progress:.1f}",
            'completed': completed,
            'junior_assistants': junior_assistants
        }
    
    def remove_student(self, name):
        """Remove student from system."""
        for key in list(self.students.keys()):
            if key.lower() == name.lower():
                del self.students[key]
                self.save_data()
                return True, f"✅ Student '{key}' removed successfully."
        return False, f"❌ Student '{name}' not found."
    
    def get_all_students(self):
        """Get list of all student names."""
        return sorted(self.students.keys())
    
    def _find_student(self, name):
        """Find student by case-insensitive name."""
        for key, value in self.students.items():
            if key.lower() == name.lower():
                return value
        return None


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = QuranSchoolManager()

manager = st.session_state.manager

# Header
st.markdown("# 🕌 Quran School Management System")
st.markdown("**Professional Student Management System for Quran Memorization**")
st.divider()

# Main Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Dashboard",
    "➕ Add Student",
    "📅 Attendance",
    "📈 Progress",
    "🎯 Roles",
    "📝 Notes",
    "👤 Profile",
    "🗑️ Remove"
])

# TAB 1: Dashboard
with tab1:
    st.subheader("📊 Dashboard Summary")
    
    stats = manager.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", stats['total_students'])
    with col2:
        st.metric("Average Progress", f"{stats['avg_progress']}%")
    with col3:
        st.metric("Completed", stats['completed'])
    with col4:
        st.metric("Junior Assistants", stats['junior_assistants'])
    
    st.divider()
    
    summary_data = manager.get_summary()
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📌 No students yet. Add a student to get started!")

# TAB 2: Add Student
with tab2:
    st.subheader("➕ Add New Student")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Student Name", placeholder="Enter student name", key="add_name")
    with col2:
        total_parts = st.number_input("Total Parts", value=30, min_value=1, key="add_parts")
    
    if st.button("Add Student", type="primary", use_container_width=True):
        if name:
            success, message = manager.add_student(name, total_parts)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("❌ Please enter a student name")

# TAB 3: Attendance
with tab3:
    st.subheader("📅 Mark Attendance")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_student = st.selectbox("Select Student", students, key="att_student")
        with col2:
            att_date = st.date_input("Date (leave for today)", key="att_date")
        
        if st.button("Mark Present", type="primary", use_container_width=True):
            date_str = att_date.strftime('%Y-%m-%d')
            success, message = manager.mark_attendance(selected_student, date_str)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.warning(message)
    else:
        st.info("📌 No students yet. Add a student first!")

# TAB 4: Progress
with tab4:
    st.subheader("📈 Update Progress")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns([2, 1])
        with col1:
            prog_student = st.selectbox("Select Student", students, key="prog_student")
        with col2:
            new_part = st.number_input("Current Part", value=0, min_value=0, max_value=30, key="prog_part")
        
        if st.button("Update Progress", type="primary", use_container_width=True):
            success, message = manager.update_progress(prog_student, new_part)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("📌 No students yet. Add a student first!")

# TAB 5: Roles
with tab5:
    st.subheader("🎯 Assign Role")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns(2)
        with col1:
            role_student = st.selectbox("Select Student", students, key="role_student")
        with col2:
            role = st.selectbox(
                "Select Role",
                ["Student", "Junior Assistant", "Group Leader", "Prayer Monitor", "Recitation Assistant"],
                key="role_select"
            )
        
        if st.button("Assign Role", type="primary", use_container_width=True):
            success, message = manager.assign_role(role_student, role)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("📌 No students yet. Add a student first!")

# TAB 6: Notes
with tab6:
    st.subheader("📝 Add Note")
    
    students = manager.get_all_students()
    if students:
        col1, col2 = st.columns(2)
        with col1:
            note_student = st.selectbox("Select Student", students, key="note_student")
        with col2:
            note_type = st.selectbox(
                "Note Type",
                ["Strengths", "Modification", "General", "Attendance", "Behavior"],
                key="note_type"
            )
        
        note_content = st.text_area("Note Content", placeholder="Enter your observation...", key="note_content")
        
        if st.button("Add Note", type="primary", use_container_width=True):
            if note_content:
                success, message = manager.add_note(note_student, note_type, note_content)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("❌ Please enter note content")
    else:
        st.info("📌 No students yet. Add a student first!")

# TAB 7: Profile
with tab7:
    st.subheader("👤 View Profile")
    
    students = manager.get_all_students()
    if students:
        profile_student = st.selectbox("Select Student", students, key="profile_student")
        
        if st.button("Load Profile", type="primary", use_container_width=True):
            profile = manager.view_profile(profile_student)
            if profile:
                # Profile header
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Role", profile['role'])
                with col2:
                    st.metric("Current/Total", f"{profile['current_part']}/{profile['total_parts']}")
                with col3:
                    st.metric("Remaining", profile['remaining'])
                with col4:
                    st.metric("Progress", f"{profile['progress']}%")
                
                # Progress bar
                progress = float(profile['progress']) / 100
                st.progress(progress, text=f"{profile['progress']}%")
                
                # Attendance
                st.subheader("📅 Recent Attendance")
                if profile['attendance']:
                    for date in profile['attendance']:
                        st.write(f"✓ {date}")
                else:
                    st.info("No attendance recorded")
                
                # Notes
                if profile['notes']:
                    st.subheader("📝 Recent Notes")
                    for note in profile['notes']:
                        date = note['date'][:10]
                        with st.expander(f"[{date}] {note['type']}"):
                            st.write(note['content'])
    else:
        st.info("📌 No students yet. Add a student first!")

# TAB 8: Remove Student
with tab8:
    st.subheader("🗑️ Remove Student")
    
    students = manager.get_all_students()
    if students:
        remove_student = st.selectbox("Select Student to Remove", students, key="remove_student")
        
        if st.button("Remove Student", type="secondary", use_container_width=True):
            success, message = manager.remove_student(remove_student)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("📌 No students to remove.")

# Footer
st.divider()
st.markdown("**🕌 Quran School Management System** | All data is automatically saved | Made for Quran educators")

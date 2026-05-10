from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

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
                'name': name,
                'current': current,
                'total': total,
                'remaining': remaining,
                'progress': f"{progress:.1f}",
                'attendance': attendance,
                'role': role
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


# Initialize manager
manager = QuranSchoolManager()


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all student names."""
    return jsonify(manager.get_all_students())


@app.route('/api/add-student', methods=['POST'])
def add_student():
    """Add a new student."""
    data = request.json
    name = data.get('name', '').strip()
    total_parts = int(data.get('total_parts', 30))
    
    success, message = manager.add_student(name, total_parts)
    return jsonify({'success': success, 'message': message})


@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    """Mark attendance."""
    data = request.json
    name = data.get('name', '').strip()
    date = data.get('date', None)
    
    success, message = manager.mark_attendance(name, date)
    return jsonify({'success': success, 'message': message})


@app.route('/api/update-progress', methods=['POST'])
def update_progress():
    """Update student progress."""
    data = request.json
    name = data.get('name', '').strip()
    new_part = data.get('new_part', 0)
    
    success, message = manager.update_progress(name, new_part)
    return jsonify({'success': success, 'message': message})


@app.route('/api/assign-role', methods=['POST'])
def assign_role():
    """Assign a role."""
    data = request.json
    name = data.get('name', '').strip()
    role = data.get('role', '').strip()
    
    success, message = manager.assign_role(name, role)
    return jsonify({'success': success, 'message': message})


@app.route('/api/add-note', methods=['POST'])
def add_note():
    """Add a note."""
    data = request.json
    name = data.get('name', '').strip()
    note_type = data.get('note_type', '').strip()
    content = data.get('content', '').strip()
    
    success, message = manager.add_note(name, note_type, content)
    return jsonify({'success': success, 'message': message})


@app.route('/api/profile/<name>', methods=['GET'])
def get_profile(name):
    """Get student profile."""
    profile = manager.view_profile(name)
    if profile:
        return jsonify(profile)
    return jsonify({'error': 'Student not found'}), 404


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary data."""
    data = manager.get_summary()
    stats = manager.get_statistics()
    return jsonify({'students': data, 'statistics': stats})


@app.route('/api/remove-student', methods=['POST'])
def remove_student():
    """Remove a student."""
    data = request.json
    name = data.get('name', '').strip()
    
    success, message = manager.remove_student(name)
    return jsonify({'success': success, 'message': message})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

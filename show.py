"""
برنامج توليد الإحصائيات والتقارير
Statistics and Reports Generator
"""

import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io

class StatisticsGenerator:
    def __init__(self, data_file='students_data.json'):
        self.data_file = data_file
        self.students = self.load_data()
        self.surahs = self.get_all_surahs()
    
    def load_data(self):
        """تحميل البيانات من ملف JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def get_all_surahs(self):
        """قائمة جميع السور"""
        return {
            1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
            6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
            11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
            16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
            21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
            26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
            31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
            36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
            41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
            46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
            51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
            56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
            61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
            66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
            71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
            76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
            81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
            86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
            91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
            96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
            101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
            106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
            111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
        }
    
    def generate_student_image(self, student_name, output_path='reports/images/'):
        """توليد صورة تقرير الطالب"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        if student_name not in self.students:
            return None
        
        student = self.students[student_name]
        completed = len(student['completed_surahs'])
        percentage = (completed / 114) * 100
        remaining = 114 - completed
        
        # إنشاء صورة
        width, height = 1080, 1350
        background_color = (240, 248, 255)  # Alice Blue
        image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(image)
        
        # محاولة تحميل خطوط
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # الألوان
        primary_color = (102, 126, 234)  # Purple
        secondary_color = (118, 75, 162)  # Dark Purple
        text_color = (44, 62, 80)  # Dark Blue
        
        # رسم رأس الصورة
        draw.rectangle([(0, 0), (width, 150)], fill=primary_color)
        draw.text((width // 2, 40), "📊 تقرير الطالب", font=title_font, fill=(255, 255, 255), anchor="mm")
        
        # اسم الطالب
        draw.text((width // 2, 180), student_name, font=header_font, fill=text_color, anchor="mm")
        
        y_position = 250
        line_spacing = 90
        
        # السور المحفوظة
        draw.text((100, y_position), "السور المحفوظة:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), f"{completed}/114", font=header_font, fill=primary_color, anchor="rm")
        
        # شريط التقدم
        bar_width = 800
        bar_height = 20
        bar_x = 100
        bar_y = y_position + 50
        
        filled_width = int((bar_width * completed) / 114)
        draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)], 
                      outline=secondary_color, width=2, fill=(220, 220, 220))
        if filled_width > 0:
            draw.rectangle([(bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height)], 
                          fill=primary_color)
        
        draw.text((bar_x + bar_width / 2, bar_y + bar_height + 15), f"{percentage:.1f}%", 
                 font=text_font, fill=text_color, anchor="mm")
        
        y_position += line_spacing * 1.5
        
        # المتبقي
        draw.text((100, y_position), "المتبقي:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), f"{remaining} سورة", font=header_font, fill=(231, 76, 60), anchor="rm")
        
        y_position += line_spacing
        
        # السلوك
        behavior = student.get('behavior', 'جيد')
        draw.text((100, y_position), "السلوك:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), behavior, font=header_font, fill=(46, 204, 113), anchor="rm")
        
        y_position += line_spacing
        
        # المستوى
        level = student.get('level', 3)
        stars = "⭐" * level + "☆" * (5 - level)
        draw.text((100, y_position), "المستوى:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), stars, font=header_font, fill=(241, 196, 15), anchor="rm")
        
        y_position += line_spacing
        
        # الحضور
        attendance = len(student.get('attendance_days', []))
        draw.text((100, y_position), "أيام الحضور:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), f"{attendance} أيام", font=header_font, fill=(52, 152, 219), anchor="rm")
        
        y_position += line_spacing
        
        # التحفيظ القادم
        next_surah = student.get('next_memorization', '')
        next_surah_name = self.surahs.get(next_surah, "لم يتم التحديد") if next_surah else "لم يتم التحديد"
        draw.text((100, y_position), "التحفيظ القادم:", font=text_font, fill=secondary_color)
        draw.text((900, y_position), next_surah_name, font=text_font, fill=primary_color, anchor="rm")
        
        # التاريخ والتوقيع
        y_position = height - 80
        today = datetime.now().strftime('%Y-%m-%d')
        draw.text((width // 2, y_position), today, font=small_font, fill=(155, 155, 155), anchor="mm")
        draw.text((width // 2, y_position + 45), "🕌 نظام إدارة طلاب القرآن", 
                 font=small_font, fill=(102, 126, 234), anchor="mm")
        
        # حفظ الصورة
        filename = f"{output_path}{student_name}_report.png"
        image.save(filename)
        return filename
    
    def generate_all_students_images(self, output_path='reports/images/'):
        """توليد صور لجميع الطلاب"""
        results = []
        for student_name in self.students.keys():
            result = self.generate_student_image(student_name, output_path)
            if result:
                results.append(result)
        return results
    
    def generate_pdf_report(self, student_name=None, output_path='reports/pdf/'):
        """توليد تقرير PDF"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        if student_name and student_name in self.students:
            # تقرير طالب واحد
            students_to_report = {student_name: self.students[student_name]}
            filename = f"{output_path}{student_name}_report.pdf"
        else:
            # تقرير جميع الطلاب
            students_to_report = self.students
            filename = f"{output_path}all_students_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, 
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # عنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # وسط
        )
        
        story.append(Paragraph("📊 تقرير الطلاب", title_style))
        story.append(Paragraph(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # إنشاء جدول
        table_data = [['الاسم', 'السور المحفوظة', 'النسبة', 'السلوك', 'المستوى', 'الحضور', 'التحفيظ القادم']]
        
        for name, student in sorted(students_to_report.items()):
            completed = len(student['completed_surahs'])
            percentage = f"{(completed/114)*100:.1f}%"
            attendance = len(student.get('attendance_days', []))
            next_surah = self.surahs.get(student.get('next_memorization'), "---") if student.get('next_memorization') else "---"
            level = "⭐" * student.get('level', 3)
            
            table_data.append([
                name,
                f"{completed}/114",
                percentage,
                student.get('behavior', '---'),
                level,
                f"{attendance}",
                next_surah
            ])
        
        # إنشاء الجدول
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        story.append(table)
        
        doc.build(story)
        return filename
    
    def generate_excel_report(self, output_path='reports/excel/'):
        """توليد تقرير Excel"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        data = []
        for name, student in sorted(self.students.items()):
            completed = len(student['completed_surahs'])
            percentage = (completed / 114) * 100
            next_surah = self.surahs.get(student.get('next_memorization'), "---") if student.get('next_memorization') else "---"
            level = student.get('level', 3)
            attendance = len(student.get('attendance_days', []))
            
            data.append({
                'الاسم': name,
                'السور المحفوظة': completed,
                'المتبقي': 114 - completed,
                'النسبة المئوية': f"{percentage:.1f}%",
                'السلوك': student.get('behavior', '---'),
                'المستوى': level,
                'الحضور': attendance,
                'التحفيظ القادم': next_surah,
                'تاريخ الإضافة': student.get('date_added', '---')[:10]
            })
        
        df = pd.DataFrame(data)
        filename = f"{output_path}students_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='الطلاب', index=False)
            
            # تنسيق الورقة
            worksheet = writer.sheets['الطلاب']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filename
    
    def get_statistics_summary(self):
        """الحصول على ملخص الإحصائيات"""
        if not self.students:
            return {}
        
        total = len(self.students)
        avg_surahs = sum(len(s['completed_surahs']) for s in self.students.values()) / total
        avg_level = sum(s.get('level', 3) for s in self.students.values()) / total
        completed_all = sum(1 for s in self.students.values() if len(s['completed_surahs']) >= 114)
        
        return {
            'إجمالي الطلاب': total,
            'متوسط السور': f"{avg_surahs:.1f}",
            'متوسط المستوى': f"{avg_level:.1f}",
            'أكملوا القرآن': completed_all,
            'تاريخ التقرير': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# استخدام البرنامج
if __name__ == "__main__":
    generator = StatisticsGenerator()
    
    print("🕌 برنامج توليد الإحصائيات والتقارير")
    print("=" * 50)
    
    # توليد الصور
    print("\n📸 توليد الصور...")
    images = generator.generate_all_students_images()
    print(f"✅ تم توليد {len(images)} صورة")
    for img in images:
        print(f"   📁 {img}")
    
    # توليد PDF
    print("\n📄 توليد تقرير PDF...")
    pdf_file = generator.generate_pdf_report()
    print(f"✅ {pdf_file}")
    
    # توليد Excel
    print("\n📊 توليد ملف Excel...")
    excel_file = generator.generate_excel_report()
    print(f"✅ {excel_file}")
    
    # الإحصائيات
    print("\n📈 الإحصائيات:")
    stats = generator.get_statistics_summary()
    for key, value in stats.items():
        print(f"   {key}: {value}")

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import StudentStatusUpdate, Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

@admin.register(Tawassut)
class TawassutAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')

@admin.register(Kafeel)
class KafeelAdmin(admin.ModelAdmin):
    actions = ['get_students_action']

    def get_students_action(self, request, queryset):
        for kafeel in queryset:
            student_list = Student.objects.filter(kafeel=kafeel, status='Active')

            if student_list.exists():
                message = f"Students connected/sponsored by {kafeel.name}:\n"
                for student in student_list:
                    message += f"{student.name}, "

                self.message_user(request, message)
            else:
                self.message_user(request, f"No active students connected/sponsored by {kafeel.name}.")

        return HttpResponseRedirect(request.get_full_path())

    get_students_action.short_description = "Get Students"

    list_display = ('number', 'name', 'phone', 'address', 'tawassut_link', 'status')

    def tawassut_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:kifalat_tawassut_change', args=[obj.tawassut.id]), obj.tawassut)
    tawassut_link.short_description = 'Tawassut'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'name', 'father_name', 'phone', 'course', 'class_field', 'section', 'kafeel_link', 'sponsoring_since', 'status')
    list_filter = ('course', 'class_field', 'section', 'kafeel', 'kafeel__tawassut', 'status')
    search_fields = ('name', 'father_name', 'phone')

    def kafeel_link(self, obj):
        if obj.kafeel:
            return format_html('<a href="{}">{}</a>', reverse('admin:kifalat_kafeel_change', args=[obj.kafeel.number]), obj.kafeel)
        else:
            return None

    kafeel_link.short_description = 'Kafeel'

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('kafeel', 'student', 'receipt_number', 'amount_paid', 'study_report', 'paid_date')
    list_filter = ('kafeel', 'student__status', 'student__course', 'student__class_field', 'student__section', 'paid_date')
    search_fields = ('receipt_number', 'study_report')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "kafeel":
            kwargs["queryset"] = Kafeel.objects.filter(status='Active')
        elif db_field.name == "student":
            kafeel_id = request.GET.get('kafeel') or request.POST.get('kafeel')
            if kafeel_id:
                kwargs["queryset"] = Student.objects.filter(kafeel__number=kafeel_id, status='Active')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.kafeel.status != 'Active':
            raise ValidationError("Cannot proceed. Selected Kafeel is inactive.")

        if obj.student.status != 'Active':
            raise ValidationError("Cannot proceed. Selected Student is inactive.")

        super().save_model(request, obj, form, change)

@admin.register(KafeelStatusUpdate)
class KafeelStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('kafeel_number', 'get_kafeel_name', 'status', 'updated_at')
    search_fields = ('kafeel_number',)
    list_filter = ('status', 'updated_at')

    def get_kafeel_name(self, obj):
        try:
            kafeel = Kafeel.objects.get(number=obj.kafeel_number)
            return kafeel.name
        except Kafeel.DoesNotExist:
            return "Kafeel not found"

    get_kafeel_name.short_description = 'Kafeel Name'

@admin.register(StudentStatusUpdate)
class StudentStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'status', 'updated_at')
    search_fields = ('admission_number',)
    list_filter = ('status', 'updated_at')

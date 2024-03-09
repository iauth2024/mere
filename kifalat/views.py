# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import StudentStatusUpdate, Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate
from .forms import ProgressForm, KafeelStatusUpdateForm
from kifalat import models


def home(request):
    return render(request, 'home.html')

def student_details(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    progress = Progress.objects.filter(student=student)

    total_paid = progress.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0.0
    total_fees = student.total_fees or 0.0
    due_amount = total_fees - total_paid

    context = {'student': student, 'progress': progress, 'total_paid': total_paid, 'total_fees': total_fees, 'due_amount': due_amount}
    return render(request, 'student_details.html', context)

def progress_form(request, kafeel_id, admission_number):
    kafeel = get_object_or_404(Kafeel, number=kafeel_id)
    student = get_object_or_404(Student, admission_number=admission_number)

    if request.method == 'POST':
        form = ProgressForm(request.POST)
        form.fields['student'].queryset = Student.objects.filter(kafeel=kafeel, status='Active')
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Progress data saved successfully!')
                return redirect('progress_form', kafeel_id=kafeel_id, admission_number=admission_number)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ProgressForm(initial={'kafeel': kafeel, 'student': student})
        form.fields['student'].queryset = Student.objects.filter(kafeel=kafeel, status='Active')

    context = {'kafeel': kafeel, 'student': student, 'form': form}
    return render(request, 'progress_form.html', context)

def kafeel_status_update(request):
    if request.method == 'POST':
        form = KafeelStatusUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kafeel status updated successfully.')
            return redirect('kafeel_status_update')
        else:
            messages.error(request, 'Error updating Kafeel status. Please check the form data.')
    else:
        form = KafeelStatusUpdateForm()

    context = {'form': form}
    return render(request, 'kafeel_status_update.html', context)
from django.shortcuts import render

from django.db.models import Sum
from decimal import Decimal

# ... (other imports)

def sponsor_dashboard(request, kafeel_id):
    if request.method == 'POST':
        entered_number = request.POST.get('kafeel_number')
        entered_phone = request.POST.get('kafeel_phone')

        try:
            entered_number = int(entered_number)
            entered_phone = int(entered_phone)
            kafeel = get_object_or_404(Kafeel, number=entered_number, phone=entered_phone)
            dashboard_data = Student.objects.filter(kafeel=kafeel, sponsoring_since__isnull=False)

            for student in dashboard_data:
                student.progress_data = Progress.objects.filter(student=student)
                # Calculate total paid
                total_paid = student.progress_data.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.0')
                # Fetch total fees for the student (replace 'total_fees' with the actual field name)
                total_fees = Decimal(str(student.total_fees)) if student.total_fees is not None else Decimal('0.0')
                # Calculate due amount
                due_amount = total_fees - total_paid
                # Assign calculated values to the student object
                student.total_paid = total_paid
                student.total_fees = total_fees
                student.due_amount = due_amount

            context = {'kafeel': kafeel, 'dashboard_data': dashboard_data}
            return render(request, 'sponsor_dashboard.html', context)

        except (ValueError, Kafeel.DoesNotExist):
            return render(request, 'sponsor_dashboard_login.html', {'error_message': 'Invalid Kafeel credentials. Please try again.'})

    return render(request, 'sponsor_dashboard_login.html', {'kafeel_id': kafeel_id})

def get_students(request):
    # Your view logic for get_students goes here
    return render(request, 'fetch_students.html', {'students': StudentStatusUpdate})
from django.conf import settings
from django.shortcuts import get_list_or_404
from .models import Account,course, Video,Payment,Assessment
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, authenticate
from django.contrib import auth
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.utils.html import strip_tags
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from io import BytesIO
import base64
# Create your views here.




def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        if password==confirmpassword:
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('signup')
            user = Account.objects.create_user(first_name=first_name,email=email, password=password)
            user.is_user = True
            user.save()
            messages.info(request, 'Thank you for registering with us. Please Login')
            messages.success(request, 'Please verify your email for login!')

            current_site = get_current_site(request)
            message = render_to_string('account_verification_email.html', {
                        'user': user,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    })

            send_mail(
                        'Please activate your account',
                        message,
                        'mycardshelp@gmail.com',
                        [email],
                        fail_silently=False,
                    )

            # return redirect('/login/?command=verification&email=' + email)

            return redirect('login')
        else:
            print('password is not matching')
            messages.info(request, '!!!Password and Confirm Password are not  match!!!')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('signup')        

    

def login(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        pswd = request.POST.get('pass')
        print(email, pswd)
        user = auth.authenticate(email=email, password=pswd)
        print(user)

        if user is not None:
            auth.login(request, user)
            # save email in session
            request.session['email'] = email
            if user.is_admin:
                return redirect('admin')
            else:
                return redirect('Homee')
          
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('index')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email


            current_site = get_current_site(request)
            message = render_to_string('ResetPassword_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                'Please activate your account',
                message,
                'mycardshelp@gmail.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'Forgot_Password.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['pass']
        confirm_password = request.POST['repass']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.info(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'ResetPassword.html')

def Homebase(request):
    return render(request,'Homebase.html')

def basee(request):
    return render(request,'basee.html')

def admin_base(request):
    user=Account.objects.all()
    return render(request,'admin_base.html',{'user':user,})

def Homee(request):
     # Fetch courses from the database
    courses = course.objects.all()

    # Pass the courses to the template
    context = {'courses': courses}
    return render(request, 'Homee.html', context)
     

def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')

def index(request):
    # Fetch courses from the database
    courses = course.objects.all()

    # Pass the courses to the template
    context = {'courses': courses}
    return render(request,'index.html',context)

import datetime
from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.shortcuts import render
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import random
def admin(request):
    # Count the number of users
    users = Account.objects.filter(is_user=True).count()
    cou= course.objects.all().count()
    # Get all courses
    courses = course.objects.all()

    # Calculate the number of successful payments for each course
    courses_data = []
    for c in courses:
        num_payments = Payment.objects.filter(product=c, paid=True).count()
        courses_data.append({'course_name': c.course_name, 'num_payments': num_payments})

    # Shuffle the courses for better visualization
    courses_data = shuffle(courses_data)

    # Extract data for the pie chart
    labels = [course['course_name'] for course in courses_data]
    data = [course['num_payments'] for course in courses_data]

    # Generate the pie chart
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that the pie chart is drawn as a circle

    # Save the pie chart to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

   # Calculate the number of successful payments for each course
    courses_data = []
    for c in courses:
        num_payments = Payment.objects.filter(product=c, paid=True).count()
        courses_data.append({'course_name': c.course_name, 'num_payments': num_payments})

    # Shuffle the courses for better visualization
    courses_data = shuffle(courses_data)

    # Extract data for the pie chart
    labels = [course['course_name'] for course in courses_data]
    data = [course['num_payments'] for course in courses_data]

    # Generate the pie chart
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that the pie chart is drawn as a circle

    # Save the pie chart to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Get yearly enrollment data for each course
    yearly_enrollment_data = []
    for c in courses:
        enrollment_by_year = (
            Payment.objects
            .filter(product=c, paid=True)
            .annotate(year=ExtractYear('created_at'))
            .values('year')
            .annotate(enrollment_count=Count('id'))
            .order_by('year')
        )
        yearly_enrollment_data.append({'course_name': c.course_name, 'enrollment_data': enrollment_by_year})

    # Pass the data as context to the template
    return render(request, 'admin.html', {'user': users, 'cou': cou, 'courses_data': courses_data, 'chart_image': chart_image, 'yearly_enrollment_data': yearly_enrollment_data})

def searchbar(request):
    query = request.GET.get('q')
    # Search for courses and users based on the query
    courses = course.objects.filter(course_name__icontains=query) if query else []
    users = Account.objects.filter(first_name__icontains=query) if query else []
    context = {'courses': courses, 'users': users, 'query': query}
    return render(request, 'searchbar.html', context)


def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('fullName', '')
        user.contact = request.POST.get('phone', '')

        # Check if 'profileImageInput' key exists in request.FILES
        if 'profileImageInput' in request.FILES:
            new_image = request.FILES['profileImageInput']
            user.img = new_image
        elif not user.img:  # Handle the case when 'profileImageInput' is not provided and user.img is empty
            user.img = None

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'profile.html')



def add_course(request):
    week_choices = course.WEEK_CHOICES

    if request.method == 'POST':
        # Handle form submission and saving data to the database
        course_name = request.POST.get('course_name')
        title = request.POST.get('title')
        outcomes = request.POST.get('outcomes')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        week = request.POST.get('week')
        image = request.FILES.get('image')

        # Get the currently logged-in user
        user = request.user

        new_course = course.objects.create(
            user=user,
            course_name=course_name,
            title=title,
            outcomes=outcomes,
            desc=desc,
            price=price,
            course_week=week,
            image=image,
            # Add other fields as needed
        )

        return redirect('admin_course_view')  # Redirect to the appropriate view after successful form submission

    context = {
        'week_choices': week_choices,
    }

    return render(request, 'add_course.html', context)




def admin_course_view(request):
    # Retrieve all courses from the database
    courses = course.objects.all()
    return render(request, 'admin_course_view.html', {'courses': courses})


def edit_course(request, course_id):
    instance = get_object_or_404(course, course_id=course_id)

    if request.method == 'POST':
        # Handle form submission and update data in the database
        instance.course_name = request.POST.get('course_name')
        instance.title = request.POST.get('title')
        instance.outcomes = request.POST.get('outcomes')
        instance.desc = request.POST.get('desc')
        instance.price = request.POST.get('price')
        instance.course_week = request.POST.get('week')
        # Check if a new image is provided
        new_image = request.FILES.get('image')
        if new_image:
            instance.image = new_image

        # Save the changes
        instance.save()

        return redirect('admin_course_view')

    # Provide the course instance to the edit_course.html template
    context = {
        'course': instance,
    }

    return render(request, 'edit_course.html', context)



def delete_course(request, id):
    item = get_object_or_404(course, course_id=id)
    item.delete()
    return redirect('admin_course_view')


def userdetails(request):
    users = Account.objects.filter(is_user=True)
    return render(request, 'userdetails.html', {'users': users})



def adminprofile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('fullName', '')
        user.contact = request.POST.get('phone', '')

        # Check if 'profileImageInput' key exists in request.FILES
        if 'profileImageInput' in request.FILES:
            new_image = request.FILES['profileImageInput']
            user.img = new_image

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('adminprofile')

    return render(request, 'adminprofile.html')


def module_add(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        week = request.POST.get('week')

        if not course_name or not week:
            return HttpResponseBadRequest("Invalid course or week.")

        existing_videos = Video.objects.filter(course__course_name=course_name, week=week)
        if existing_videos.exists():
            return HttpResponseBadRequest("Videos for the selected week already exist. You can't add videos for the same week again.")

        for i in range(1, 6):
            video_file = request.FILES.get(f'video_{i}')
            video_title = request.POST.get(f'video_title_{i}')
            
            if video_file and video_title:
                Video.objects.create(
                    week=week,
                    video_number=i,
                    video_file=video_file,
                    video_title=video_title,
                    course=course.objects.get(course_name=course_name)
                )
        return redirect('admin_module_view')

    return render(request, 'module_add.html', {'existing_courses': course.objects.all()})



def module_edit(request, week_id):
    videos = Video.objects.filter(week=week_id)

    if request.method == 'POST':
        video_number = request.POST.get('video_number')
        video_file = request.FILES.get('video_file')

        if not video_number:
            return HttpResponseBadRequest("Missing video_number parameter.")

        video_data = get_object_or_404(Video, week=week_id, video_number=video_number)

        if video_file:
            video_data.video_file = video_file
            video_data.save()
        return redirect('admin_module_view')

    return render(request, 'module_edit.html', {'videos': videos, 'week_id': week_id})




def admin_add_assesment_edit(request, week_id, course_id):
    # Fetch course object using get_object_or_404
    course_obj = get_object_or_404(course, course_id=course_id)

    if request.method == 'POST':
        # Extract data from the form
        question = request.POST.get('question')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        option5 = request.POST.get('option5')
        answers = request.POST.get('answers')

        # Create Assessment object with the correct 'course' reference
        assessment = Assessment.objects.create(
            week=week_id,
            course=course_obj,  # Set the course reference
            question=question,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            option5=option5,
            answers=answers
        )

        return redirect('admin_module_view')

    # Render the template with necessary context
    return render(request, 'admin_add_assesment_edit.html', {'week_id': week_id, 'course_id': course_id, 'course': course_obj})



def admin_module_view(request):
    courses = course.objects.all()

    # Create a list of dictionaries to store video URLs for each course and week
    course_weeks = []
    for course_obj in courses:
        videos_by_week = []
        for week, week_name in course.WEEK_CHOICES:
            videos = Video.objects.filter(course=course_obj, week=week)
            video_urls = [video.video_file.url for video in videos]
            videos_by_week.append({
                'week_name': week_name,
                'video_urls': video_urls,
                'range_5': range(5),
                'week_id': week, 
            })

        course_weeks.append({'course': course_obj, 'weeks': videos_by_week})

    context = {'course_weeks': course_weeks}
    return render(request, 'admin_module_view.html', context)






def Course_User(request):
    return render(request, 'Course_User.html')


def course_detail(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    x = course_instance.outcomes.split("->")
    context = {'course_instance': course_instance, 'x': x}
    return render(request, 'course_detail.html', context)


def enroll_course(request, course_id):
    if request.method == 'POST':
        course_instance = get_object_or_404(course, course_id=course_id)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not logged in'}, status=401)

        # Ensure the amount is an integer in paise
        amount = int(course_instance.price * 100)
        if amount < 100:
            return JsonResponse({'error': 'Invalid amount'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'course_{course_instance.course_id}_{request.user.id}',
            'payment_capture': '1',
        }

        order = client.order.create(data=order_data)
        order_id = order['id']
        request.session['order_id'] = order_id
        order_status = order['status']

        if order_status == 'created':
            # Check if the user has already enrolled in this course
            existing_payment = Payment.objects.filter(user=request.user, product=course_instance, paid=True).first()

            if not existing_payment:
                # User has not enrolled in this course, create a new payment record
                payment = Payment.objects.create(
                    user=request.user,
                    amount=course_instance.price,  # Save the original price in rupees
                    razorpay_order_id=order_id,
                    razorpay_payment_status=order_status,
                    product=course_instance
                )
                payment.save()

                # Set paid to True and save razorpay_payment_id upon successful payment
                payment.paid = True
                payment.razorpay_payment_id = order.get('id')
                payment.save()

                return JsonResponse({'order_id': order['id'], 'amount': amount, 'course_id': course_instance.course_id})
            else:
                # User has already enrolled in this course, return an error
                return JsonResponse({'error': 'User is already enrolled in this course'}, status=400)

        return JsonResponse({'error': 'Invalid request method'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# def payment_done(request):
#     order_id = request.GET.get('order_id')
#     payment_id = request.GET.get('payment_id')

#     if order_id:
#         payment = get_object_or_404(Payment, razorpay_order_id=order_id, razorpay_payment_status='created')

#         payment.paid = True
#         payment.razorpay_payment_id = payment_id
#         payment.razorpay_payment_status = 'paid'
#         payment.save()

#         # Send enrollment confirmation email
#         send_enrollment_confirmation_email(request.user, payment.product, payment)

#         return JsonResponse({'message': 'Payment successful'})

#     return JsonResponse({'error': 'Invalid payment confirmation'}, status=400)


# def send_enrollment_confirmation_email(user, course_instance, payment):
#     subject = 'Course Enrollment Confirmation'
#     message = render_to_string('enrollment_confirmation_email.html', {'user': user, 'course': course_instance, 'payment': payment})
#     plain_message = strip_tags(message)
#     from_email = 'mycardshelp@gmail.com'  # Update with your email
#     to_email = [user.email]

#     send_mail(subject, plain_message, from_email, to_email, html_message=message)

def course_single(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    videos = Video.objects.filter(course=course_instance)
    assessments = Assessment.objects.filter(course=course_instance)
    context = {
        'course_instance': course_instance,
        'videos': videos,
        'assessments': assessments,
        'weeks_range': range(1, course_instance.course_week + 1),
    }
    return render(request, 'course_single.html', context)



def My_Course(request):
    user = request.user
    enrolled_courses = Payment.objects.filter(user=user, paid=True).select_related('product')

    context = {
        'enrolled_courses': enrolled_courses
    }

    return render(request, 'My_Course.html', context)




def weekly_assessment(request, course_id, week):
    course_instance = get_object_or_404(course, course_id=course_id)
    questions = Assessment.objects.filter(course=course_instance, week=week, status=True)

    results = []
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            selected_option_id = int(value)
            
            assessment = get_object_or_404(Assessment, id=question_id)

            # Assuming the correct answer is stored in the 'answers' field
            correct_answers = [option.strip() for option in assessment.answers.split(',')]

            selected_answer = getattr(assessment, f'option{selected_option_id}')
            is_correct = selected_answer in correct_answers
            print(selected_answer)
            results.append({
                'question_id': question_id,
                'selected_answer': selected_answer,
                'is_correct': is_correct
            })

    total_questions = len(questions)
    correct_answers_count = sum(result['is_correct'] for result in results)
    final_percentage = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0

    context = {
        'course_instance': course_instance,
        'questions': questions,
        'week': week,
        'results': results,
        'final_percentage': final_percentage
    }
    return render(request, 'assessment.html', context)
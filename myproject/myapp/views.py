from django.conf import settings
from django.shortcuts import get_list_or_404
import numpy as np
from .models import Account,course, Video,Payment,Assessment,UserAssessment,Grand_Quiz,Certificate
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
from django.http import Http404, HttpResponse, JsonResponse
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
    pay=Payment.objects.all()

    # Fetch count of reviews for each course
    for course_instance in courses:
        course_instance.review_count = ReviewRating.objects.filter(product=course_instance, status=True).count()
        course_instance.video_count = Video.objects.filter(course=course_instance).count()
     # Get recommended courses for the current user
    recommended_courses = course_recommendations(request)

    # Pass the courses to the template
    context = {'courses': courses, 'recommended_courses': recommended_courses,'pay':pay}
    return render(request, 'Homee.html', context)


def search_results(request):
    
    query = request.GET.get('q')
    if query:
        courses = course.objects.filter(course_name__icontains=query) | course.objects.filter(categories__icontains=query)
    else:
        courses = []
    context = {'courses': courses, 'query': query}
    return render(request, 'search_results.html', context)

      

def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')

def index(request):
    # Fetch courses from the database
    courses = course.objects.all()

    # Fetch count of reviews and videos for each course
    for course_instance in courses:
        course_instance.review_count = ReviewRating.objects.filter(product=course_instance, status=True).count()
        course_instance.video_count = Video.objects.filter(course=course_instance).count()


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
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
from django.utils import timezone
from collections import defaultdict
from django.db.models import Sum

from django.db.models import Q
from django.utils import timezone

def admin(request):
    # Ensure the NLTK VADER lexicon is downloaded
    nltk.download('vader_lexicon')

    # Count the number of users
    users = Account.objects.filter(is_user=True).count()
    cou = course.objects.all().count()

    # Get all courses
    courses = course.objects.all()

    # Calculate total revenue
    total_revenue = Payment.objects.filter(paid=True).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Calculate the number of successful payments for each course
    courses_data = []
    for c in courses:
        num_payments = Payment.objects.filter(product=c, paid=True).count()
        courses_data.append({'course_name': c.course_name, 'num_payments': num_payments})

    # Shuffle the courses for better visualization
    courses_data = shuffle(courses_data)

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

    # Get unique years for enrollment
    years = set()
    for course_data in yearly_enrollment_data:
        for enrollment_data in course_data['enrollment_data']:
            years.add(enrollment_data['year'])

    # Sort years in ascending order
    years = sorted(years)

    # Create a dictionary to store enrollment counts per year per course
    enrollment_counts = {course_data['course_name']: {year: 0 for year in years} for course_data in yearly_enrollment_data}

    # Update enrollment counts
    for course_data in yearly_enrollment_data:
        for enrollment_data in course_data['enrollment_data']:
            enrollment_counts[course_data['course_name']][enrollment_data['year']] = enrollment_data['enrollment_count']

    # Convert enrollment data to a format suitable for JavaScript
    js_yearly_enrollment_data = [{'course_name': course_data['course_name'], 'enrollment_counts': [enrollment_counts[course_data['course_name']][year] for year in years]} for course_data in yearly_enrollment_data]

    ## Get sentiment analysis data for each course
    # Get sentiment analysis data for each course
    course_sentiments = defaultdict(list)
    sia = SentimentIntensityAnalyzer()
    for c in courses:
        reviews = ReviewRating.objects.filter(product=c, status=True)
        for review in reviews:
            sentiment_score = sia.polarity_scores(review.review)['compound']
            sentiment_category = 'positive' if sentiment_score >= 0 else 'negative'
            course_sentiments[c.course_name].append(sentiment_category)

    # Count the number of positive and negative reviews for each course
    sentiment_counts = {course_name: {'positive': sentiments.count('positive'), 'negative': sentiments.count('negative')} for course_name, sentiments in course_sentiments.items()}

    # Separate the sentiment data into positive and negative reviews
    positive_reviews = [{'course_name': course_name, 'count': counts['positive']} for course_name, counts in sentiment_counts.items()]
    negative_reviews = [{'course_name': course_name, 'count': counts['negative']} for course_name, counts in sentiment_counts.items()]

    # Sort the positive and negative reviews by count
    positive_reviews = sorted(positive_reviews, key=lambda x: x['count'], reverse=True)
    negative_reviews = sorted(negative_reviews, key=lambda x: x['count'], reverse=True)

    # Render the results
    positive_data = [review for review in positive_reviews]
    negative_data = [review for review in negative_reviews]

    return render(request, 'admin.html', {'user': users, 'cou': cou, 'courses_data': courses_data, 'years': years, 'js_yearly_enrollment_data': js_yearly_enrollment_data, 'positive_data': positive_data, 'negative_data': negative_data,'total_revenue': total_revenue})

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



from django.shortcuts import render, redirect
from .models import course

def add_course(request):
    week_choices = course.WEEK_CHOICES

    if request.method == 'POST':
        # Handle form submission and saving data to the database
        course_name = request.POST.get('course_name')
        title = request.POST.get('title')
        outcomes = request.POST.get('outcomes')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        week = request.POST.get('week')
        image = request.FILES.get('image')
        requirements = request.POST.get('requirements')
        language = request.POST.get('language')
        skill_level = request.POST.get('skill_level')
        certificate = request.POST.get('certificate')
        categories = request.POST.get('categories')

        # Convert certificate value to boolean
        certificate = True if certificate == 'yes' else False

        # Get the currently logged-in user
        user = request.user

        new_course = course.objects.create(
            user=user,
            course_name=course_name,
            title=title,
            outcomes=outcomes,
            desc=desc,
            price=price,
            discount=discount,
            course_week=week,
            image=image,
            requirements=requirements,
            language=language,
            skill_level=skill_level,
            certificate=certificate,
            categories=categories,
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
        instance.discount = request.POST.get('discount')
        
        # Correctly retrieve and save the course week
        course_week = request.POST.get('week')
        instance.course_week = int(course_week) if course_week.isdigit() else 0
        
        instance.requirements = request.POST.get('requirements')
        instance.language = request.POST.get('language')
        instance.skill_level = request.POST.get('skill_level')
        instance.certi = request.POST.get('certi')
        
        # Convert certi value to boolean
        instance.certi = True if instance.certi == 'on' else False

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



def module_edit(request, course_id, week_id):
    videos = Video.objects.filter(course_id=course_id, week=week_id)

    if request.method == 'POST':
        video_number = request.POST.get('video_number')
        video_file = request.FILES.get('video_file')

        if not video_number:
            return HttpResponseBadRequest("Missing video_number parameter.")

        video_data = get_object_or_404(Video, course_id=course_id, week=week_id, video_number=video_number)

        if video_file:
            video_data.video_file = video_file
            video_data.save()
        return redirect('admin_module_view')

    return render(request, 'module_edit.html', {'videos': videos, 'week_id': week_id, 'course_id': course_id})



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
            if week <= course_obj.course_week:  # Filter weeks based on the actual number of weeks for the course
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
    courses = course.objects.all()
    categories = course.objects.values_list('categories', flat=True).distinct()
    skill_levels = course.objects.values_list('skill_level', flat=True).distinct()
     # Filter courses based on selected skill level and category
    selected_category = request.GET.get('category')
    selected_skill_level = request.GET.get('skill_level')

    courses = course.objects.all()
    if selected_category:
        courses = courses.filter(categories=selected_category)
    if selected_skill_level:
        courses = courses.filter(skill_level=selected_skill_level)

   # Calculate video count and rating count for each course
    for course_obj in courses:
        course_obj.video_count = course_obj.video_set.count()
        course_obj.rating_count = ReviewRating.objects.filter(product=course_obj).count()
    
    # Calculate rating count for each course
    for course_obj in courses:
        course_obj.rating_count = ReviewRating.objects.filter(product=course_obj, status=True).count()

    return render(request, 'Course_User.html', {'courses': courses, 'categories': categories, 'skill_levels': skill_levels,'selected_category': selected_category,
        'selected_skill_level': selected_skill_level,
    })


def enroll_course(request, course_id):
    if request.method == 'POST':
        course_instance = get_object_or_404(course, course_id=course_id)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not logged in'}, status=401)
        
        # Ensure the amount is an integer in paise
        amount = int(course_instance.price * 100)
        discount_amount=amount*course_instance.discount/100
        amount-=discount_amount
        # print(amount,course_instance.discount)
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
    feedback=ReviewRating.objects.all()
    
    # Fetching user assessments
    user = request.user
    user_assessments = UserAssessment.objects.filter(course=course_instance, user=user)
    # Preparing data for the chart
    user_data = {}
    for user_assessment in user_assessments:
        user_key = f"{user_assessment.user.first_name} {user_assessment.user.last_name}"
        if user_key not in user_data:
            user_data[user_key] = [0] * course_instance.course_week
        
        user_data[user_key][user_assessment.week - 1] = user_assessment.marks
        
    
    context = {
        'course_id': course_id,
        'course_instance': course_instance,
        'videos': videos, 
        'assessments': assessments,
        'weeks_range': range(1, course_instance.course_week + 1),
        'user_data': user_data,
        'feedback':feedback
    }
    # Calculate star rating percentage for each review
    for review in feedback:
        review.star_rating_percentage = review.rating / 5 * 100

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

    # Check if the assessment for the week has already been taken
    previous_user_assessment = UserAssessment.objects.filter(
        user=request.user,
        course=course_instance,
        week=week
    ).first()

    assessment_taken = False

    if previous_user_assessment:
        assessment_taken = True
        context = {
            'course_instance': course_instance,
            'questions': questions,
            'week': week,
            'results': [],  # Empty results to avoid displaying any previous results
            'final_percentage': 0,
            'assessment_taken': assessment_taken,
        }
        return render(request, 'assessment.html', context)

    results = []
    assessment = None

    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            selected_option_id = int(value)
            
            assessment = get_object_or_404(Assessment, id=question_id)

            # Assuming the correct answer is stored in the 'answers' field
            correct_answers = [option.strip() for option in assessment.answers.split(',')]

            selected_answer = getattr(assessment, f'option{selected_option_id}')
            is_correct = selected_answer in correct_answers
            results.append({
                'question_id': question_id,
                'selected_answer': selected_answer,
                'is_correct': is_correct
            })

    total_questions = len(questions)
    correct_answers_count = sum(result['is_correct'] for result in results)
    final_percentage = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0

    # Check if assessment is not None before creating or updating UserAssessment
    if assessment:
        # Store the results in the UserAssessment model
        user_assessment, created = UserAssessment.objects.get_or_create(
            user=request.user,  # Assuming user is authenticated, change as needed
            assessment=assessment,
            week=week,
            course=course_instance,  # Include the course field
            defaults={'marks': final_percentage, 'taken': True}
        )

        # Check if the assessment was already taken
        if not created:
            messages.error(request, "You have already taken this assessment.")
            assessment_taken = True

    context = {
        'course_instance': course_instance,
        'questions': questions,
        'week': week,
        'results': results,
        'final_percentage': final_percentage,
        'assessment_taken': assessment_taken,
    }
    return render(request, 'assessment.html', context)



def grand_quiz(request):
    existing_courses = course.objects.all()

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        quiz_file = request.FILES.get('quiz_file')

        if not course_name or not quiz_file:
            return HttpResponseBadRequest("Invalid form submission")

        try:
            # Read and decode the content of the text file
            content = quiz_file.read().decode('utf-8')

            # Split the content into lines
            lines = content.split('\n')

            # Initialize variables
            questions_data = []
            question = None
            options = []

            for line in lines:
                line = line.strip()
                if line:
                    # If line starts with a digit, it's a new question
                    if line[0].isdigit():
                        # If previous question data exists, append it to questions_data
                        if question and options:
                            questions_data.append({
                                'question': question,
                                'options': options,
                                'answer': answer
                            })
                        # Initialize for the new question
                        question = line
                        options = []
                        answer = None
                    elif line.startswith("Answer:"):
                        # If line starts with "Answer:", it's the answer for the current question
                        answer = line
                    else:
                        # Otherwise, it's an option
                        options.append(line)

            # Append the last question data to questions_data
            if question and options:
                questions_data.append({
                    'question': question,
                    'options': options,
                    'answer': answer
                })
                print(answer)
            # Get or create the Course instance
            course_instance, created = course.objects.get_or_create(course_name=course_name)

            # Create a Grand_Quiz instance
            grand_quiz_instance = Grand_Quiz.objects.create(
                coursename=course_instance,
                questions=questions_data,
                status=True
            )

            return redirect('grand_quiz')

        except Exception as e:
            return HttpResponseBadRequest(f"Error processing the file: {str(e)}")

    context = {'existing_courses': existing_courses}
    return render(request, 'grand_quiz.html', context)






def Grand_Quiz_User(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    grand_quiz_data = Grand_Quiz.objects.filter(coursename=course_instance)

    if request.method == 'POST':
        total_marks = 0
        max_marks = 0
        results = []

        for grand_quiz in grand_quiz_data:
            max_marks += len(grand_quiz.questions)
            for index, question in enumerate(grand_quiz.questions):
                user_answer = request.POST.get(str(index + 1), "")
                correct_answer = question['answer'][8:]

                if user_answer.lower() == correct_answer.lower():
                    total_marks += 1

                results.append({
                    'question_id': index + 1,
                    'is_correct': user_answer.lower() == correct_answer.lower(),
                    'selected_answer': user_answer,
                })

        score_percentage = (total_marks / max_marks) * 100

        if score_percentage >= 80:
            result_category = 'Expert'
        elif score_percentage < 50:
            result_category = 'Beginner'
        else:
            result_category = 'Intermediate'

        certificate = Certificate.objects.create(
            user=request.user,
            course=course_instance,
            percentage=score_percentage,
            result=result_category,
        )

        context = {
            'course_instance': course_instance,
            'grand_quiz_data': grand_quiz_data,
            'results': results,
            'final_percentage': score_percentage,
            'certificate': certificate,
        }

        return render(request, 'Grand_Quiz_User.html', context)

    context = {
        'course_instance': course_instance,
        'grand_quiz_data': grand_quiz_data,
    }

    return render(request, 'Grand_Quiz_User.html', context)



def certificate_view(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    return render(request, 'certificate.html', {'certificate': certificate})




from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from .models import Certificate

def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    # Render the modified HTML content of the certificate
    certificate_html = render_to_string('certificate.html', {'certificate': certificate})
    soup = BeautifulSoup(certificate_html, 'html.parser')
    certificate_content1 = soup.find('div', id='x')
    certificate_content=str(certificate_content1)
    certificate_content="""<html>
<head>
    <title>Test Page</title>
    <style>
        /* Your CSS styles here */
        
         
         body {
        margin: 0;
        padding: 0;
        font-family: 'Lobster', cursive;  
    }
         #content { 
         width: 90%;
         margin: auto;  
        text-align: center; 
    }
     .logo {
        max-width: 100px;
        margin-bottom: 10px;
    }
    .certificate-title {
        color: #191C24;
        font-size: 30px;
    }
    .certificate-header, .certificate-footer {
        padding: 10px 0;
    }
    .certificate-body {
        padding: 20px 0;
    }
    .certificate-assignment, .certificate-reason {
        font-size: 18px;
        color: #333;
        margin-bottom: 10px;
    }
    .certificate-person {
        font-size: 36px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .course-name {
        font-size: 24px;
        font-weight: bold;
        color: #191C24;
    }
    .certificate-info {
        font-size: 16px;
        color: #666;
    }
    </style>
</head>
<body >
    <div id="content">
    """+certificate_content+"""</div></body></html>"""
    print(certificate_content) 
    # Generate PDF from the HTML content
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(certificate_content.encode("UTF-8")), result)
    
    if not pdf.err:
        # Set response content type as PDF
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        # Set content disposition to attachment to force download
        response['Content-Disposition'] = f'attachment; filename="certificate_{certificate_id}.pdf"'
        return response
    else:
        return HttpResponse("Error generating PDF", status=500)


def my_Certificate_list(request):
    return render(request, 'my_Certificate_list.html')




########################################################################################

from django.shortcuts import render
from .models import ReviewRating, course
from django.db.models import Avg
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.express as px
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.sentiment import SentimentIntensityAnalyzer

def review_analysis(request,course_id):
    if request.method == 'POST':
        # Handle form submission
            rating = request.POST.get('rating')
            review_title = request.POST.get('review_title')
            review_content = request.POST.get('review_content')

            # Ensure the user is logged in
            if request.user.is_authenticated:
                user_instance = request.user
            else:
                # Handle the case when the user is not authenticated
                # You may redirect them to the login page or handle it as needed
                messages.error(request, 'Please log in to submit a review.')
                return redirect('login')  # Update 'login' with the actual login URL

            # Save the review to the database
            course_instance = course.objects.get(pk=course_id)
            review = ReviewRating.objects.create(
                product=course_instance,
                user=user_instance,  # Associate the review with the logged-in user
                rating=rating,
                headline=review_title,
                review=review_content,
                # You may need to adjust other fields based on your model
            )
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('course_single', course_id=course_id)  # Redirect to the same page to display updated reviews

    # Load the review data from the database, filtering by status=True
    reviews = ReviewRating.objects.filter(status=True)

    # Convert the review data to a Pandas DataFrame
    review_data = pd.DataFrame(list(reviews.values()))

    # Tokenize the review text
    stop_words = stopwords.words('english')
    stemmer = SnowballStemmer('english')
    review_data['tokens'] = review_data['review'].apply(
        lambda x: [stemmer.stem(token.lower()) for token in word_tokenize(x) if token.lower() not in stop_words])

    # Calculate the sentiment score for each review using VADER
    sia = SentimentIntensityAnalyzer()
    review_data['sentiment_scores'] = review_data.apply(
        lambda x: sia.polarity_scores(x['review'])['compound'], axis=1)

    # Assign each review to a "positive" or "negative" category based on the sentiment score
    review_data['sentiment_category'] = review_data['sentiment_scores'].apply(
        lambda x: 'positive' if x >= 0.05 else 'negative')

    # Calculate the average sentiment score for each course
    course_sentiment = review_data.groupby(['product_id', 'sentiment_category'])['sentiment_scores'].mean().reset_index()
    course_data = pd.DataFrame(list(course.objects.all().values()))
    course_data = course_data.merge(course_sentiment, left_on='course_id', right_on='product_id')


     # Create a bar chart using Plotly
    fig = px.bar(
        course_data,
        x='course_id',
        y='sentiment_scores',
        color='sentiment_category',
        labels={'sentiment_scores': 'Average Sentiment Score'},
        title='Sentiment Analysis for Courses',
    )

    # Convert the plot to HTML code
    chart_html = plot(fig, output_type='div')

    # Separate the course data into positive and negative reviews
    positive_reviews = course_data[course_data['sentiment_category'] == 'positive']
    negative_reviews = course_data[course_data['sentiment_category'] == 'negative']

    # Sort the positive and negative reviews by sentiment score
    positive_reviews = positive_reviews.sort_values(by='sentiment_scores', ascending=False)
    negative_reviews = negative_reviews.sort_values(by='sentiment_scores', ascending=True)

    # Render the results
    positive_data = positive_reviews.to_dict('records')
    negative_data = negative_reviews.to_dict('records')

    # Pass the HTML code and course data to the template
    context = {
        'course_id': course_id,
        'positive_data': positive_data,
        'negative_data': negative_data,
        'html_code': chart_html,
    }
    return render(request, 'course_single.html', context)



from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import course, UserAssessment,ReviewRating

def course_detail(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    x = course_instance.outcomes.split("->")
    y = course_instance.requirements.split("->")

    # Fetch count of enrolled students for the current course
    enrolled_students_count = Payment.objects.filter(product=course_instance, paid=True).count()

    # Fetch all reviews for the current course
    reviews = ReviewRating.objects.filter(product=course_instance, status=True)
    
     # Calculate the count of reviews for the course
    reviews_count = reviews.count()

    # Calculate the width of the rating bar
    for review in reviews:
        review.rating_width = int(review.rating * 20)  # Convert rating to percentage
    
    
    
    context = {
        'course_instance': course_instance,
        'x': x,
        'y': y,
        'enrolled_students_count': enrolled_students_count,
        'reviews': reviews,
        'reviews_count': reviews_count,  # Pass the reviews to the template context
    }
    return render(request, 'course_detail.html', context)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import get_object_or_404

def course_recommendations(request):
    user = request.user
    
    # Get all courses that the user has enrolled in
    enrolled_courses = UserAssessment.objects.filter(user=user, taken=True).values_list('course_id', flat=True)
    enrolled_course_ids = list(enrolled_courses)
    
    if not enrolled_course_ids:
        return []
    
    # Get the text descriptions of the enrolled courses
    enrolled_desc = [c.outcomes for c in course.objects.filter(course_id__in=enrolled_course_ids)]
    
    # Fetch all courses except the ones the user has already enrolled in
    unenrolled_courses = course.objects.exclude(course_id__in=enrolled_course_ids)
    
    if not unenrolled_courses:
        return []
    
    # Get the text descriptions of the unenrolled courses
    unenrolled_desc = [c.outcomes for c in unenrolled_courses]
    
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit the vectorizer to the text descriptions
    vectorizer.fit(enrolled_desc + unenrolled_desc)
    
    # Transform the enrolled and unenrolled descriptions to TF-IDF vectors
    enrolled_vectors = vectorizer.transform(enrolled_desc)
    unenrolled_vectors = vectorizer.transform(unenrolled_desc)
    
    # Calculate the cosine similarity between the enrolled and unenrolled vectors
    similarity = cosine_similarity(enrolled_vectors, unenrolled_vectors)
    
    # Get the indices of the most similar unenrolled courses for each enrolled course
    top_indices = similarity.argsort(axis=1)[:, ::-1][:, :1]
    
    # Get the course objects corresponding to the top indices
    recommended_courses = []
    for i, course_index in enumerate(top_indices):
        enrolled_course = get_object_or_404(course, course_id=enrolled_course_ids[i])
        unenrolled_course = unenrolled_courses[int(course_index)]
        recommended_courses.append({'enrolled_course': enrolled_course, 'unenrolled_course': unenrolled_course})
    
    return recommended_courses









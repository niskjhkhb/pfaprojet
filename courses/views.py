
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required # for Access Control
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404
from .models import Course
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import CustomUserCreationForm


# Create views here.
def courses_processor(request):
    courses = Course.objects.filter(course_is_active='Yes')  # Fetch only active courses
    return {'courses': courses}

def home(request):
    return render(request,'courses/index.html')


def signup(request):        
    return render(request, 'courses/signup.html')

def index(request):
    courses = Course.objects.filter(course_is_active='Yes', course_is_featured="Yes")
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)

def baseview(request):
    courses = Course.objects.filter(course_is_active='Yes')
    context = {
        'courses': courses,
    }
    return render(request, 'courses/baseview.html', context)

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'courses/login.html'  

    def form_valid(self, form):
        # Check if "Remember Me" is selected
        remember_me = self.request.POST.get('remember', None)

        # Log in the user
        login(self.request, form.get_user())

        if not remember_me:
            # Set session to expire when the browser is closed
            self.request.session.set_expiry(0)
        else:
            # Set session to the default duration (e.g., 2 weeks)
            self.request.session.set_expiry(1209600)  # 2 weeks in seconds

        return super().form_valid(form)

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None  # Remove help text
            field.widget.attrs.update({'placeholder': field.label})  # Optional: set placeholder


from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # ✅ use your custom form here
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()  # ✅ here too
    return render(request, 'courses/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'courses/profile.html')

 
from django.shortcuts import render, get_object_or_404
from .models import Course, Progress

def course_detail(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    
    # Only check Progress if the user is authenticated
    if request.user.is_authenticated:
        progress = Progress.objects.filter(user=request.user, course=course).first()
    else:
        progress = None  # No progress for unauthenticated users

    context = {
        'course': course,
        'quiz_score': progress.quiz_score if progress else None,  # Pass the quiz score if progress exists
    }

    return render(request, 'courses/course_detail.html', context)


def topic_courses(request, topic_slug):
    topic = Topic.objects.get(topic_slug=topic_slug)
    courses = Course.objects.filter(course_is_active='Yes', course_topic=topic)
    context = {
        'courses': courses,
        'topic': topic,
    }
    return render(request, 'courses/topic_courses.html', context)


def search_courses(request):
    if request.method == "GET":
        keyword = request.GET.get('q')
        courses = Course.objects.filter(course_is_active='Yes')
        searched_courses = courses.filter(course_title__icontains=keyword) | courses.filter(course_description__icontains=keyword)
        
        context = {
            'courses': searched_courses,
            'keyword': keyword,
        }
        return render(request, 'courses/search_courses.html', context)


"""def course_detail(request, course_slug):
    try:
        course = Course.objects.get(course_slug=course_slug)
        lectures = Lecture.objects.filter(course=course.id)

        # Check
        if request.user.is_authenticated:
            enrolled = Enroll.objects.filter(course=course, user=request.user)
        else:
            enrolled = None
        

        context = {
            'course': course,
            'lectures': lectures,
            'enrolled': enrolled,
        }
        return render(request, 'courses/course_detail.html', context)

    except:
        messages.error(request, "Course Does not Exist.")
        return redirect(index)
"""
@login_required  # Redirect to login if not authenticated
def lecture(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lectures = Lecture.objects.filter(course=course)

    # Check if the user is enrolled
    enrolled = Enroll.objects.filter(course=course, user=request.user).exists()

    if enrolled:
        # Get the first lecture of the course
        first_lecture = lectures.first()

        context = {
            'course': course,
            'lectures': lectures,
            'lecture_selected': first_lecture,  # Pass the first lecture as the selected lecture
        }
        return render(request, 'courses/lecture.html', context)
    else:
        messages.error(request, "You must enroll in this course to access the lectures.")
        return redirect('course_detail', course_slug=course_slug)

@login_required # Redirect to login if not authenticated
def lecture_selected(request, course_slug, lecture_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lectures = Lecture.objects.filter(course=course)
    lecture_selected = get_object_or_404(Lecture, lecture_slug=lecture_slug)

    # Check if the user is enrolled
    enrolled = Enroll.objects.filter(course=course, user=request.user).exists()

    if enrolled:
        context = {
            'course': course,
            'lectures': lectures,
            'lecture_selected': lecture_selected,
        }
        return render(request, 'courses/lecture.html', context)
    else:
        messages.error(request, "You must enroll in this course to access the lectures.")
        return redirect('course_detail', course_slug=course_slug)

@login_required # Redirect to login if not authenticated
def enroll(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    try:
        # Check if the user is already enrolled
        if not Enroll.objects.filter(user=user, course=course).exists():
            Enroll.objects.create(user=user, course=course)
            messages.success(request, "Successfully enrolled in the course.")
        else:
            messages.info(request, "You are already enrolled in this course.")

        # Redirect to the course lectures
        return redirect('lecture', course_slug=course.course_slug)

    except Exception as e:
        messages.error(request, "Couldn't enroll in the course. Please try again later.")
        return redirect('course_detail', course_slug=course.course_slug)
      

@login_required
def enrolled_courses(request):

    try:
        courses = Enroll.objects.filter(user=request.user)
        context = {
            'courses': courses,
        }
        return render(request, 'courses/enrolled_courses.html', context)

    except:
        messages.error(request, "Couldn't Enroll to the course. Please try again later.")
        return redirect(index)
    


@login_required  # Redirect to login if not authenticated
def quiz(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    quiz = get_object_or_404(Quiz, course=course)

    context = {
        'course': course,
        'quiz': quiz,
    }
    return render(request, 'courses/quiz.html', context)

@login_required  # Redirect to login if not authenticated
def submit_quiz(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    quiz = get_object_or_404(Quiz, course=course)

    if request.method == 'POST':
        score = 0
        total_questions = quiz.questions.count()

        for question in quiz.questions.all():
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1

        # Calculate the score as a percentage
        percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0

        # Save the score to the Progress model
        progress, created = Progress.objects.get_or_create(user=request.user, course=course)
        progress.quiz_score = percentage_score
        progress.save()

        messages.success(request, f"You scored {percentage_score:.2f}%!")
        return redirect('course_detail', course_slug=course.course_slug)

    return redirect('course_detail', course_slug=course.course_slug)
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('baseview/',views.baseview, name='baseview'),
    path('course/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),  # Add this line
    path('topic/<slug:topic_slug>/', views.topic_courses, name='topic_courses'),
    path('search/', views.search_courses, name='search_courses'),
    path('course/<slug:course_slug>/lectures/', views.lecture, name='lecture'),
    path('course/<slug:course_slug>/lectures/<slug:lecture_slug>/', views.lecture_selected, name='lecture_selected'),
    path('course/<slug:course_slug>/quiz/', views.quiz, name='quiz'),
    path('course/<slug:course_slug>/quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'), 
    path('logout/', LogoutView.as_view(), name='logout'),
   
    

]
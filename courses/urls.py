from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.login, name='login'),
    path('signup/',views.signup, name='signup'),
    path('baseview/',views.baseview, name='baseview'),
    path('course/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),  # Add this line
    
    
]
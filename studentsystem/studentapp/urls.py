from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('roadmap/', views.roadmap_view, name='roadmap'),
    path('resources/', views.resources_view, name='resources'),
    path('resources/<str:category>/', views.resource_detail_view, name='resource_detail'),
    path('start-roadmap/', views.start_roadmap, name='start_roadmap'),
    path('progress/', views.progress_view, name='progress'),
    path('toggle-task/<int:task_id>/', views.toggle_task, name='toggle_task'),

]

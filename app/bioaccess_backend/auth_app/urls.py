from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('biometric-auth/face/', views.face_auth, name='face_auth'),
    path('biometric-auth/voice/', views.voice_auth, name='voice_auth'),
    path('admin/logs/', views.admin_access_logs, name='admin_logs'),
    path('admin/create-room/', views.create_room, name='create_room'),
]

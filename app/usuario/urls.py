from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path('', views.index, name='index'),
    
    
    
     # URLs de autenticación
    path("solicitar_reset/", views.solicitar_reset, name="solicitar_reset"),
    path("reset_password/<str:token>/", views.reset_password, name="reset_password"),
]
from django.urls import path
from . import views
urlpatterns = [
path("gestionar/", views.gestionar_usuarios, name="gestionar_usuarios"),
path("reservas/gestionar/", views.gestionar_reservas, name="gestionar_reservas"),
path("noticias/", views.listar_noticias, name="listar_noticias"),

path("noticias/eliminar/<int:id_noticia>/", views.eliminar_noticia, name="eliminar_noticia"),

path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
path('vehiculo/<int:pk>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    
path('sorteos/', views.sorteos_list_create, name='sorteos_list_create'),

path('sorteo/<int:sorteo_id>/vehiculos/', views.sorteo_vehiculos, name='sorteo_vehiculos'),

path("reserva/<int:id_reserva>/detalle-pagos/", views.detalle_reserva_con_pagos, name="detalle_reserva_con_pagos"),
path("pago/<int:pago_id>/eliminar/", views.eliminar_pago, name="eliminar_pago"),

]
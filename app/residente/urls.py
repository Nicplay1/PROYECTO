from django.urls import path
from . import views

urlpatterns = [
    path("residente/", views.detalle_residente, name="detalle_residente"),
    
    path("zonas/", views.listar_zonas, name="listar_zonas"),
    path("reservar/<int:id_zona>/", views.crear_reserva, name="crear_reserva"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),  # vista general
    path("reservas/eliminar/<int:id_reserva>/", views.eliminar_reserva, name="eliminar_reserva"),
    path('zonas/<int:id_zona>/fechas-ocupadas/', views.fechas_ocupadas, name='fechas_ocupadas'),
    

    # Detalles de un vehículo y gestión de archivos
    path('vehiculos/<int:vehiculo_id>/', views.detalles, name='detalles'),
    
    path('reserva/<int:id_reserva>/agregar-pago/', views.agregar_pago, name='agregar_pago'),
    
]
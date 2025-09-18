from django import forms
from usuario.models import *


class CambiarRolForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['id_rol']
        labels = {'id_rol': 'Rol'}


class EditarReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["observacion", "estado"]
        labels = {
            "observacion": "Observación",
            "estado": "Estado"
        }
        widgets = {
            "observacion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Escribe una observación..."
            }),
            "estado": forms.Select(attrs={"class": "form-select-modern"})
        }

class NoticiasForm(forms.ModelForm):
    class Meta:
        model = Noticias
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese la descripción'
            }),
        }
        
class VehiculoResidenteForm(forms.ModelForm):
    class Meta:
        model = VehiculoResidente
        fields = ['documentos']
        widgets = {
            'documentos': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class SorteoForm(forms.ModelForm):
    tipo_residente_propietario = forms.BooleanField(
        required=False,  # Permite que quede vacío (null)
        label='Propietario',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Sorteo
        fields = ['tipo_residente_propietario', 'fecha_inicio', 'hora_sorteo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_sorteo': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'hora_sorteo': 'Hora del Sorteo',
        }
        

class EstadoPagoForm(forms.ModelForm):
    class Meta:
        model = PagosReserva
        fields = ["estado"]
        widgets = {
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

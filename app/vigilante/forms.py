from django import forms
from usuario.models import *
from django.core.exceptions import ValidationError

class BuscarPlacaForm(forms.Form):
    placa = forms.CharField(
        max_length=10,
        label="Buscar Placa",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo: ABC123'})
    )

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombres', 'apellidos', 'celular', 'documento', 'tipo_vehiculo', 'placa']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class DetalleParqueaderoForm(forms.ModelForm):
    class Meta:
        model = DetallesParqueadero
        fields = ['tipo_propietario', 'hora_salida', 'id_parqueadero']
        widgets = {
            'tipo_propietario': forms.Select(attrs={'class': 'form-control'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'id_parqueadero': forms.Select(attrs={'class': 'form-control'}),
        }
        
class RegistroCorrespondenciaForm(forms.ModelForm):
    class Meta:
        model = RegistroCorrespondencia
        fields = ['tipo', 'descripcion', 'fecha_registro', 'cod_vigilante']
        widgets = {
            'fecha_registro': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clase form-control a todos los campos
        for field_name, field in self.fields.items():
            if field_name != 'fecha_registro':  # ya tiene form-control
                field.widget.attrs['class'] = 'form-control'

        # Filtrar cod_vigilante
        self.fields['cod_vigilante'].queryset = Usuario.objects.filter(id_rol=4)

class BuscarResidenteForm(forms.Form):
    torre = forms.IntegerField(label="Torre", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    apartamento = forms.IntegerField(label="Apartamento", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    

class RegistrarPaqueteForm(forms.Form):
    apartamento = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control-modern'})
    )
    torre = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control-modern'})
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control-modern'})
    )
    cod_usuario_recepcion = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        empty_label="Seleccione vigilante",
        widget=forms.Select(attrs={'class': 'form-control-modern'}),
        label="Vigilante de Recepción"
    )


class EntregaPaqueteForm(forms.Form):
    id_paquete = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'entregaPaqueteId'})  # 👈 fijo
    )

    nombre_residente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control-modern'}),
        label="Recibido por"
    )

    cod_usuario_entrega = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(id_rol=4),
        empty_label="Seleccione vigilante",
        widget=forms.Select(attrs={'class': 'form-control-modern'}),
        label="Vigilante que Entrega"
    )
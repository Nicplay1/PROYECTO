from django import forms
from usuario.models import *


class DetalleResidenteForm(forms.ModelForm):
    class Meta:
        model = DetalleResidente
        fields = ['propietario', 'apartamento', 'torre']
        widgets = {
            'propietario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'apartamento': forms.NumberInput(attrs={'class': 'form-control'}),
            'torre': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['hora_inicio', 'hora_fin', 'fecha_uso']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'fecha_uso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class VehiculoResidenteForm(forms.ModelForm):
    class Meta:
        model = VehiculoResidente
        fields = ['placa', 'tipo_vehiculo', 'activo', 'documentos']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_vehiculo': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'documentos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ArchivoVehiculoForm(forms.ModelForm):
    class Meta:
        model = ArchivoVehiculo
        fields = ['idTipoArchivo', 'archivo', 'fechaVencimiento']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fechaVencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        
class PagosReservaForm(forms.ModelForm):
    class Meta:
        model = PagosReserva
        fields = ["id_reserva", "archivo_1", "archivo_2", "estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # estilos Bootstrap
        self.fields["archivo_1"].widget.attrs.update({"class": "form-control"})
        self.fields["archivo_2"].widget.attrs.update({"class": "form-control"})
        self.fields["estado"].widget.attrs.update({"class": "form-control"})
        self.fields["id_reserva"].widget.attrs.update({"class": "form-control"})
from django import forms
from .models import Usuario
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        }),
        label="Contraseña"
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        }),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = Usuario
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'correo', 'telefono', 'celular', 'contraseña'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese sus nombres'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese sus apellidos'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Seleccione su tipo de documento'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su número de documento'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su correo electrónico'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su teléfono'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su celular'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar_contraseña = cleaned_data.get("confirmar_contraseña")

        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data




class LoginForm(forms.Form):
    numero_documento = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Documento de Identidad"
    )
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )

class UsuarioUpdateForm(forms.ModelForm):
    # contraseña no es obligatoria
    contraseña = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['correo', 'celular', 'telefono', 'contraseña']
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nueva_contrasena = self.cleaned_data.get('contraseña')

        if nueva_contrasena:  # solo actualiza si se ingresa algo
            usuario.contraseña = make_password(nueva_contrasena)
        else:
            # si no hay contraseña nueva, mantenemos la que ya estaba
            usuario.contraseña = Usuario.objects.get(pk=usuario.pk).contraseña

        if commit:
            usuario.save()
        return usuario
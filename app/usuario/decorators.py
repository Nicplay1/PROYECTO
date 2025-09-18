from functools import wraps
from django.shortcuts import redirect
from .models import Usuario  # importa tu modelo de usuario

def login_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')

        if not usuario_id:
            return redirect('login')

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            request.usuario = usuario
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

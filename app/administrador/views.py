from django.shortcuts import render, redirect, get_object_or_404
from usuario.models import *
from usuario.decorators import login_requerido
from django.contrib import messages
from .forms import *
import random
from django.core.mail import send_mail

# Create your views here.
@login_requerido
def gestionar_usuarios(request):
    usuarios = Usuario.objects.select_related("id_rol").all()

    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        form = CambiarRolForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f" Rol de {usuario.nombres} actualizado correctamente.")
            return redirect("gestionar_usuarios")
        else:
            messages.error(request, " Error al actualizar el rol. Verifica los datos.")
            return redirect("gestionar_usuarios")
    else:
        form = CambiarRolForm()

    return render(request, "administrador/gestionar_usuarios.html", {
        "usuarios": usuarios,
        "form": form,
        "roles": Rol.objects.all()
    })
    
@login_requerido
def gestionar_reservas(request):
    reservas = Reserva.objects.select_related("cod_usuario", "cod_zona").all()

    if request.method == "POST":
        reserva_id = request.POST.get("reserva_id")
        reserva = get_object_or_404(Reserva, pk=reserva_id)
        form = EditarReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, f" Reserva {reserva.id_reserva} actualizada correctamente.")
            return redirect("gestionar_reservas")
    else:
        form = EditarReservaForm()

    return render(request, "administrador/gestionar_reservas.html", {
        "reservas": reservas,
        "form": form
    })
    

@login_requerido
def detalle_reserva_con_pagos(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)
    pagos = PagosReserva.objects.filter(id_reserva=reserva)

    form_reserva = EditarReservaForm(instance=reserva)

    if request.method == "POST":
        if "reserva_id" in request.POST:  # Guardar toda la reserva
            form_reserva = EditarReservaForm(request.POST, instance=reserva)
            if form_reserva.is_valid():
                form_reserva.save()
                messages.success(request, f"Reserva {reserva.id_reserva} actualizada correctamente.")
                return redirect("detalle_reserva_con_pagos", id_reserva=id_reserva)
        elif "pago_id" in request.POST:  # Editar estado de pago
            pago_id = request.POST.get("pago_id")
            pago = get_object_or_404(PagosReserva, pk=pago_id)
            form_pago = EstadoPagoForm(request.POST, instance=pago)
            if form_pago.is_valid():
                form_pago.save()
                messages.success(request, f"Pago {pago.id_pago} actualizado correctamente.")
                return redirect("detalle_reserva_con_pagos", id_reserva=id_reserva)

    # Adjuntar form_estado a cada pago
    for pago in pagos:
        pago.form_estado = EstadoPagoForm(instance=pago)

    return render(
        request,
        "administrador/reservas/detalle_reserva_pagos.html",
        {
            "reserva": reserva,
            "pagos": pagos,
            "form_reserva": form_reserva
        },
    )


@login_requerido
def eliminar_pago(request, pago_id):
    pago = get_object_or_404(PagosReserva, pk=pago_id)
    reserva_id = pago.id_reserva.id_reserva
    if request.method == "POST":
        pago.delete()
        messages.success(request, f"Pago {pago_id} eliminado correctamente.")
        return redirect("detalle_reserva_con_pagos", id_reserva=reserva_id)


@login_requerido
def listar_noticias(request):
    noticias = Noticias.objects.all().order_by("-fecha_publicacion")

    # Crear Noticia
    if request.method == "POST" and "crear" in request.POST:
        form = NoticiasForm(request.POST)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.cod_usuario = request.usuario
            noticia.save()
            messages.success(request, "Noticia creada exitosamente ")
            return redirect("listar_noticias")
    # Editar Noticia
    elif request.method == "POST" and "editar" in request.POST:
        noticia = get_object_or_404(Noticias, id_noticia=request.POST.get("id_noticia"))
        form = NoticiasForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, "Noticia actualizada correctamente ")
            return redirect("listar_noticias")

    else:
        form = NoticiasForm()

    return render(request, "administrador/noticias/listar.html", {
        "noticias": noticias,
        "form": form,
    })

# EDITAR

# ELIMINAR
@login_requerido
def eliminar_noticia(request, id_noticia):
    noticia = get_object_or_404(Noticias, id_noticia=id_noticia)
    noticia.delete()
    messages.success(request, "Noticia eliminada ")
    return redirect("listar_noticias")


def lista_vehiculos(request):
    vehiculos = VehiculoResidente.objects.all()
    return render(request, 'administrador/vehiculos/lista_vehiculos.html', {'vehiculos': vehiculos})

# Vista de detalle de un vehículo y edición de 'documentos'
def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(VehiculoResidente, pk=pk)
    archivos = ArchivoVehiculo.objects.filter(idVehiculo=vehiculo)

    if request.method == 'POST':
        form = VehiculoResidenteForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, " Documnetacion validada ")
            return redirect('detalle_vehiculo', pk=vehiculo.pk)
    else:
        form = VehiculoResidenteForm(instance=vehiculo)

    context = {
        'vehiculo': vehiculo,
        'archivos': archivos,
        'form': form,
    }
    return render(request, 'administrador/vehiculos/detalles_vehiculo.html', context)


def sorteos_list_create(request):
    sorteos = Sorteo.objects.all().order_by('-fecha_creado')

    if request.method == 'POST':
        # Crear sorteo
        if 'crear_sorteo' in request.POST:
            form = SorteoForm(request.POST)
            if form.is_valid():
                sorteo = form.save()
                messages.success(request, "Sorteo fue creado correctamente.")
                return redirect('sorteos_list_create')

        # Liberar parqueaderos propietarios
        elif 'liberar_propietarios' in request.POST:
            parqueaderos = Parqueadero.objects.filter(comunal=True, estado=True)
            parqueaderos.update(estado=False)
            messages.success(request, "Se liberaron todos los parqueaderos de propietarios.")

        # Liberar parqueaderos arrendatarios
        elif 'liberar_arrendatarios' in request.POST:
            parqueaderos = Parqueadero.objects.filter(comunal=False, estado=True)
            parqueaderos.update(estado=False)
            messages.success(request, "Se liberaron todos los parqueaderos de arrendatarios.")

        return redirect('sorteos_list_create')

    else:
        form = SorteoForm()

    context = {
        'sorteos': sorteos,
        'form': form,
    }
    return render(request, 'administrador/sorteo/sorteos.html', context)


def sorteo_vehiculos(request, sorteo_id):
    # Obtener el sorteo
    sorteo = get_object_or_404(Sorteo, id_sorteo=sorteo_id)

    # Filtrar residentes según tipo de sorteo
    if sorteo.tipo_residente_propietario is True:
        residentes = DetalleResidente.objects.filter(propietario=True)
        parqueaderos = Parqueadero.objects.filter(comunal=True, estado=False)
    elif sorteo.tipo_residente_propietario is False:
        residentes = DetalleResidente.objects.filter(propietario=False)
        parqueaderos = Parqueadero.objects.filter(comunal=False, estado=False)
    else:
        residentes = DetalleResidente.objects.all()
        parqueaderos = Parqueadero.objects.filter(estado=False)

    # Filtrar vehículos válidos
    usuarios_residentes = residentes.values_list('cod_usuario', flat=True)
    vehiculos = VehiculoResidente.objects.filter(
        documentos=True,
        cod_usuario__in=usuarios_residentes
    ).select_related('cod_usuario')

    # Realizar sorteo
    if request.method == 'POST' and 'realizar_sorteo' in request.POST:
        if len(residentes) < 1:
            messages.error(request, "No hay suficientes residentes para realizar el sorteo.")
        elif len(parqueaderos) < 1:
            messages.error(request, "No hay suficientes parqueaderos disponibles para el sorteo.")
        else:
            ganadores_residentes = random.sample(list(residentes), 1)
            parqueaderos_disponibles = random.sample(list(parqueaderos), 1)

            for i, residente in enumerate(ganadores_residentes):
                parqueadero = parqueaderos_disponibles[i]

                # Crear registro de ganador
                ganador = GanadorSorteo.objects.create(
                    id_sorteo=sorteo,
                    id_detalle_residente=residente,
                    id_parqueadero=parqueadero
                )

                # Cambiar estado parqueadero
                parqueadero.estado = True
                parqueadero.save()

                # Buscar vehículo del residente
                vehiculo = VehiculoResidente.objects.filter(
                    cod_usuario=residente.cod_usuario,
                    documentos=True
                ).first()

                # Enviar correo
                if residente.cod_usuario.correo:
                    try:
                        send_mail(
                            subject="Ganador de sorteo - Altos de Fontibón",
                            message=(
                                f"Estimado(a) {residente.cod_usuario.nombres} {residente.cod_usuario.apellidos},\n\n"
                                f"¡Felicitaciones! Has resultado ganador en el sorteo de parqueaderos.\n\n"
                                f"Parqueadero asignado: {parqueadero.numero_parqueadero}\n"
                                f"Vehículo: {vehiculo.placa if vehiculo else 'No registrado'}\n\n"
                                "Atentamente.\nAdministración Altos de Fontibón"
                            ),
                            from_email="altosdefontibon.cr@gmail.com",
                            recipient_list=[residente.cod_usuario.correo],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Error enviando correo a {residente.cod_usuario.correo}: {e}")

            messages.success(request, "¡Sorteo realizado con éxito! Los ganadores han sido notificados por correo.")
            return redirect('sorteo_vehiculos', sorteo_id=sorteo.id_sorteo)

    context = {
        'sorteo': sorteo,
        'residentes': residentes,
        'parqueaderos': parqueaderos,
        'vehiculos': vehiculos,
    }
    return render(request, 'administrador/sorteo/sorteo_vehiculos.html', context)

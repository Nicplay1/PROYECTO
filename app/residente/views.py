from django.shortcuts import render, redirect,get_object_or_404
from usuario.models import *
from usuario.decorators import login_requerido
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
import datetime


# Create your views here.
@login_requerido
def detalle_residente(request):
    """
    Si el residente ya tiene detalle → mostrar últimas 2 noticias.
    Si no → mostrar formulario para registrar detalles.
    """
    usuario = request.usuario
    detalle = DetalleResidente.objects.filter(cod_usuario=usuario).first()

    # Si ya tiene detalle → mostrar las noticias
    if detalle:
        noticias = Noticias.objects.all().order_by("-fecha_publicacion")[:2]  # 🔥 Solo las 2 últimas
        return render(request, "residente/detalles_residente/noticias.html", {
            "usuario": usuario,
            "detalle": detalle,
            "noticias": noticias,
        })

    # Si no tiene → permitir registrar
    if request.method == "POST":
        form = DetalleResidenteForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.cod_usuario = usuario
            detalle.save()
            messages.success(request, "Detalles de residente registrados correctamente.")
            return redirect("detalle_residente")  # redirige para ahora sí ver noticias
    else:
        form = DetalleResidenteForm()

    return render(
        request,
        "residente/detalles_residente/registrar_detalle_residente.html",
        {"form": form}
    )


@login_requerido
def listar_zonas(request):
    zonas = ZonaComun.objects.all()
    return render(request, "residente/zonas_comunes/listar_zonas.html", {"zonas": zonas})

# Crear reserva
@login_requerido
def crear_reserva(request, id_zona):
    zona = get_object_or_404(ZonaComun, pk=id_zona)

    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            fecha_uso = form.cleaned_data['fecha_uso']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_fin = form.cleaned_data['hora_fin']

            # 🔹 Validación de fecha ocupada solo para zonas 6, 12 y 13
            if zona.id_zona in [6, 12, 13] and Reserva.objects.filter(cod_zona=zona, fecha_uso=fecha_uso).exists():
                messages.error(request, "Ya existe una reserva para esta fecha en la zona seleccionada.")
            else:
                reserva = form.save(commit=False)
                reserva.cod_usuario = request.usuario
                reserva.cod_zona = zona
                reserva.estado = "En espera"
                reserva.forma_pago = "Efectivo"

                # ----------------------------
                # 🔹 CÁLCULO DEL PAGO
                # ----------------------------
                total_a_pagar = 0

                if hora_inicio and hora_fin:
                    # Convertir a datetime para calcular duración
                    dummy_date = datetime.date(2000, 1, 1)
                    inicio_dt = datetime.datetime.combine(dummy_date, hora_inicio)
                    fin_dt = datetime.datetime.combine(dummy_date, hora_fin)

                    # Si cruza medianoche
                    if fin_dt < inicio_dt:
                        fin_dt += datetime.timedelta(days=1)

                    duracion_minutos = (fin_dt - inicio_dt).total_seconds() / 60

                    if zona.tipo_pago == "Por hora":
                        total_a_pagar = (duracion_minutos / 60) * float(zona.tarifa_base)

                    elif zona.tipo_pago == "Franja horaria":
                        franja_minutos = 60
                        if zona.nombre_zona == "Lavandería":
                            franja_minutos = 90
                        total_a_pagar = (duracion_minutos / franja_minutos) * float(zona.tarifa_base)

                    elif zona.tipo_pago == "Evento":
                        total_a_pagar = float(zona.tarifa_base)

                # Guardamos el valor en la reserva
                reserva.valor_pago = total_a_pagar
                reserva.save()

                messages.success(request, f"Reserva creada correctamente. Total a pagar: ${total_a_pagar:,.0f}")

                request.session["mostrar_alerta_pago"] = True
                return redirect("mis_reservas")
        else:
            messages.error(request, "Error al crear la reserva. Revisa los datos.")
    else:
        form = ReservaForm()

    return render(request, "residente/zonas_comunes/crear_reserva.html", {
        "form": form,
        "zona": zona
    })


@login_requerido
def fechas_ocupadas(request, id_zona):
    zona = get_object_or_404(ZonaComun, pk=id_zona)

    # Solo marcar "ocupado" si la zona pertenece a los ids 6, 12 o 13
    if zona.id_zona in [6, 12, 13]:
        reservas = Reserva.objects.filter(cod_zona=zona).values_list("fecha_uso", flat=True)
    else:
        reservas = []  # las demás zonas siempre aparecen libres

    return JsonResponse({"fechas": list(reservas)})

# Detalle de la reserva
@login_requerido
def mis_reservas(request):
    usuario = request.usuario
    reservas = Reserva.objects.filter(cod_usuario=usuario).select_related("cod_zona")

    mostrar_alerta = request.session.pop("mostrar_alerta_pago", False)

    return render(
        request,
        "residente/zonas_comunes/detalle_reserva.html",
        {"reservas": reservas, "mostrar_alerta": mostrar_alerta}
    )


@login_requerido
def eliminar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)

    # Validar permisos: si es residente, solo puede eliminar sus propias reservas
    if request.usuario.id_rol.id_rol == 2 and reserva.cod_usuario != request.usuario:
        messages.error(request, " No puedes eliminar esta reserva.")
        return redirect("mis_reservas")

    if request.method == "POST":
        reserva.delete()
        messages.success(request, f" Reserva {id_reserva} eliminada correctamente.")

        # Redirección según el rol
        if request.usuario.id_rol.id_rol == 3:  # Admin
            return redirect("gestionar_reservas")
        return redirect("mis_reservas")

    # Si alguien intenta entrar por GET, redirigimos con error
    messages.error(request, " Operación no permitida.")
    if request.usuario.id_rol.id_rol == 3:
        return redirect("gestionar_reservas")
    return redirect("mis_reservas")
    

@login_requerido
def detalles(request, vehiculo_id):
    vehiculo = get_object_or_404(VehiculoResidente, pk=vehiculo_id)
    archivos = ArchivoVehiculo.objects.filter(idVehiculo=vehiculo)
   

    if request.method == 'POST':
        form = ArchivoVehiculoForm(request.POST, request.FILES)  # importante request.FILES
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.idVehiculo = vehiculo
            archivo.save()
            messages.success(request, "Archivo registrado correctamente.")
            return redirect('detalles', vehiculo_id=vehiculo.id_vehiculo_residente)
    else:
        form = ArchivoVehiculoForm()

    return render(request, 'residente/vehiculos/detalles.html', {
        'vehiculo': vehiculo,
        'archivos': archivos,
        'form': form
    })
    

def agregar_pago(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)
    pago_actual = PagosReserva.objects.filter(id_reserva=reserva).order_by("-id_pago").first()

    form = None  

    if request.method == "POST":
        if pago_actual and not pago_actual.estado and not pago_actual.archivo_2:
            # subir archivo_2
            form = PagosReservaForm(request.POST, request.FILES, instance=pago_actual)
            if form.is_valid():
                pago = form.save(commit=False)
                pago.estado = False
                pago.save()
                # guardamos alerta en sesión
                request.session["mostrar_alerta"] = "validando_pago"
                return redirect("agregar_pago", id_reserva=reserva.id_reserva)

        else:
            # nuevo pago con archivo_1
            form = PagosReservaForm(request.POST, request.FILES)
            if form.is_valid():
                pago = form.save(commit=False)
                pago.id_reserva = reserva
                pago.estado = False
                pago.save()
                # guardamos alerta en sesión
                request.session["mostrar_alerta"] = "primer_pago"
                return redirect("agregar_pago", id_reserva=reserva.id_reserva)

    else:  # GET
        if pago_actual and not pago_actual.estado and not pago_actual.archivo_2:
            # ya subió archivo_1 → ocultar archivo_1, mostrar archivo_2
            form = PagosReservaForm(instance=pago_actual)
            form.fields["archivo_1"].widget = forms.HiddenInput()
            form.fields["estado"].widget = forms.HiddenInput()
            form.fields["id_reserva"].widget = forms.HiddenInput()
            form.fields["archivo_2"].widget = forms.FileInput(attrs={"class": "form-control"})

        elif pago_actual and not pago_actual.estado and pago_actual.archivo_2:
            # ya subió ambos comprobantes pero sigue pendiente
            form = None

        elif pago_actual and pago_actual.estado:
            # ya aprobado → no hay más formulario
            form = None

        else:
            # nuevo pago con archivo_1
            form = PagosReservaForm(initial={"id_reserva": reserva.id_reserva})
            form.fields["archivo_2"].widget = forms.HiddenInput()
            form.fields["estado"].widget = forms.HiddenInput()
            form.fields["id_reserva"].widget = forms.HiddenInput()

    # 👇 Recuperamos y borramos la alerta de sesión (solo se muestra una vez)
    mostrar_alerta = request.session.pop("mostrar_alerta", None)

    pagos = reserva.pagosreserva_set.all()

    return render(
        request,
        "residente/zonas_comunes/pago_reserva.html",
        {
            "form": form,
            "reserva": reserva,
            "pagos": pagos,
            "pago_actual": pago_actual,
            "mostrar_alerta": mostrar_alerta,
        },
    )

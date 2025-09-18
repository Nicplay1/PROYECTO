from django.shortcuts import render, redirect, get_object_or_404
from usuario.models import *
from .forms import *
from django.contrib import messages
from django.utils import timezone
from random import choice
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from usuario.decorators import login_requerido
from django.core.mail import send_mail
from django.urls import reverse
from .models import *
from datetime import datetime



def registrar_parqueadero(request):
    query = request.GET.get("placa", "").upper()

    registros = DetallesParqueadero.objects.select_related(
        "id_visitante", "id_vehiculo_residente", "id_parqueadero"
    ).order_by('-id_detalle')

    placa_encontrada = None
    mostrar_formulario = False
    mostrar_modal_residente = False   # ✅ inicializar aquí
    form = None

    # POST visitante normal
    if request.method == "POST" and "guardar_visitante" in request.POST:
        form = VisitanteForm(request.POST)
        if form.is_valid():
            visitante = form.save()
            
            parqueaderos_disponibles = Parqueadero.objects.filter(estado=False)
            if parqueaderos_disponibles.exists():
                parqueadero_default = choice(parqueaderos_disponibles)
                parqueadero_default.estado = True
                parqueadero_default.save()
            else:
                messages.error(request, "No hay parqueadero disponible.")
                return redirect('registrar_detalle_parqueadero')
            
            DetallesParqueadero.objects.create(
                tipo_propietario="Visitante",
                id_visitante=visitante,
                id_vehiculo_residente=None,
                id_parqueadero=parqueadero_default,
                hora_llegada=timezone.localtime().time()
            )
            messages.success(request, f"Visitante y detalle creados con placa {visitante.placa}")
            return redirect('registrar_detalle_parqueadero')

    # GET Buscar placa
    if query:
        vehiculo = VehiculoResidente.objects.filter(placa=query).first()
        visitante = Visitante.objects.filter(placa=query).first()
        hora_actual = timezone.localtime().time()

        if vehiculo:
            ganador = GanadorSorteo.objects.filter(
                id_detalle_residente__cod_usuario__vehiculoresidente__placa=vehiculo.placa
            ).select_related("id_parqueadero").first()

            if not ganador:
                messages.error(request, f"El vehículo con placa {query} no es ganador del sorteo.")
            else:
                parqueadero_ganador = ganador.id_parqueadero
                placa_encontrada = vehiculo.placa

                # 🔔 Mostrar modal solo si no se ha seleccionado acción
                if not request.GET.get("accion"):
                    mostrar_modal_residente = True

                # Acción Entrada
                if request.GET.get("accion") == "entrada":
                    if not parqueadero_ganador.estado:
                        parqueadero_ganador.estado = True
                        parqueadero_ganador.save()

                    DetallesParqueadero.objects.create(
                        tipo_propietario="Residente",
                        id_vehiculo_residente=vehiculo,
                        id_visitante=None,
                        id_parqueadero=parqueadero_ganador,
                        hora_llegada=hora_actual,
                        hora_salida=None
                    )
                    messages.success(request, f"Entrada registrada para residente con placa {placa_encontrada}")

                # Acción Salida
                elif request.GET.get("accion") == "salida":
                    DetallesParqueadero.objects.create(
                        tipo_propietario="Residente",
                        id_vehiculo_residente=vehiculo,
                        id_visitante=None,
                        id_parqueadero=parqueadero_ganador,
                        hora_llegada=None,
                        hora_salida=hora_actual
                    )
                    parqueadero_ganador.estado = False
                    parqueadero_ganador.save()
                    messages.success(request, f"Salida registrada para residente con placa {placa_encontrada}")

        elif visitante:
            parqueaderos_disponibles = Parqueadero.objects.filter(estado=False)
            if parqueaderos_disponibles.exists():
                parqueadero_default = choice(parqueaderos_disponibles)
                parqueadero_default.estado = True
                parqueadero_default.save()

                DetallesParqueadero.objects.create(
                    tipo_propietario="Visitante",
                    id_visitante=visitante,
                    id_vehiculo_residente=None,
                    id_parqueadero=parqueadero_default,
                    hora_llegada=hora_actual
                )
                placa_encontrada = visitante.placa
                messages.success(request, f"Detalle creado para visitante con placa {placa_encontrada}")
            else:
                messages.error(request, "No hay parqueadero disponible para visitantes.")
        else:
            mostrar_formulario = True
            form = VisitanteForm(initial={"placa": query})

    # Calcular tiempo y valor
    for detalle in registros:
        if detalle.tipo_propietario == "Residente":
            detalle.valor_pago = 0
            detalle.tiempo_total = None
        elif detalle.hora_llegada and detalle.hora_salida:
            llegada_dt = datetime.combine(detalle.registro, detalle.hora_llegada)
            salida_dt = datetime.combine(detalle.registro, detalle.hora_salida)
            duracion = salida_dt - llegada_dt
            horas = duracion.total_seconds() / 3600
            detalle.tiempo_total = duracion
            detalle.valor_pago = round(max(horas, 1) * 2000, 2)
        else:
            detalle.tiempo_total = None
            detalle.valor_pago = None

    return render(request, "vigilante/vigilante.html", {
    "registros": registros,
    "placa_encontrada": placa_encontrada,
    "mostrar_formulario": mostrar_formulario,
    "mostrar_modal_residente": mostrar_modal_residente,
    "form": form
})

def poner_hora_salida(request, id_detalle):
    detalle = get_object_or_404(DetallesParqueadero, id_detalle=id_detalle)
    if not detalle.hora_salida:
        detalle.hora_salida = timezone.localtime().time()
        detalle.save()
        messages.success(request, "Hora de salida registrada.")
    else:
        messages.info(request, "Este registro ya tiene hora de salida.")
    return redirect('registrar_detalle_parqueadero')

def realizar_pago(request, id_detalle):
    detalle = get_object_or_404(DetallesParqueadero, id_detalle=id_detalle)
    if detalle.hora_salida and detalle.pago is None:
        llegada_dt = datetime.combine(detalle.registro, detalle.hora_llegada)
        salida_dt = datetime.combine(detalle.registro, detalle.hora_salida)
        duracion = salida_dt - llegada_dt
        horas = duracion.total_seconds() / 3600
        detalle.pago = round(max(horas, 1) * 2000, 2)
        detalle.tiempo_total = duracion
        detalle.save()

        # Liberar parqueadero
        parqueadero = detalle.id_parqueadero
        parqueadero.estado = False
        parqueadero.save()

        messages.success(request, f"Pago realizado: {detalle.pago} pesos")
    return redirect('registrar_detalle_parqueadero')

@login_requerido
def registro_correspondencia_view(request):
    registros = RegistroCorrespondencia.objects.all()
    form = RegistroCorrespondenciaForm(request.POST or None)

    if request.method == 'POST' and 'crear_registro' in request.POST:
        if form.is_valid():
            registro = form.save()

            residentes = Usuario.objects.filter(id_rol=2, estado="Activo")  

            for residente in residentes:
                try:
                    send_mail(
                        subject="Nuevo recibo en porteria - Altos de Fontibón",
                        message=(
                            f"Estimado residente \n\n"
                            f"Te informamos que se ha registrado un nuevo recibo en la porteria del conjunto \n\n"
                            f"Descripción: {registro.descripcion}\n"
                            f"Fecha: {registro.fecha_registro.strftime('%d/%m/%Y %H:%M')}\n\n"
                            f"Por favor acérquese a reclamarlo en porteria\n\n"
                            f"Atentamente.\nAdministración: Altos de Fontibón"
                        ),
                        from_email="altosdefontibon.cr@gmail.com",
                        recipient_list=[residente.correo],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error enviando a {residente.correo}: {e}")

            messages.success(request, "Registro de correspondencia creado y notificación enviada a los residentes.")
            return redirect('registro_correspondencia')

    form_entrega = BuscarResidenteForm()  
    return render(request, 'vigilante/resibos.html', {
        'registros': registros,
        'form': form,
        'form_entrega': form_entrega
    })

@login_requerido
def registrar_entrega_view(request):
    if request.method == "POST":
        # Registrar entrega
        if request.POST.get("accion") == "registrar_entrega":
            id_corres = request.POST.get("id_correspondencia")
            id_res = request.POST.get("id_residente")
            residente = get_object_or_404(DetalleResidente, id_detalle_residente=id_res)
            correspondencia = get_object_or_404(RegistroCorrespondencia, id_correspondencia=id_corres)

            if not EntregaCorrespondencia.objects.filter(idDetalles_residente=residente, idCorrespondecia=correspondencia).exists():
                EntregaCorrespondencia.objects.create(
                    idUsuario=request.usuario,
                    idCorrespondecia=correspondencia,
                    idDetalles_residente=residente,
                    fechaEntrega=timezone.now()
                )
            return JsonResponse({'success': True})

        # Filtrado AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            torre = request.POST.get("torre")
            apartamento = request.POST.get("apartamento")
            try:
                residente = DetalleResidente.objects.get(torre=torre, apartamento=apartamento)
            except DetalleResidente.DoesNotExist:
                residente = None

            registros = []
            if residente:
                entregas_residente = EntregaCorrespondencia.objects.filter(idDetalles_residente=residente)
                entregados_ids = entregas_residente.values_list('idCorrespondecia_id', flat=True)
                registros = RegistroCorrespondencia.objects.exclude(id_correspondencia__in=entregados_ids)

            html = render_to_string('vigilante/partial_registros.html', {
                'registros': registros,
                'residente': residente
            })
            return JsonResponse({'html': html})

    return JsonResponse({'success': False})


def buscar_paquete(request):
    apartamento = request.GET.get('apartamento')
    torre = request.GET.get('torre')

    # Solo mostrar paquetes no entregados
    paquetes = Paquete.objects.filter(fecha_entrega__isnull=True)

    if apartamento:
        paquetes = paquetes.filter(apartamento=apartamento)
    if torre:
        paquetes = paquetes.filter(torre=torre)

    resultados = []
    for p in paquetes:
        resultados.append({
            "id": p.id_paquete,
            "fecha_recepcion": p.fecha_recepcion.strftime("%d/%m/%Y"),
            "vigilante_recepcion": f"{p.cod_usuario_recepcion.nombres} {p.cod_usuario_recepcion.apellidos}",
        })

    return JsonResponse({"resultados": resultados})


def correspondencia(request):
    paquetes = Paquete.objects.select_related('cod_usuario_recepcion', 'cod_usuario_entrega')\
                              .order_by("-fecha_recepcion")

    vigilantes = Usuario.objects.filter(id_rol=4, estado='Activo').order_by('nombres')

    registrar_form = RegistrarPaqueteForm()
    entrega_form = EntregaPaqueteForm()

    return render(request, "vigilante/correspondencia.html", {
        "paquetes": paquetes,
        "vigilantes": vigilantes,
        "registrar_form": registrar_form,
        "entrega_form": entrega_form,
    })


def registrar_paquete(request):
    if request.method == 'POST':
        form = RegistrarPaqueteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            paquete = Paquete(
                apartamento=data['apartamento'],
                torre=data['torre'],
                descripcion=data.get('descripcion') or None,
                fecha_recepcion=timezone.now(),
                cod_usuario_recepcion=data['cod_usuario_recepcion']
            )
            paquete.save()

            detalle = DetalleResidente.objects.filter(
                torre=paquete.torre,
                apartamento=paquete.apartamento
            ).select_related("cod_usuario").first()

            if detalle and detalle.cod_usuario and detalle.cod_usuario.correo:
                try:
                    send_mail(
                        subject="Nuevo paquete en porteria - Altos de Fontibón",
                        message=(
                            f"Estimado(a) {detalle.cod_usuario.nombres},\n\n"
                            f"Se ha registrado un paquete para su apartamento {paquete.apartamento}, Torre {paquete.torre}\n\n"
                            f"Descripción: {paquete.descripcion or 'Sin descripción'}\n\n"
                            "Puede acercarse a porteria a reclamarlo\n\n"
                            "Atentamente.\nAdministración: Altos de Fontibón"
                        ),
                        from_email="altosdefontibon.cr@gmail.com",
                        recipient_list=[detalle.cod_usuario.correo],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error enviando correo a {detalle.cod_usuario.correo}: {e}")
            else:
                print("No se encontró residente con ese apartamento y torre.")

            messages.success(request, "Paquete registrado correctamente y notificación enviada.")
        else:
            messages.error(request, "Revise los datos del formulario.")

    return redirect(reverse('correspondencia'))


def entregar_paquete(request):
    if request.method == 'POST':
        form = EntregaPaqueteForm(request.POST)
        if form.is_valid():
            id_paquete = form.cleaned_data['id_paquete']
            nombre_residente = form.cleaned_data['nombre_residente']
            vigilante_entrega = form.cleaned_data['cod_usuario_entrega']

            paquete = get_object_or_404(Paquete, pk=id_paquete)
            paquete.nombre_residente = nombre_residente
            paquete.cod_usuario_entrega = vigilante_entrega
            paquete.fecha_entrega = timezone.now()
            paquete.save()

            messages.success(request, "Entrega registrada correctamente.")
        else:
            messages.error(request, "Revise los datos del formulario de entrega.")
    return redirect(reverse('correspondencia'))

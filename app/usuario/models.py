from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Rol'

    def __str__(self):
        return self.nombre_rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    tipo_documento = models.CharField(
        max_length=20,
        choices=[('CC', 'CC'), ('CE', 'CE'), ('TI', 'TI'), ('Pasaporte', 'Pasaporte')]
    )
    numero_documento = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=13)
    celular = models.CharField(max_length=13)
    estado = models.CharField(max_length=10, default='Activo')
    contraseña = models.CharField(max_length=250, null=True, blank=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='ID_rol', default=1)
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_expira = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "Usuario"   # <- Esto fuerza a Django a usar esa tabla
        managed = False  # <- Esto le dice a Django que NO maneje migraciones
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"    

    def generar_token_reset(self):
        token = str(uuid.uuid4())
        self.reset_token = token
        self.reset_token_expira = timezone.now() + timedelta(hours=1)
        self.save()
        return token

    def token_es_valido(self, token):
        return (
            self.reset_token == token and
            self.reset_token_expira and
            timezone.now() < self.reset_token_expira
        )


class ZonaComun(models.Model):
    # Campo para la clave primaria, mapeado a 'id_zona'
    id_zona = models.AutoField(primary_key=True)
    
    # Campo para el nombre de la zona, con un máximo de 20 caracteres
    nombre_zona = models.CharField(max_length=20, null=False)
    
    # Campo para la capacidad de la zona, de tipo entero
    capacidad = models.IntegerField(null=False)
    
    # Campo para el tipo de pago, usando una lista de opciones predefinidas
    tipo_pago = models.CharField(
        max_length=20,
        choices=[
            ('Por hora', 'Por hora'),
            ('Franja horaria', 'Franja horaria'),
            ('Evento', 'Evento')
        ],
        null=False
    )
    
    # Campo para el estado de la zona, de tipo booleano con valor predeterminado True
    estado = models.BooleanField(default=True)
    
    # Campo para la tarifa base, mapeado a DECIMAL(10, 2) en la base de datos
    tarifa_base = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        # Esto le indica a Django que la tabla ya existe y no debe crearla
        managed = False
        
        # Le dice a Django el nombre exacto de la tabla en la base de datos
        db_table = 'Zona_comun'

    def __str__(self):
        return self.nombre_zona


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=15,
        choices=[('Rechazada', 'Rechazada'), ('Aprobada', 'Aprobada'), ('En espera', 'En espera')],
        default='En espera'
    )
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_uso = models.DateField()
    observacion = models.CharField(max_length=255, null=True, blank=True)
    forma_pago = models.CharField(
        max_length=20,
        choices=[('Transferencia', 'Transferencia'), ('Efectivo', 'Efectivo')],
        null=True, blank=True
    )
    valor_pago = models.FloatField(null=True, blank=True)  # 👈 nuevo campo

    cod_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='cod_usuario')
    cod_zona = models.ForeignKey(ZonaComun, on_delete=models.CASCADE, db_column='cod_zona')

    class Meta:
        managed = False   # ⚠️ Recuerda que Django NO manejará migraciones aquí
        db_table = 'Reserva'

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.cod_usuario}"


class DetalleResidente(models.Model):
    id_detalle_residente = models.AutoField(primary_key=True)
    propietario = models.BooleanField(default=True)
    apartamento = models.IntegerField()
    torre = models.IntegerField()
    cod_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='cod_usuario')

    class Meta:
        managed = False
        db_table = 'Detalle_residente'

    def __str__(self):
        return f"Residente {self.cod_usuario} - Torre {self.torre}, Apto {self.apartamento}"
    
    
class Noticias(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()  # ahora es TextField
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    cod_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='cod_usuario'
    )

    class Meta:
        managed = False   # porque la tabla ya existe en la BD
        db_table = 'Noticias'

    def __str__(self):
        return f"Noticia {self.id_noticia}: {self.descripcion[:30]}..."


class VehiculoResidente(models.Model):
    id_vehiculo_residente = models.AutoField(primary_key=True, db_column='ID_vehiculo_residente')
    placa = models.CharField(max_length=7, unique=True)
    tipo_vehiculo = models.CharField(
        max_length=10,
        choices=[('Carro', 'Carro'), ('Moto', 'Moto')]
    )
    activo = models.BooleanField()
    documentos = models.BooleanField(default=True)
    cod_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='cod_usuario'
    )

    class Meta:
        managed = False
        db_table = 'Vehiculo_residente'

    def __str__(self):
        return f"{self.placa} - {self.tipo_vehiculo}"


class TipoArchivo(models.Model):
    idTipoArchivo = models.AutoField(primary_key=True, db_column='idTipoArchivo')
    tipo_documento = models.CharField(
        max_length=50,
        choices=[
            ('SOAT', 'SOAT'),
            ('Tarjeta de propiedad', 'Tarjeta de propiedad'),
            ('Técnico-mecánica', 'Técnico-mecánica'),
            ('Licencia', 'Licencia'),
            ('Identidad', 'Identidad'),
        ]
    )

    class Meta:
        managed = False
        db_table = 'TipoArchivo'

    def __str__(self):
        return self.tipo_documento


class ArchivoVehiculo(models.Model):
    idArchivo = models.AutoField(primary_key=True, db_column='idArchivo')
    idVehiculo = models.ForeignKey(
        'VehiculoResidente',
        on_delete=models.CASCADE,
        db_column='idVehiculo'
    )
    idTipoArchivo = models.ForeignKey(
        'TipoArchivo',
        on_delete=models.CASCADE,
        db_column='idTipoArchivo'
    )
    archivo = models.FileField(
        upload_to='vehiculos/',  # carpeta dentro de MEDIA_ROOT
        db_column='rutaArchivo'
    )
    fechaSubida = models.DateTimeField(auto_now_add=True, db_column='fechaSubida')
    fechaVencimiento = models.DateField(null=True, blank=True, db_column='fechaVencimiento')

    class Meta:
        managed = False
        db_table = 'ArchivoVehiculo'

    def __str__(self):
        return f"{self.idVehiculo.placa} - {self.idTipoArchivo.tipo_documento}"
       

class Parqueadero(models.Model):
    id_parqueadero = models.IntegerField(primary_key=True, db_column='ID_parqueadero')
    numero_parqueadero = models.CharField(max_length=6)
    comunal = models.BooleanField()
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'Parqueadero'

    def __str__(self):
        return f"Parqueadero {self.numero_parqueadero}"


class Sorteo(models.Model):
    id_sorteo = models.AutoField(primary_key=True, db_column='ID_sorteo')
    fecha_creado = models.DateTimeField(auto_now_add=True, db_column='fecha_creado')
    tipo_residente_propietario = models.BooleanField(null=True, blank=True)
    fecha_inicio = models.DateField()
    hora_sorteo = models.TimeField(default=1)

    class Meta:
        managed = False
        db_table = 'Sorteo'

    def __str__(self):
        tipo = "Propietarios" if self.tipo_residente_propietario else "Arrendatarios" if self.tipo_residente_propietario == False else "Todos"
        return f"Sorteo {self.id_sorteo} - {tipo} - {self.fecha_inicio}"


class GanadorSorteo(models.Model):
    id_ganador = models.AutoField(primary_key=True, db_column='ID_ganador')
    id_sorteo = models.ForeignKey(Sorteo, on_delete=models.CASCADE, db_column='id_sorteo')
    id_detalle_residente = models.ForeignKey(DetalleResidente, on_delete=models.CASCADE, db_column='id_detalle_residente')
    id_parqueadero = models.ForeignKey(Parqueadero, on_delete=models.CASCADE, db_column='id_parqueadero')
    fecha_ganado = models.DateTimeField(auto_now_add=True, db_column='fecha_ganado')

    class Meta:
        managed = False
        db_table = 'Ganador_sorteo'

    def __str__(self):
        return f"Ganador: {self.id_detalle_residente} - Parqueadero {self.id_parqueadero.numero_parqueadero}"
    

class Visitante(models.Model):
    id_visitante = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    documento = models.CharField(max_length=50)
    celular = models.CharField(max_length=20)
    tipo_vehiculo = models.CharField(max_length=20)
    placa = models.CharField(max_length=10)

    class Meta:
        managed = False  # Porque la tabla ya existe
        db_table = 'visitante'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.placa}"


class DetallesParqueadero(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    tipo_propietario = models.CharField(
        max_length=10,
        choices=[('Visitante', 'Visitante'), ('Residente', 'Residente')]
    )
    id_visitante = models.ForeignKey(
        'Visitante',
        models.DO_NOTHING,
        db_column='id_visitante',
        blank=True,
        null=True
    )
    id_vehiculo_residente = models.ForeignKey(
        'VehiculoResidente',
        models.DO_NOTHING,
        db_column='id_vehiculo_residente',
        blank=True,
        null=True
    )
    registro = models.DateField(auto_now_add=True)  # fecha automática
    hora_llegada = models.TimeField(blank=True, null=True)
    hora_salida = models.TimeField(blank=True, null=True)
    pago = models.FloatField(blank=True, null=True)  # nuevo campo para el pago
    id_parqueadero = models.ForeignKey(
        'Parqueadero',
        models.DO_NOTHING,
        db_column='ID_parqueadero'
    )

    class Meta:
        managed = False
        db_table = 'detalles_parqueadero'

    def __str__(self):
        return f"Detalle {self.id_detalle} - {self.tipo_propietario}"
    

class RegistroCorrespondencia(models.Model):
    TIPO_CHOICES = [
        ('Recibo', 'Recibo'),
    ]

    id_correspondencia = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField()
    cod_vigilante = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column='cod_vigilante',
        related_name='correspondencias_vigilante'
    )

    class Meta:
        db_table = 'RegistroCorrespondencia'
        managed = False  # Django no intentará crear ni modificar la tabla

    def __str__(self):
        return f"{self.tipo} - {self.descripcion[:20]}"


class EntregaCorrespondencia(models.Model):
    id_Entrega = models.AutoField(primary_key=True)
    fechaEntrega = models.DateTimeField(auto_now_add=True)  # se llena automáticamente
    idUsuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column='idUsuario',
        related_name='entregas_usuario'
    )
    idCorrespondecia = models.ForeignKey(
        RegistroCorrespondencia,
        on_delete=models.DO_NOTHING,
        db_column='idCorrespondecia',
        related_name='entregas_correspondencia'
    )
    idDetalles_residente = models.ForeignKey(
        'DetalleResidente',  # Asumiendo que tienes un modelo llamado DetalleResidente
        on_delete=models.DO_NOTHING,
        db_column='idDetalles_residente',
        related_name='entregas_residente'
    )

    class Meta:
        db_table = 'EntregaCorrespondecia'
        managed = False  # Django no intentará crear o modificar la tabla

    def __str__(self):
        return f"Entrega {self.id_Entrega} - {self.idDetalles_residente}"
    
    
class PagosReserva(models.Model):
    id_pago = models.AutoField(primary_key=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    # Archivos subidos a media/pagos/
    archivo_1 = models.FileField(upload_to='pagos/', null=False, blank=False)
    archivo_2 = models.FileField(upload_to='pagos/', null=True, blank=True)

    estado = models.BooleanField(default=False)  # oculto por defecto

    id_reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        db_column='id_reserva'
    )

    class Meta:
        managed = False
        db_table = 'pagos_reserva'

    def __str__(self):
        return f"Pago {self.id_pago} de la Reserva {self.id_reserva.id_reserva}"


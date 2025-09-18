from django.db import models
from usuario.models import *

# Create your models here.
class Paquete(models.Model):
    id_paquete = models.AutoField(db_column='ID_paquete', primary_key=True)
    apartamento = models.IntegerField(db_column='apartamento')
    torre = models.IntegerField(db_column='torre')
    fecha_recepcion = models.DateTimeField(db_column='fecha_recepcion')
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column='descripcion')

    cod_usuario_recepcion = models.ForeignKey(
        Usuario,
        db_column='cod_usuario_recepcion',
        related_name='paquetes_recepcion',
        on_delete=models.DO_NOTHING
    )

    fecha_entrega = models.DateTimeField(db_column='fecha_entrega', null=True, blank=True)
    cod_usuario_entrega = models.ForeignKey(
        Usuario,
        db_column='cod_usuario_entrega',
        related_name='paquetes_entrega',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    nombre_residente = models.CharField(max_length=100, null=True, blank=True, db_column='nombre_residente')

    class Meta:
        db_table = 'Paquete'
        managed = False  # Tabla existente

    def __str__(self):
        return f"Paquete {self.id_paquete} - Apt {self.apartamento}"
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # username = models.CharField(max_length=100, unique=True)
    # email = models.EmailField(max_length=256, unique=True)
    # password = models.CharField(max_length=256)
    # created_at = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"
    

class Cita(models.Model):
    TIPOS_CITA = [
    ('Masaje', 'Masaje'),
    ('Nutrición', 'Nutrición'),
    ('Peso', 'Bajada de peso'),
    ]
    
    user = models.ForeignKey(
        'User',                    # Relación con el modelo User
        on_delete=models.CASCADE,  # Si se borra el usuario, se borran sus citas
        related_name='citas'       # Permite acceder a las citas desde el usuario: user.citas.all()
    )
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=TIPOS_CITA)

    def __str__(self):
        return f"{self.tipo} - {self.fecha} ({self.user.username})"

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.CharField(max_length=50)  # Lo guardamos como texto por formatos “37,92 €”
    
    img_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Promocion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la promoción")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción del descuento (ej. 10%)")
    fecha_inicio = models.DateField(verbose_name="Vigencia Desde")
    fecha_fin = models.DateField(verbose_name="Vigencia Hasta")
    activa = models.BooleanField(default=True, verbose_name="¿Activa?")

    def __str__(self):
        return self.nombre
    

    
class Directo(models.Model):
    """
    Modelo para almacenar el mensaje que se muestra globalmente en la cabecera.
    """
    text = models.CharField(max_length=255, verbose_name="Mensaje de cabecera")
    url = models.URLField(max_length=200, blank=True, null=True, verbose_name="Hipervínculo")
    is_active = models.BooleanField(default=False, verbose_name="¿Activo para mostrar?")
    
    def __str__(self):
        return self.text
from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=256, unique=True)
    password = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"
    

TIPOS_CITA = [
    ('Masaje', 'Masaje'),
    ('Nutrición', 'Nutrición'),
    ('Peso', 'Bajada de peso'),
]

class Cita(models.Model):
    user = models.ForeignKey(
        'User',            # Relación con el modelo User
        on_delete=models.CASCADE,  # Si se borra el usuario, se borran sus citas
        related_name='citas'       # Permite acceder a las citas desde el usuario: user.citas.all()
    )
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=TIPOS_CITA)

    def __str__(self):
        return f"{self.tipo} - {self.fecha} ({self.user.username})"
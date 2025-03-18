from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Utilizadores(AbstractUser):
    CLASSE_CHOICES = (
        ('MiniBad', 'MiniBad'),
        ('classe_1', 'Classe 1'),
        ('classe_2', 'Classe 2'),
        ('participacao_geral', 'Participação Geral'),
        ('rendimento', 'Rendimento'),
    )
    

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField(null=False, blank=False)
    classe = models.CharField(max_length=50, choices=CLASSE_CHOICES, null=True, blank=True)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilizadores_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_query_name='utilizadores',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilizadores_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_query_name='utilizadores',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    



class Treinos(models.Model):
    DIAS_SEMANA_CHOICES = [
        ('segunda-feira', 'Segunda-feira'),
        ('terça-feira', 'Terça-feira'),
        ('quarta-feira', 'Quarta-feira'),
        ('quinta-feira', 'Quinta-feira'),
        ('sexta-feira', 'Sexta-feira'),
        ('sábado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    TIPO_CHOICES = [
        ('treino', 'Treino'),
        ('torneio', 'Torneio'),
    ]

    descricao = models.CharField(max_length=255, null=True, blank=True, default='None')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    dia_da_semana = models.CharField(max_length=20, choices=DIAS_SEMANA_CHOICES)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='Treino')

    def __str__(self):
        return f'{self.descricao}'


class Reservas(models.Model):
    utilizador = models.ForeignKey(Utilizadores, on_delete=models.CASCADE)
    treino = models.ForeignKey(Treinos, on_delete=models.CASCADE)
    confirmado = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.utilizador.username} - {self.treino.data_inicio}"




class GestaoCarrinha(models.Model):
    torneio = models.ForeignKey(Treinos, on_delete=models.CASCADE, limit_choices_to={'tipo': 'torneio'})
    ocupante1 = models.CharField(max_length=100, null=True, blank=True)
    ocupante2 = models.CharField(max_length=100, null=True, blank=True)
    ocupante3 = models.CharField(max_length=100, null=True, blank=True)
    ocupante4 = models.CharField(max_length=100, null=True, blank=True)
    ocupante5 = models.CharField(max_length=100, null=True, blank=True)
    ocupante6 = models.CharField(max_length=100, null=True, blank=True)
    ocupante7 = models.CharField(max_length=100, null=True, blank=True)
    ocupante8 = models.CharField(max_length=100, null=True, blank=True)
    condutor = models.ForeignKey(Utilizadores, on_delete=models.CASCADE)
    quilometros_saida = models.DecimalField(max_digits=6, decimal_places=3)
    quilometros_chegada = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return f'{self.torneio}'


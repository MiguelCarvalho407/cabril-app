from django.contrib import admin
from django import forms
from .models import *

# 1. Form personalizado
class UtilizadorForm(forms.ModelForm):
    class Meta:
        model = Utilizadores
        fields = '__all__'
        #NO ADMIN MUDAR O NOME DOS CAMPOS PARA NOMES PERSONALIZADOS
        labels = {
            'username': 'Nome',
            'funcao': 'Função',
            'last_login': 'Último Login',
            'date_joined': 'Data Criação da Conta',
        }
        widgets = {
            'funcao': forms.CheckboxSelectMultiple,
        }

# 2. Admin personalizado
@admin.register(Utilizadores)
class UtilizadoresAdmin(admin.ModelAdmin):
    form = UtilizadorForm
    list_display = ('username', 'email', 'get_funcoes', 'is_active', 'is_staff')
    list_filter = ('funcao', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

    readonly_fields = ('email_readonly',)
    
    fieldsets = (
        ('Informações de Login', {
            'fields': ('email', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('username', 'email_readonly', 'data_nascimento', 'classe')
        }),
        ('Permissões e Funções', {
            'fields': ('funcao', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Outras Informações', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_funcoes(self, obj):
        return ", ".join([f.get_nome_display() for f in obj.funcao.all()])
    get_funcoes.short_description = 'Funções'

    def email_readonly(self, obj):
        return obj.email
    email_readonly.short_description = 'Email'

# 3. Outros modelos (sem alterações)
admin.site.register(Treinos)
admin.site.register(Reservas)
admin.site.register(Funcoes)
admin.site.register(GestaoCarrinha)

from django.forms import ModelForm
from .models import *
from django import forms
import dns.resolver


class CriarContaForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': 'Primeiro e Último'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control',
        'placeholder':'Insere o teu email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'Insere a tua password'
    }))
    confirmar_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'Confirma a password'
    }))
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={
        'class':'form-control',
        'type':'date'
    }))
    chave = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'Chave fornecida pelo clube'
    }))


    # VER SE OS @ INSERIDOS NA CRIAÇÃO DAS CONTAS SÃO VÁLIDOS
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            try:
                nome, dominio = email.split('@')

                # Consulta registros MX para o domínio
                registros_mx = dns.resolver.resolve(dominio, 'MX')

                # Se não houver registros MX, o domínio não tem servidor de e-mail
                if not registros_mx:
                    raise ValidationError(f"'{dominio}' não é válido.")

            except dns.resolver.NXDOMAIN:
                raise ValidationError(f"O domínio '{dominio}' não é válido.")

            except dns.resolver.NoAnswer:
                raise ValidationError(f"'{dominio}' não é válido.")

            except dns.exception.Timeout:
                raise ValidationError("Erro ao verificar o e-mail. Tente novamente mais tarde.")

        return email

    # ERROS NO CRIAÇÃO DAS CONTAS
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')
        chave = cleaned_data.get('chave')

        if password and len(password) < 8:
            self.add_error('password', 'A password deve conter pelo menos 8 caracteres')

        if confirmar_password != password:
            self.add_error('confirmar_password', 'As passwords não correspondem')

        if chave != '123':
            self.add_error('chave', 'Chave Incorreta.')

        return cleaned_data



class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control',
        'placeholder':'Insere o teu email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'Insere a tua password'
    }))



# ========== CriarEventosCRUD ========== #


class CriarTreinoForm(forms.Form):
    descricao = forms.CharField(widget=forms.TextInput(), required=False)

    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    hora_inicio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    hora_fim = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    dia_da_semana = forms.MultipleChoiceField(
        choices=Treinos.DIAS_SEMANA_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    tipo = forms.ChoiceField(
        choices=Treinos.TIPO_CHOICES,
        widget=forms.Select()
    )


class ReservasForm(forms.ModelForm):
    class Meta:
        model = Reservas
        fields = ['treino']


# ========== ================ ========== #






class GestaoCarrinhaForm(forms.ModelForm):
    quilometros_chegada = forms.DecimalField(required=False)

    class Meta:
        model = GestaoCarrinha
        fields = ['torneio', 'ocupante1', 'ocupante2', 'ocupante3', 'ocupante4', 'ocupante5',
                  'ocupante6', 'ocupante7', 'ocupante8', 'condutor', 'quilometros_saida', 'quilometros_chegada']    

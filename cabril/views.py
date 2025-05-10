from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from .forms import *
import json
from django.contrib import messages
from django.db.models import Q
from django.conf import settings




# ========== CRIAR CONTAS/LOGIN/LOGOUT ========== #

def signup(request):
    if request.method == 'POST':
        form = CriarContaForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            if Utilizadores.objects.filter(email=email).exists():
                form.add_error('email', 'Este email já está em uso.')
            else:

                Utilizadores.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    data_nascimento=form.cleaned_data['data_nascimento'],
                )
            
            return redirect('login')
    else:
        form = CriarContaForm()

    return render(request, 'CABRIL_APP/CABRIL_APP_CONTAS/singup.html', {'form': form})


def dologin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                form.add_error(None, 'Email ou password incorretos.')
    else:
        form = LoginForm()

    return render(request, 'CABRIL_APP/CABRIL_APP_CONTAS/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')


# ========== MUDAR PASSWORD ========== #

from django.contrib.auth import update_session_auth_hash

@login_required
def alterar_password(request):
    if request.method == 'POST':
        form = PasswordChangeFormPT(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'A tua password foi alterada com sucesso!')
            return redirect('definicoes')
    else:
        form = PasswordChangeFormPT(user=request.user)
    
    return render(request, 'CABRIL_APP/CABRIL_APP_CONTAS/alterar_password.html', {'form':form})


# ========== RECUPERAR PASSWORD ========== #


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = Utilizadores.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            current_site = request.get_host()
            reset_url = f"http://{current_site}/reset/{uid}/{token}/"

            send_mail(
                "CABRIL-Serpins - Recuperar Password",
                f'Olá {user.username}\n\n'
                f"Clica no seguinte link para definires uma nova password: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect("login")
    else:
        form = PasswordResetRequestForm()

    return render(request, 'CABRIL_APP/CABRIL_APP_CONTAS/password_reset_form.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilizadores.objects.get(pk=uid)
    except (Utilizadores.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password1"])
                user.save()
                return redirect('login')
        else:
            form = SetNewPasswordForm()
        return render(request, "CABRIL_APP/CABRIL_APP_CONTAS/password_reset_confirm.html", {"form": form})
    else:
        return render(request, "CABRIL_APP/CABRIL_APP_CONTAS/password_reset_invalid.html")



# ========== ======================== =========== #





# ================= APPS CABRIL ================= #


# REMOVER (PÁGINAS EM DESENVOLVIMENTO)
@login_required
def pagsdesenvolvimento(request):
    return render(request, 'CABRIL_APP/REMOVER/index.html')


@login_required
def inicio(request):
    return render(request, 'CABRIL_APP/base.html')



@login_required
def atletas(request):
    query = request.GET.get('q', '')
    if query:
        membros = Utilizadores.objects.filter(Q(username__icontains=query))
    else:
        membros = Utilizadores.objects.all()
    return render(request, 'CABRIL_APP/membros.html', {'membros': membros})



@login_required
def calendario_classe3(request):
    treinos = Treinos.objects.all()
    
    reservas_atleta = Reservas.objects.filter(utilizador=request.user).select_related('treino')
    reservas_dict = {reserva.treino.id: reserva.confirmado for reserva in reservas_atleta}

    treinos_json = [
        {
            "id": treino.id,
            "data": treino.data_inicio.strftime("%Y-%m-%d"),
            "hora_inicio": treino.hora_inicio.strftime("%H:%M"),
            "hora_fim": treino.hora_fim.strftime("%H:%M"),
            "tipo": treino.get_tipo_display(),
            "descricao": treino.descricao,
            "dia_da_semana": treino.get_dia_da_semana_display(),
            "reservado": treino.id in reservas_dict,
            "confirmado": reservas_dict.get(treino.id, False),
        }
        for treino in treinos
    ]

    return render(request, 'CABRIL_APP/CALENDARIOS/classe3.html', {'treinos_json': json.dumps(treinos_json)})



@login_required
def reservas(request, training_id):
    training = get_object_or_404(Treinos, id=training_id)

    treino_datetime = datetime.combine(training.data_inicio, training.hora_inicio)
    treino_datetime = timezone.make_aware(treino_datetime, timezone.get_current_timezone())


    # VER SE O TREINO JÁ PASSOU
    if timezone.now() >= treino_datetime:
        return redirect('calendario_classe3')

    # VER SE O UTILIZADOR JÁ TEM RESERVA
    reservation = Reservas.objects.filter(utilizador=request.user, treino=training).first()
    
    # SE TIVER RESERVA PODE CANCELAR
    if reservation:
        reservation.delete()

    else:
        # SENÃO MARCA
        Reservas.objects.create(utilizador=request.user, treino=training)
    return redirect('calendario_classe3')



@login_required
def reservas_detalhes(request, training_id):
    training = get_object_or_404(Treinos, id=training_id)
    reservations = Reservas.objects.filter(treino=training)

    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        reservation = get_object_or_404(Reservas, id=reservation_id)

        # Alterna entre confirmado e não confirmado
        reservation.confirmado = not reservation.confirmado
        reservation.save()

        return redirect('reservas_detalhes', training_id=training.id)

    return render(request, 'CABRIL_APP/reservas_detalhes.html', {'training': training, 'reservations': reservations})



@login_required
def remover_presenca(request, treino_id, user_id):
    if not request.user.is_staff:
        return render(request, 'CABRIL_APP/ERRORS/403.html')
    
    treino = get_object_or_404(Treinos, id=treino_id)
    reserva = Reservas.objects.filter(utilizador_id=user_id, treino=treino).first()

    if reserva:
        reserva.delete()

    return redirect('reservas_detalhes', training_id=treino.id)



@login_required
def adicionar_utilizador(request, treino_id):
    if not request.user.is_staff:
        return render(request, 'CABRIL_APP/ERRORS/403.html')
    
    treino = get_object_or_404(Treinos, id=treino_id)

    if request.method == "POST":
        utilizador_id = request.POST.get('utilizador_id')
        utilizador = get_object_or_404(Utilizadores, id=utilizador_id)

        # Criar uma reserva para o utilizador, marcando como ausente
        Reservas.objects.get_or_create(
            treino=treino, 
            utilizador=utilizador, 
            defaults={'confirmado': False}  # Aqui dizemos que não confirmou presença
        )

        return redirect('adicionar_utilizador', treino_id=treino.id)

    # Pega os utilizadores que **ainda não têm reserva** para este treino
    utilizadores_sem_reserva = Utilizadores.objects.exclude(
        id__in=Reservas.objects.filter(treino=treino).values_list('utilizador_id', flat=True)
    )

    return render(request, 'CABRIL_APP/adicionar_utilizador.html', {'utilizadores_sem_reserva': utilizadores_sem_reserva, 'treino': treino})



@login_required
def cancelar_evento(request, treino_id):
    if not request.user.is_staff:
        return render(request, 'CABRIL_APP/ERRORS/403.html')
    
    treino = get_object_or_404(Treinos, id=treino_id)

    if request.user.is_staff:
        treino.delete()

    return redirect('calendario_classe3')






@login_required
def definicoes(request):
    if request.method == 'POST':
        form = DefinicoesForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Alterações guardadas com sucesso!')
            return redirect('definicoes')
        
    else:
        form = DefinicoesForm(instance=request.user)

    return render(request, 'CABRIL_APP/definicoes.html', {'form': form})



@login_required
def criarevento(request):
    if not request.user.is_staff:
        return render(request, 'CABRIL_APP/ERRORS/403.html')
    
    if request.method == 'POST':
        form = CriarTreinoForm(request.POST)
        if form.is_valid():
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_fim = form.cleaned_data['hora_fim']
            dias_da_semana = form.cleaned_data['dia_da_semana']
            tipo = form.cleaned_data['tipo']
            descricao = form.cleaned_data['descricao']
        
            dia_semana_map = {
                'segunda-feira': 0,
                'terça-feira': 1,
                'quarta-feira': 2,
                'quinta-feira': 3,
                'sexta-feira': 4,
                'sábado': 5,
                'domingo': 6,
            }

            current_date = data_inicio
            while current_date <= data_fim:
                # Verifica se a data corresponde a algum dos dias escolhidos
                if current_date.weekday() in [dia_semana_map[dia] for dia in dias_da_semana]:
                    for dia_da_semana in dias_da_semana:
                        if current_date.weekday() == dia_semana_map[dia_da_semana]:  
                            Treinos.objects.create(
                                data_inicio=current_date,
                                data_fim=data_fim,
                                hora_inicio=hora_inicio,
                                hora_fim=hora_fim,
                                dia_da_semana=dia_da_semana ,
                                tipo = tipo,
                                descricao=descricao,
                            )

                current_date += timedelta(days=1)

            return redirect('calendario_classe3')
    else:
        form = CriarTreinoForm()

    return render(request, 'CABRIL_APP/CriarEventosCRUD/criar.html', {'form': form})



# ========== GESTÃO DA CARRINHA ========== #



@login_required
def gestaocarrinha(request):

    if request.method == 'POST':
        form = GestaoCarrinhaForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('ver_registos')
    else:
        form = GestaoCarrinhaForm()

    return render(request, 'CABRIL_APP/GestaoCarrinha/preencher.html', {'form':form})


@login_required
def editar_gestao_carrinha(request, carrinha_id):
    carrinha = get_object_or_404(GestaoCarrinha, id=carrinha_id)

    if request.method == 'POST':
        form = GestaoCarrinhaForm(request.POST, instance=carrinha)
        if form.is_valid():
            form.save()
            return redirect('ver_registos')
    else:
        form = GestaoCarrinhaForm(instance=carrinha)

    return render(request, 'CABRIL_APP/GestaoCarrinha/editar.html', {'form': form})



@login_required
def ver_registos(request):
    registos = GestaoCarrinha.objects.all()
    return render(request, 'CABRIL_APP/GestaoCarrinha/ver_registos.html', {'registos': registos})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from .forms import *
import json



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



# ========== ======================== =========== #







# ================ SITE CABRIL ================== #


# def base(request):
#     return render(request, 'CABRIL_SITE/base.html')


# def socios(request):
#     return render(request, 'CABRIL_SITE/socios.html')

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
def calendario(request):
    treinos = Treinos.objects.all()

    treinos_json = [
        {
            "id": treino.id,
            "data": treino.data_inicio.strftime("%Y-%m-%d"),
            "hora_inicio": treino.hora_inicio.strftime("%H:%M"),
            "hora_fim": treino.hora_fim.strftime("%H:%M"),
            "tipo": treino.get_tipo_display(),
            "reservado": Reservas.objects.filter(utilizador=request.user, treino=treino).exists(),
        }
        for treino in treinos
    ]

    return render(request, 'CABRIL_APP/calendario.html', {'treinos_json': json.dumps(treinos_json)})



@login_required
def reservas(request, training_id):
    training = get_object_or_404(Treinos, id=training_id)
    
    # Verifica se o usuário já fez a reserva para este treino
    reservation = Reservas.objects.filter(utilizador=request.user, treino=training).first()
    
    if reservation:
        # Se a reserva existe, o usuário pode desreservar
        reservation.delete()
        return redirect('calendario')

    # Cria a reserva para o usuário
    Reservas.objects.create(utilizador=request.user, treino=training)
    return redirect('calendario')



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
def adicionar_utilizador(request):

    treino_atual = Treinos.objects.first()


    utilizadores_sem_reserva = Utilizadores.objects.exclude(id__in=Reservas.objects.filter(treino=treino_atual).values('utilizador_id'))


    if request.method == "POST":

        utilizador_id = request.POST.get('utilizador_id')
        utilizador = Utilizadores.objects.get(id=utilizador_id)
        
        Reservas.objects.create(treino=treino_atual, utilizador=utilizador)
        
        return redirect('adicionar_utilizador')

    return render(request, 'CABRIL_APP/adicionar_utilizador.html', {
        'utilizadores_sem_reserva': utilizadores_sem_reserva,
        'treino_atual': treino_atual,
    })



@login_required
def cancelar_evento(request, treino_id):
    treino = get_object_or_404(Treinos, id=treino_id)

    if request.user.is_staff:
        treino.delete()

    return redirect('calendario')






@login_required
def definicoes(request):
    return render(request, 'CABRIL_APP/definicoes.html')



@login_required
def criarevento(request):
    if request.method == 'POST':
        form = CriarTreinoForm(request.POST)
        if form.is_valid():
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_fim = form.cleaned_data['hora_fim']
            dias_da_semana = form.cleaned_data['dia_da_semana']  # Lista com os dias selecionados
            tipo = form.cleaned_data['tipo']
        
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
                            )

                current_date += timedelta(days=1)

            return redirect('calendario')
    else:
        form = CriarTreinoForm()

    return render(request, 'CABRIL_APP/CriarEventosCRUD/criar.html', {'form': form})



@login_required
def gestaocarrinha(request):

    if request.method == 'POST':
        form = GestaoCarrinhaForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = GestaoCarrinhaForm()

    return render(request, 'CABRIL_APP/GestaoCarrinha/preencher.html', {'form':form})
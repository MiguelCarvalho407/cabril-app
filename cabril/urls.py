from django.shortcuts import redirect
from django.urls import path
from . import views

# SERVE CASO ALGUEM ACESSE UMA URL ANTES DE FAZER LOGIN ELE REDIRECIONA PARA A DE LOGIN 
def home_redirect(request):
    return redirect('/login/')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('login/', views.dologin, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),


    # ========== CABRIL_APP ========== #

    path('inicio/', views.inicio, name='inicio'),
    path('gestaocarrinha/', views.gestaocarrinha, name='gestaocarrinha'),
    path('calendario/', views.calendario, name='calendario'),
    path('definicoes/', views.definicoes, name='definicoes'),

    path('treinodetalhes/<int:training_id>/', views.reservas_detalhes, name='reservas_detalhes'),
    path('reservas/<int:training_id>/', views.reservas, name='reservas'),
    path('adicionarutilizador/<int:treino_id>/', views.adicionar_utilizador, name='adicionar_utilizador'),
    path('removerutilizador/<int:treino_id>/<int:user_id>/', views.remover_presenca, name='remover_presenca'),


    path('desenvolvimento/', views.pagsdesenvolvimento, name='pagsdesenvolvimento'),

    
    # ========== CriarEventosCRUD ========== #

    path('criarevento/', views.criarevento, name='criarevento'),
    path('cancelarevento/<int:treino_id>/', views.cancelar_evento, name='cancelar_evento'),

    # ========== ========== ========== #

]

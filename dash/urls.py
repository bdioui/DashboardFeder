"""dash_board URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import HomeView, RechercheListView, Enveloppe_form, Home_Report
from django.contrib.auth.decorators import login_required

app_name ='dash'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('opération/<str:numero_op>/', views.detail_view, name='opération'),
    path('tableau_directeur/', views.directeur, name='directeur'),
    path('porteur_privé/', views.porteur_privé, name='porteur_privé'),
    path('porteur_public/', views.porteur_public, name='porteur_public'),
    path('données_financières/', views.données_financières, name='données_financières'),
    path('ramo/', views.ramo, name='ramo'),
    path('recherche/', RechercheListView.as_view(), name='recherche'),
    path('suivi_indicateurs/', views.suivi_indicateurs, name='suivi_indicateurs'),

    path('Home_Report/', Home_Report.as_view(), name='Report'),
    
    path('alerte/', views.alerte, name='alerte'),
    path('difficulté/', views.difficulté, name='difficulté'),
    path('programmé_difficulté/', views.programmé_difficulté, name='programmé_difficulté'),
    path('difficultés/', views.difficultés, name='difficultés'),

    path('erreur/', views.erreur, name='erreur'),



    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot'),

    path('csv_load/', views.CSV_update, name='csv_load'),
    path('indicateurs_load/', views.indicateurs_update, name='indicateurs_load'),
    path('enveloppe/', views.Enveloppe_form.as_view(), name='enveloppe'),

    path('charts/', views.charts, name='charts'),
    path('cards/', views.cards, name='cards'),
    path('404/', views.error, name='error'),

    path('tables/', views.tables, name='tables'),
    path('tables_programmé/', views.tables_programmé, name='tables_programmé'),
    path('tables_déposés/', views.tables_déposés, name='tables_déposés'),
    path('tables_instruction/', views.tables_instruction, name='tables_instruction'),
    path('tables_soldés/', views.tables_soldés, name='tables_soldés'),
    path('tables_retirés/', views.tables_retirés, name='tables_retirés'),



    path('api/data/', views.get_data, name='api-data'),
    path('api/bar_data/', views.bar_data, name='api-bar_data'),
    path('api/bar_data2/', views.bar_data2, name='api-bar_data2'),
    #path('api/chart/data/', ChartData.as_view()),

]

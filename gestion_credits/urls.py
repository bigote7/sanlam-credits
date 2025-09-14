from django.urls import path
from . import views

app_name = 'gestion_credits'

urlpatterns = [
    # Route racine - redirection vers le tableau de bord
    path('', views.redirect_to_dashboard, name='home'),
    
    # URLs d'authentification
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    
    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Gestion des clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/update/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Gestion des crédits
    path('credits/', views.credit_list, name='credit_list'),
    path('credits/create/', views.credit_create, name='credit_create'),
    path('credits/create/divise/', views.credit_create_divise_complet, name='credit_create_divise_complet'),
    path('credits/<int:pk>/', views.credit_detail, name='credit_detail'),
    path('credits/<int:pk>/delete/', views.credit_delete, name='credit_delete'),
    
    # Gestion des paiements
    path('credits/<int:credit_id>/paiements/ajouter/', views.echeance_create_for_credit, name='echeance_create_for_credit'),
    path('credits/<int:credit_id>/payer-cheque-especes/', views.payer_cheque_especes, name='payer_cheque_especes'),
    
    # Gestion des chèques
    path('cheques/<int:pk>/gerer/', views.gerer_cheque_garantie, name='gerer_cheque_garantie'),
    
    # Règlements
    path('credits/<int:credit_id>/reglements/create/', views.reglement_create, name='reglement_create'),
    path('reglements/<int:pk>/update/', views.reglement_update, name='reglement_update'),
    path('reglements/<int:pk>/delete/', views.reglement_delete, name='reglement_delete'),
    
    # Paiement des échéances (nouveau système professionnel)
    path('credits/<int:credit_id>/paiement-echeance/create/', views.paiement_echeance_create, name='paiement_echeance_create'),
    
    # Ajout de paiement simplifié
    path('credits/<int:credit_id>/ajout-paiement/create/', views.ajout_paiement_create, name='ajout_paiement_create'),
    
    # Chèques de garantie
    path('credits/<int:credit_id>/cheques-garantie/create/', views.cheque_garantie_create, name='cheque_garantie_create'),
    path('cheques-garantie/<int:pk>/update/', views.cheque_garantie_update, name='cheque_garantie_update'),
    path('cheques-garantie/<int:pk>/delete/', views.cheque_garantie_delete, name='cheque_garantie_delete'),
    
    # Gestion des alertes
    path('alertes/', views.alerte_list, name='alerte_list'),
    path('alertes/<int:pk>/traiter/', views.alerte_traiter, name='alerte_traiter'),
    
    # Historique des actions
    path('historique/', views.historique_actions, name='historique_actions'),
]

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import date, timedelta, datetime
from decimal import Decimal
import json

from .models import Client, Credit, Echeance, Cheque, Alerte, ReportEcheance, ActionLog, Reglement, ChequeGarantie
from .forms import (
    ClientForm, CreditForm, CreditUniqueForm, CreditDiviseForm, CreditDiviseCompletForm,
    EcheanceForm, ChequeForm, AlerteForm, ReportEcheanceForm, UserRegistrationForm,
    ReglementForm, ChequeGarantieForm, PaiementEcheanceForm, AjoutPaiementForm
)
from django.contrib.auth.models import User


def redirect_to_dashboard(request):
    """Rediriger la racine vers le tableau de bord"""
    if request.user.is_authenticated:
        return redirect('gestion_credits:dashboard')
    else:
        return redirect('gestion_credits:user_login')


@login_required
def dashboard(request):
    """Tableau de bord principal optimisé pour le système de paiements flexibles"""
    today = date.today()
    
    # === STATISTIQUES GLOBALES ===
    total_credits = Credit.objects.count()
    total_clients = Client.objects.count()
    
    # Calcul des paiements selon la nouvelle logique
    total_paiements_especes = Reglement.objects.filter(
        mode_paiement='especes'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    total_paiements_cheques_verses = Reglement.objects.filter(
        mode_paiement='cheque', 
        statut='verse'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    total_cheques_en_attente = Reglement.objects.filter(
        mode_paiement='cheque', 
        statut='non_verse'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    total_paiements_verses = total_paiements_especes + total_paiements_cheques_verses
    
    # Montant total des crédits
    montant_total_credits = Credit.objects.aggregate(total=Sum('montant_total'))['total'] or 0
    
    # Taux de recouvrement
    taux_recouvrement = 0
    if montant_total_credits > 0:
        taux_recouvrement = (total_paiements_verses / montant_total_credits) * 100
    
    # === PAIEMENTS DU JOUR ===
    paiements_aujourd_hui = Reglement.objects.filter(
        date_reglement=today
    ).select_related('credit__client').order_by('-montant')
    
    montant_paiements_aujourd_hui = paiements_aujourd_hui.aggregate(total=Sum('montant'))['total'] or 0
    
    # === CHÈQUES À ÉCHÉANCE PROCHE ===
    cheques_echeance_proche = ChequeGarantie.objects.filter(
        date_echeance__range=[today, today + timedelta(days=7)]
    ).select_related('credit__client').order_by('date_echeance')
    
    # === CHÈQUES EN RETARD ===
    cheques_en_retard = ChequeGarantie.objects.filter(
        date_echeance__lt=today
    ).select_related('credit__client').order_by('date_echeance')
    
    # === ALERTES ACTIVES ===
    alertes_en_attente = Alerte.objects.filter(
        statut='en_attente'
    ).select_related('echeance__credit__client', 'agent').order_by('date_rappel')[:10]
    
    # === PERFORMANCE DES AGENTS ===
    agents_performance = User.objects.filter(
        reglements_crees__isnull=False
    ).annotate(
        total_paiements=Sum('reglements_crees__montant')
    ).order_by('-total_paiements')[:5]
    
    # === STATISTIQUES PAR TYPE DE CRÉDIT ===
    credits_uniques = Credit.objects.filter(type_credit='unique').count()
    credits_divises = Credit.objects.filter(type_credit='divise').count()
    
    # Calculer les pourcentages pour les barres de progression
    pourcentage_especes = 0
    pourcentage_cheques_verses = 0
    pourcentage_cheques_en_attente = 0
    pourcentage_credits_uniques = 0
    pourcentage_credits_divises = 0
    
    if montant_total_credits > 0:
        pourcentage_especes = (total_paiements_especes / montant_total_credits) * 100
        pourcentage_cheques_verses = (total_paiements_cheques_verses / montant_total_credits) * 100
        pourcentage_cheques_en_attente = (total_cheques_en_attente / montant_total_credits) * 100
    
    if total_credits > 0:
        pourcentage_credits_uniques = (credits_uniques / total_credits) * 100
        pourcentage_credits_divises = (credits_divises / total_credits) * 100
    
    # === RÉPARTITION DES PAIEMENTS PAR MOIS (30 derniers jours) ===
    paiements_30_jours = []
    for i in range(30):
        date_calcul = today - timedelta(days=i)
        montant_jour = Reglement.objects.filter(
            date_reglement=date_calcul
        ).aggregate(total=Sum('montant'))['total'] or 0
        paiements_30_jours.append({
            'date': date_calcul.strftime('%d/%m'),
            'montant': float(montant_jour)
        })
    
    paiements_30_jours.reverse()  # Du plus ancien au plus récent
    
    # === TOP 5 DES CLIENTS PAR MONTANT DE CRÉDIT ===
    top_clients = Client.objects.annotate(
        total_credits=Sum('credits__montant_total')
    ).filter(total_credits__isnull=False).order_by('-total_credits')[:5]
    
    context = {
        # Statistiques globales
        'total_credits': total_credits,
        'total_clients': total_clients,
        'montant_total_credits': montant_total_credits,
        'total_paiements_verses': total_paiements_verses,
        'total_paiements_especes': total_paiements_especes,
        'total_paiements_cheques_verses': total_paiements_cheques_verses,
        'total_cheques_en_attente': total_cheques_en_attente,
        'taux_recouvrement': taux_recouvrement,
        
        # Paiements du jour
        'paiements_aujourd_hui': paiements_aujourd_hui,
        'montant_paiements_aujourd_hui': montant_paiements_aujourd_hui,
        
        # Chèques
        'cheques_echeance_proche': cheques_echeance_proche,
        'cheques_en_retard': cheques_en_retard,
        
        # Alertes
        'alertes_en_attente': alertes_en_attente,
        
        # Performance
        'agents_performance': agents_performance,
        
        # Types de crédits
        'credits_uniques': credits_uniques,
        'credits_divises': credits_divises,
        
        # Pourcentages pour les barres de progression
        'pourcentage_especes': pourcentage_especes,
        'pourcentage_cheques_verses': pourcentage_cheques_verses,
        'pourcentage_cheques_en_attente': pourcentage_cheques_en_attente,
        'pourcentage_credits_uniques': pourcentage_credits_uniques,
        'pourcentage_credits_divises': pourcentage_credits_divises,
        
        # Graphiques
        'paiements_30_jours': paiements_30_jours,
        'top_clients': top_clients,
        
        # Date
        'today': today,
    }
    
    return render(request, 'gestion_credits/dashboard.html', context)


@login_required
def client_list(request):
    """Liste des clients"""
    search_query = request.GET.get('search', '')
    clients = Client.objects.all()
    
    if search_query:
        clients = clients.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(cin__icontains=search_query) |
            Q(telephone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'gestion_credits/client_list.html', context)


@login_required
def client_create(request):
    """Créer un nouveau client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            
            # Créer une action dans l'historique pour la création du client
            ActionLog.objects.create(
                type_action='client_creation',
                description=f'Client créé : {client.nom_complet} - CIN: {client.cin} - Téléphone: {client.telephone}',
                statut='succes',
                agent=request.user,
                client=client,
                donnees_apres={
                    'nom': client.nom,
                    'prenom': client.prenom,
                    'cin': client.cin,
                    'telephone': client.telephone,
                    'email': client.email,
                    'adresse': client.adresse
                }
            )
            
            messages.success(request, f'Client {client.nom_complet} créé avec succès.')
            return redirect('gestion_credits:client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'gestion_credits/client_form.html', context)


@login_required
def client_update(request, pk):
    """Modifier un client existant"""
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            # Sauvegarder l'état avant modification
            donnees_avant = {
                'nom': client.nom,
                'prenom': client.prenom,
                'cin': client.cin,
                'telephone': client.telephone,
                'email': client.email,
                'adresse': client.adresse
            }
            
            client = form.save()
            
            # Créer une action dans l'historique pour la modification du client
            ActionLog.objects.create(
                type_action='client_modification',
                description=f'Client modifié : {client.nom_complet} - CIN: {client.cin}',
                statut='succes',
                agent=request.user,
                client=client,
                donnees_avant=donnees_avant,
                donnees_apres={
                    'nom': client.nom,
                    'prenom': client.prenom,
                    'cin': client.cin,
                    'telephone': client.telephone,
                    'email': client.email,
                    'adresse': client.adresse
                }
            )
            
            messages.success(request, f'Client {client.nom_complet} modifié avec succès.')
            return redirect('gestion_credits:client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    context = {'form': form, 'action': 'Modifier', 'client': client}
    return render(request, 'gestion_credits/client_form.html', context)


@login_required
def client_detail(request, pk):
    """Détails d'un client"""
    client = get_object_or_404(Client, pk=pk)
    credits = client.credits.all().order_by('-date_creation')
    
    context = {
        'client': client,
        'credits': credits,
    }
    return render(request, 'gestion_credits/client_detail.html', context)


@login_required
def client_delete(request, pk):
    """Supprimer un client"""
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, f'Client {client.nom_complet} supprimé avec succès.')
        return redirect('gestion_credits:client_list')
    
    context = {'client': client}
    return render(request, 'gestion_credits/client_confirm_delete.html', context)


@login_required
def credit_list(request):
    """Liste des crédits avec séparation payés/non réglés"""
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    statut_filter = request.GET.get('statut', '')
    
    # Récupérer tous les crédits avec leurs règlements
    credits = Credit.objects.all().select_related('client', 'agent').prefetch_related('reglements')
    
    # Appliquer les filtres de recherche
    if search_query:
        credits = credits.filter(
            Q(client__nom__icontains=search_query) |
            Q(client__prenom__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(numero_police__icontains=search_query)
        )
    
    if type_filter:
        credits = credits.filter(type_credit=type_filter)
    
    # Séparer les crédits payés des crédits non réglés selon la nouvelle logique
    credits_payes = []
    credits_non_regles = []
    
    for credit in credits:
        # Calculer le reste à payer selon la nouvelle logique
        # Seuls les règlements effectivement versés comptent
        total_reglements_verses = 0
        
        for reglement in credit.reglements.all():
            if reglement.mode_paiement == 'especes':
                # Les paiements en espèces comptent toujours
                total_reglements_verses += reglement.montant
            elif reglement.mode_paiement == 'cheque' and reglement.statut == 'verse':
                # Seuls les chèques versés comptent
                total_reglements_verses += reglement.montant
        
        reste_a_payer = credit.montant_total - total_reglements_verses
        
        # Un crédit est "réglé" si le reste à payer est <= 0
        if reste_a_payer <= 0:
            credits_payes.append(credit)
        else:
            credits_non_regles.append(credit)
    
    # Appliquer le filtre de statut si spécifié
    if statut_filter == 'payes':
        credits_a_afficher = credits_payes
    elif statut_filter == 'non_regles':
        credits_a_afficher = credits_non_regles
    else:
        # Par défaut, afficher tous les crédits
        credits_a_afficher = list(credits)
    
    # Statistiques
    total_credits = len(credits)
    total_payes = len(credits_payes)
    total_non_regles = len(credits_non_regles)
    
    # Calculer les montants
    montant_total_payes = sum(credit.montant_total for credit in credits_payes)
    montant_total_non_regles = sum(credit.montant_total for credit in credits_non_regles)
    
    # Pagination
    paginator = Paginator(credits_a_afficher, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'statut_filter': statut_filter,
        'type_choices': Credit.TYPE_CHOICES,
        
        # Statistiques
        'total_credits': total_credits,
        'total_payes': total_payes,
        'total_non_regles': total_non_regles,
        'montant_total_payes': montant_total_payes,
        'montant_total_non_regles': montant_total_non_regles,
        
        # Crédits séparés pour affichage
        'credits_payes': credits_payes[:5],  # Afficher seulement les 5 premiers
        'credits_non_regles': credits_non_regles[:5],  # Afficher seulement les 5 premiers
    }
    return render(request, 'gestion_credits/credit_list.html', context)


@login_required
def credit_create(request):
    """Créer un crédit (unique ou divisé)"""
    credit_type = request.GET.get('type', 'unique')
    
    if credit_type == 'unique':
        if request.method == 'POST':
            form = CreditUniqueForm(request.POST)
            if form.is_valid():
                credit = form.save(commit=False)
                credit.agent = request.user
                # Le numéro de police est déjà validé par le formulaire
                credit.save()
                
                # Créer un log d'action pour la création du crédit
                ActionLog.objects.create(
                    type_action='credit_creation',
                    description=f'Crédit unique créé pour {credit.client.nom_complet} - Police {credit.numero_police} - Montant: {credit.montant_total} DH',
                    statut='succes',
                    agent=request.user,
                    client=credit.client,
                    credit=credit,
                    donnees_apres={
                        'numero_police': credit.numero_police,
                        'montant_total': str(credit.montant_total),
                        'type_credit': credit.type_credit,
                        'description': credit.description,
                        'client': credit.client.nom_complet
                    }
                )
                
                # Créer l'échéance unique
                if credit.date_echeance:
                    date_echeance = credit.date_echeance
                else:
                    # Calculer la date d'échéance basée sur la durée
                    if credit.duree_jours:
                        date_echeance = date.today() + timedelta(days=credit.duree_jours)
                    elif credit.duree_semaines:
                        date_echeance = date.today() + timedelta(weeks=credit.duree_semaines)
                    elif credit.duree_mois:
                        date_echeance = date.today() + timedelta(days=credit.duree_mois * 30)
                    else:
                        date_echeance = date.today() + timedelta(days=30)
                
                # Vérifier si un chèque de garantie est fourni
                has_cheque_garantie = form.cleaned_data.get('has_cheque_garantie', False)
                
                if has_cheque_garantie:
                    # Créer l'échéance avec chèque de garantie
                    echeance = Echeance.objects.create(
                        credit=credit,
                        numero_partie=1,
                        montant=credit.montant_total,
                        date_echeance=date_echeance,
                        est_especes=False  # Pas en espèces car chèque de garantie
                    )
                    
                    # Log pour la création de l'échéance
                    ActionLog.objects.create(
                        type_action='echeance_creation',
                        description=f'Échéance créée pour le crédit {credit.numero_police} - Montant: {echeance.montant} DH - Date: {echeance.date_echeance}',
                        statut='succes',
                        agent=request.user,
                        credit=credit,
                        echeance=echeance,
                        donnees_apres={
                            'numero_partie': echeance.numero_partie,
                            'montant': str(echeance.montant),
                            'date_echeance': str(echeance.date_echeance),
                            'est_especes': echeance.est_especes
                        }
                    )
                    
                    # Créer le chèque de garantie
                    Cheque.objects.create(
                        echeance=echeance,
                        numero_cheque=form.cleaned_data['numero_cheque_garantie'],
                        banque=form.cleaned_data['banque_garantie'],
                        date_emission=form.cleaned_data['date_emission_garantie'],
                        date_reglement_prevu=form.cleaned_data['date_reglement_prevu_garantie'],
                        montant=credit.montant_total,
                        remarques=form.cleaned_data.get('remarques_garantie', ''),
                        statut='garantie'
                    )
                    
                    # Créer l'alerte pour le chèque de garantie
                    Alerte.objects.create(
                        echeance=echeance,
                        type_alerte='cheque_garantie',
                        message=f'Chèque de garantie à traiter pour {credit.client.nom_complet}',
                        date_alerte=date.today(),
                        date_rappel=form.cleaned_data['date_reglement_prevu_garantie'],
                        agent=request.user
                    )
                else:
                    # Créer l'échéance en espèces
                    echeance = Echeance.objects.create(
                        credit=credit,
                        numero_partie=1,
                        montant=credit.montant_total,
                        date_echeance=date_echeance,
                        est_especes=True
                    )
                    
                    # Créer l'alerte pour l'échéance en espèces
                    Alerte.objects.create(
                        echeance=echeance,
                        type_alerte='echeance',
                        message=f'Échéance unique pour {credit.client.nom_complet}',
                        date_alerte=date.today(),
                        date_rappel=echeance.date_rappel,
                        agent=request.user
                    )
                
                messages.success(request, f'Crédit unique créé avec succès pour {credit.client.nom_complet}.')
                return redirect('gestion_credits:credit_detail', pk=credit.pk)
        else:
            form = CreditUniqueForm()
        
        context = {'form': form, 'credit_type': credit_type}
        return render(request, 'gestion_credits/credit_form.html', context)
    
    else:  # type == 'divise'
        if request.method == 'POST':
            form = CreditDiviseCompletForm(request.POST)
            if form.is_valid():
                try:
                    # Créer le crédit
                    credit = form.save(commit=False)
                    credit.type_credit = 'divise'
                    credit.agent = request.user
                    credit.save()
                    
                    # Récupérer les données du formulaire
                    montant_total = credit.montant_total
                    montant_especes = form.cleaned_data['montant_especes']
                    type_garantie = form.cleaned_data.get('type_garantie')
                    
                    # Créer automatiquement un règlement pour le montant payé en espèces
                    if montant_especes and montant_especes > 0:
                        Reglement.objects.create(
                            credit=credit,
                            montant=montant_especes,
                            date_reglement=date.today(),
                            mode_paiement='especes',
                            statut=None,  # Pas de statut pour les espèces
                            commentaire='Paiement initial en espèces lors de la création du crédit',
                            agent=request.user
                        )
                    
                    # Gérer les chèques de garantie selon le type choisi
                    if type_garantie == 'unique':
                        # Créer un seul chèque de garantie
                        ChequeGarantie.objects.create(
                            credit=credit,
                            numero=form.cleaned_data['numero_cheque_unique'],
                            montant=form.cleaned_data['montant_garantie_unique'],
                            banque=form.cleaned_data['banque_unique'],
                            date_emission=form.cleaned_data['date_emission_unique'],
                            date_echeance=form.cleaned_data['date_reglement_prevu_unique'],
                            commentaire=form.cleaned_data.get('commentaire_unique', '')
                        )
                        
                        # Créer l'alerte pour le chèque de garantie unique
                        Alerte.objects.create(
                            echeance=None,
                            type_alerte='cheque_garantie',
                            message=f'Chèque de garantie unique à traiter pour {credit.client.nom_complet}',
                            date_alerte=date.today(),
                            date_rappel=form.cleaned_data['date_reglement_prevu_unique'],
                            agent=request.user
                        )
                        
                    elif type_garantie == 'multiple':
                        # Créer plusieurs chèques de garantie
                        nombre_cheques = form.cleaned_data['nombre_cheques']
                        
                        for i in range(1, nombre_cheques + 1):
                            # Récupérer les données du formulaire pour chaque chèque
                            numero_cheque = request.POST.get(f'numero_cheque_{i}')
                            banque = request.POST.get(f'banque_{i}')
                            date_emission_str = request.POST.get(f'date_emission_{i}')
                            date_reglement_str = request.POST.get(f'date_reglement_prevu_{i}')
                            montant_cheque_str = request.POST.get(f'montant_garantie_{i}')
                            commentaire = request.POST.get(f'commentaire_{i}', '')
                            
                            # Validation des champs obligatoires
                            if numero_cheque and banque and date_emission_str and date_reglement_str and montant_cheque_str:
                                try:
                                    date_emission = datetime.strptime(date_emission_str, '%Y-%m-%d').date()
                                    date_reglement = datetime.strptime(date_reglement_str, '%Y-%m-%d').date()
                                    montant_cheque = Decimal(montant_cheque_str)
                                    
                                    # Créer le chèque de garantie
                                    ChequeGarantie.objects.create(
                                        credit=credit,
                                        numero=numero_cheque,
                                        montant=montant_cheque,
                                        banque=banque,
                                        date_emission=date_emission,
                                        date_echeance=date_reglement,
                                        commentaire=commentaire
                                    )
                                    
                                    # Créer l'alerte pour le chèque de garantie
                                    Alerte.objects.create(
                                        echeance=None,
                                        type_alerte='cheque_garantie',
                                        message=f'Chèque de garantie {i} à traiter pour {credit.client.nom_complet}',
                                        date_alerte=date.today(),
                                        date_rappel=date_reglement,
                                        agent=request.user
                                    )
                                except (ValueError, TypeError) as e:
                                    messages.error(request, f'Erreur dans les données du chèque {i}: {str(e)}')
                                    continue
                            else:
                                messages.error(request, f'Données manquantes pour le chèque {i}')
                                continue
                    
                    # Créer un log d'action pour la création du crédit
                    ActionLog.objects.create(
                        type_action='credit_creation',
                        description=f'Crédit divisé créé pour {credit.client.nom_complet} - Police {credit.numero_police} - Montant: {credit.montant_total} DH - Espèces: {montant_especes} DH',
                        statut='succes',
                        agent=request.user,
                        client=credit.client,
                        credit=credit,
                        donnees_apres={
                            'numero_police': credit.numero_police,
                            'montant_total': str(credit.montant_total),
                            'montant_especes': str(montant_especes),
                            'type_garantie': type_garantie,
                            'type_credit': credit.type_credit,
                            'description': credit.description,
                            'client': credit.client.nom_complet
                        }
                    )
                    
                    messages.success(request, f'Crédit divisé créé avec succès pour {credit.client.nom_complet}.')
                    return redirect('gestion_credits:credit_detail', pk=credit.pk)
                    
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création du crédit: {str(e)}')
                    # Supprimer le crédit créé en cas d'erreur
                    if 'credit' in locals():
                        credit.delete()
        else:
            form = CreditDiviseCompletForm()
        
        context = {'form': form, 'credit_type': credit_type}
        return render(request, 'gestion_credits/credit_divise_complet_form.html', context)


@login_required
def credit_create_divise_complet(request):
    """Créer un crédit divisé complet avec tous les détails"""
    if request.method == 'POST':
        form = CreditDiviseCompletForm(request.POST)
        if form.is_valid():
            try:
                # Créer le crédit
                credit = form.save(commit=False)
                credit.type_credit = 'divise'
                credit.agent = request.user
                credit.save()
                
                # Créer automatiquement un règlement pour le montant payé en espèces
                montant_especes = form.cleaned_data['montant_especes']
                if montant_especes and montant_especes > 0:
                    Reglement.objects.create(
                        credit=credit,
                        montant=montant_especes,
                        date_reglement=date.today(),
                        mode_paiement='especes',
                        statut=None,  # Pas de statut pour les espèces
                        commentaire='Paiement initial en espèces lors de la création du crédit',
                        agent=request.user
                    )
                    
                    # Recalculer le reste à payer du crédit
                    credit.recalculer_reste_a_payer()
                
                # Récupérer le type de garantie choisi
                type_garantie = form.cleaned_data['type_garantie']
                
                if type_garantie == 'unique':
                    # Créer un seul chèque de garantie
                    ChequeGarantie.objects.create(
                        credit=credit,
                        numero=form.cleaned_data['numero_cheque_unique'],
                        montant=form.cleaned_data['montant_garantie_unique'],
                        banque=form.cleaned_data['banque_unique'],
                        date_emission=form.cleaned_data['date_emission_unique'],
                        date_echeance=form.cleaned_data['date_reglement_prevu_unique'],
                        commentaire=form.cleaned_data.get('commentaire_unique', '')
                    )
                    
                    # Créer l'alerte pour le chèque de garantie unique
                    Alerte.objects.create(
                        echeance=None,
                        type_alerte='cheque_garantie',
                        message=f'Chèque de garantie unique à traiter pour {credit.client.nom_complet}',
                        date_alerte=date.today(),
                        date_rappel=form.cleaned_data['date_reglement_prevu_unique'],
                        agent=request.user
                    )
                    
                elif type_garantie == 'multiple':
                    # Créer plusieurs chèques de garantie
                    nombre_cheques = form.cleaned_data['nombre_cheques']
                    montant_especes = form.cleaned_data['montant_especes']
                    montant_reste = credit.montant_total - montant_especes
                    montant_partie = montant_reste / nombre_cheques
                    
                    for i in range(1, nombre_cheques + 1):
                        # Récupérer les données du formulaire pour chaque chèque
                        numero_cheque = request.POST.get(f'numero_cheque_{i}')
                        banque = request.POST.get(f'banque_{i}')
                        date_emission_str = request.POST.get(f'date_emission_{i}')
                        date_reglement_str = request.POST.get(f'date_reglement_prevu_{i}')
                        montant_cheque_str = request.POST.get(f'montant_garantie_{i}')
                        commentaire = request.POST.get(f'commentaire_{i}', '')
                        
                        # Validation des champs obligatoires
                        if numero_cheque and banque and date_emission_str and date_reglement_str and montant_cheque_str:
                            try:
                                date_emission = datetime.strptime(date_emission_str, '%Y-%m-%d').date()
                                date_reglement = datetime.strptime(date_reglement_str, '%Y-%m-%d').date()
                                montant_cheque = Decimal(montant_cheque_str)
                                
                                # Créer le chèque de garantie
                                ChequeGarantie.objects.create(
                                    credit=credit,
                                    numero=numero_cheque,
                                    montant=montant_cheque,
                                    banque=banque,
                                    date_emission=date_emission,
                                    date_echeance=date_reglement,
                                    commentaire=commentaire
                                )
                                
                                # Créer l'alerte pour le chèque de garantie
                                Alerte.objects.create(
                                    echeance=None,
                                    type_alerte='cheque_garantie',
                                    message=f'Chèque de garantie {i} à traiter pour {credit.client.nom_complet}',
                                    date_alerte=date.today(),
                                    date_rappel=date_reglement,
                                    agent=request.user
                                )
                            except (ValueError, TypeError) as e:
                                messages.error(request, f'Erreur dans les données du chèque {i}: {str(e)}')
                                continue
                        else:
                            messages.error(request, f'Données manquantes pour le chèque {i}')
                            continue
                
                messages.success(request, f'Crédit divisé créé avec succès pour {credit.client.nom_complet}.')
                return redirect('gestion_credits:credit_detail', pk=credit.pk)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du crédit: {str(e)}')
                # Supprimer le crédit créé en cas d'erreur
                if 'credit' in locals():
                    credit.delete()
    else:
        form = CreditDiviseCompletForm()
    
    context = {
        'form': form,
        'action': 'Créer un Crédit Divisé',
    }
    return render(request, 'gestion_credits/credit_divise_complet_form.html', context)


@login_required
def credit_detail(request, pk):
    """Détails d'un crédit"""
    credit = get_object_or_404(Credit, pk=pk)
    echeances = credit.echeances.all().order_by('numero_partie')
    
    # Récupérer les règlements et chèques de garantie
    reglements = credit.reglements.all().order_by('-date_reglement')
    cheques_garantie = credit.cheques_garantie.all().order_by('date_echeance')
    
    # Calculer les compteurs pour le template
    echeances_payees_count = echeances.filter(est_traitee=True).count()
    echeances_en_attente_count = echeances.filter(est_traitee=False).count()
    echeances_en_retard_count = echeances.filter(
        date_echeance__lt=date.today(), 
        est_traitee=False
    ).count()
    
    # Calculer les totaux des règlements
    # Seuls les règlements effectivement versés comptent pour le total payé
    total_reglements_verses = 0
    total_chèques_non_verses = 0
    
    for reglement in reglements:
        if reglement.mode_paiement == 'especes':
            # Les paiements en espèces comptent toujours
            total_reglements_verses += reglement.montant
        elif reglement.mode_paiement == 'cheque' and reglement.statut == 'verse':
            # Seuls les chèques versés comptent
            total_reglements_verses += reglement.montant
        elif reglement.mode_paiement == 'cheque' and reglement.statut == 'non_verse':
            # Les chèques non versés ne comptent pas
            total_chèques_non_verses += reglement.montant
    
    reste_a_payer = credit.montant_total - total_reglements_verses
    
    # Récupérer les chèques de garantie et les diviser par statut
    cheques_garantie = credit.cheques_garantie.all()
    cheques_verses = []
    cheques_non_verses = []
    
    for cheque in cheques_garantie:
        # Déterminer le statut du chèque en regardant les règlements correspondants
        statut_cheque = 'non_verse'  # Par défaut
        for reglement in reglements:
            if (reglement.mode_paiement == 'cheque' and 
                reglement.commentaire and 
                cheque.numero in reglement.commentaire):
                statut_cheque = reglement.statut or 'non_verse'
                break
        
        if statut_cheque == 'verse':
            cheques_verses.append(cheque)
        else:
            cheques_non_verses.append(cheque)
    
    # Calculer le total payé et le reste à payer
    total_paye = getattr(credit, 'total_paye', 0)
    reste_a_payer = getattr(credit, 'reste_a_payer', credit.montant_total)
    
    context = {
        'credit': credit,
        'echeances': echeances,
        'reglements': reglements,
        'cheques_garantie': cheques_garantie,
        'echeances_payees_count': echeances_payees_count,
        'echeances_en_attente_count': echeances_en_attente_count,
        'echeances_en_retard_count': echeances_en_retard_count,
        'total_reglements': total_reglements_verses,
        'total_cheques_non_verses': total_chèques_non_verses,
        'reste_a_payer': reste_a_payer,
        'today': date.today(),
        'today_plus_7': date.today() + timedelta(days=7),
        'cheques_verses': cheques_verses,
        'cheques_non_verses': cheques_non_verses
    }
    return render(request, 'gestion_credits/credit_detail.html', context)


@login_required
def reglement_create(request, credit_id):
    """Créer un nouveau règlement pour un crédit"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        form = ReglementForm(request.POST, credit=credit)
        if form.is_valid():
            reglement = form.save(commit=False)
            reglement.credit = credit
            reglement.agent = request.user
            reglement.save()
            
            # Recalculer le reste à payer du crédit
            credit.recalculer_reste_a_payer()
            
            messages.success(request, f'Règlement de {reglement.montant} DH ajouté avec succès.')
            return redirect('gestion_credits:credit_detail', pk=credit.pk)
    else:
        form = ReglementForm(credit=credit)
    
    context = {
        'form': form,
        'credit': credit,
    }
    return render(request, 'gestion_credits/reglement_form.html', context)


@login_required
def reglement_update(request, pk):
    """Modifier un règlement existant"""
    reglement = get_object_or_404(Reglement, pk=pk)
    credit = reglement.credit
    
    if request.method == 'POST':
        form = ReglementForm(request.POST, instance=reglement, credit=credit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Règlement modifié avec succès.')
            return redirect('gestion_credits:credit_detail', pk=credit.pk)
    else:
        form = ReglementForm(instance=reglement, credit=credit)
    
    context = {
        'form': form,
        'reglement': reglement,
        'credit': credit,
    }
    return render(request, 'gestion_credits/reglement_form.html', context)


@login_required
def reglement_delete(request, pk):
    """Supprimer un règlement"""
    reglement = get_object_or_404(Reglement, pk=pk)
    credit = reglement.credit
    
    if request.method == 'POST':
        reglement.delete()
        messages.success(request, 'Règlement supprimé avec succès.')
        return redirect('gestion_credits:credit_detail', pk=credit.pk)
    
    context = {
        'reglement': reglement,
        'credit': credit,
    }
    return render(request, 'gestion_credits/reglement_confirm_delete.html', context)


@login_required
def cheque_garantie_create(request, credit_id):
    """Créer un nouveau chèque de garantie pour un crédit"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        form = ChequeGarantieForm(request.POST)
        if form.is_valid():
            cheque = form.save(commit=False)
            cheque.credit = credit
            cheque.save()
            
            messages.success(request, f'Chèque de garantie {cheque.numero} ajouté avec succès.')
            return redirect('gestion_credits:credit_detail', pk=credit.pk)
    else:
        form = ChequeGarantieForm()
    
    context = {
        'form': form,
        'credit': credit,
    }
    return render(request, 'gestion_credits/cheque_garantie_form.html', context)


@login_required
def cheque_garantie_update(request, pk):
    """Modifier un chèque de garantie existant"""
    cheque = get_object_or_404(ChequeGarantie, pk=pk)
    credit = cheque.credit
    
    if request.method == 'POST':
        form = ChequeGarantieForm(request.POST, instance=cheque)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chèque de garantie modifié avec succès.')
            return redirect('gestion_credits:credit_detail', pk=credit.pk)
    else:
        form = ChequeGarantieForm(instance=cheque)
    
    context = {
        'form': form,
        'cheque': cheque,
        'credit': credit,
    }
    return render(request, 'gestion_credits/cheque_garantie_form.html', context)


@login_required
def cheque_garantie_delete(request, pk):
    """Supprimer un chèque de garantie"""
    cheque = get_object_or_404(ChequeGarantie, pk=pk)
    credit = cheque.credit
    
    if request.method == 'POST':
        cheque.delete()
        messages.success(request, 'Chèque de garantie supprimé avec succès.')
        return redirect('gestion_credits:credit_detail', pk=credit.pk)
    
    context = {
        'cheque': cheque,
        'credit': credit,
    }
    return render(request, 'gestion_credits/cheque_garantie_confirm_delete.html', context)


@login_required
def credit_delete(request, pk):
    """Supprimer un crédit"""
    credit = get_object_or_404(Credit, pk=pk)
    if request.method == 'POST':
        credit.delete()
        messages.success(request, f'Crédit supprimé avec succès.')
        return redirect('gestion_credits:credit_list')
    
    context = {'credit': credit}
    return render(request, 'gestion_credits/credit_confirm_delete.html', context)


@login_required
def echeance_create_for_credit(request, credit_id):
    """Ajouter des paiements pour un crédit (espèces ou effets)"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        type_paiement = request.POST.get('type_paiement')
        montant_str = request.POST.get('montant')
        date_paiement_str = request.POST.get('date_paiement')
        commentaire = request.POST.get('commentaire', '')
        
        # Validation des champs obligatoires
        if not all([type_paiement, montant_str, date_paiement_str]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                'credit': credit,
                'today': date.today(),
                'reglements': credit.reglements.all().order_by('-date_reglement'),
                'total_paye': getattr(credit, 'total_paye', 0),
                'reste_a_payer': getattr(credit, 'reste_a_payer', credit.montant_total)
            })
        
        try:
            montant = Decimal(montant_str)
            date_paiement = datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
            
            # Validation du montant
            if montant <= 0:
                messages.error(request, 'Le montant doit être supérieur à 0.')
                return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                    'credit': credit,
                    'today': date.today(),
                    'reglements': credit.reglements.all().order_by('-date_reglement'),
                    'total_paye': getattr(credit, 'total_paye', 0),
                    'reste_a_payer': getattr(credit, 'reste_a_payer', credit.montant_total)
                })
            
            # Vérifier que le montant ne dépasse pas le reste à payer
            reste_a_payer = getattr(credit, 'reste_a_payer', credit.montant_total)
            if montant > reste_a_payer:
                messages.error(request, f'Le montant ({montant:.2f} DH) ne peut pas dépasser le reste à payer ({reste_a_payer:.2f} DH).')
                return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                    'credit': credit,
                    'today': date.today(),
                    'reglements': credit.reglements.all().order_by('-date_reglement'),
                    'total_paye': getattr(credit, 'total_paye', 0),
                    'reste_a_payer': reste_a_payer
                })
            
            # Validation de la date
            if date_paiement > date.today():
                messages.error(request, 'La date de paiement ne peut pas être dans le futur.')
                return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                    'credit': credit,
                    'today': date.today(),
                    'reglements': credit.reglements.all().order_by('-date_reglement'),
                    'total_paye': getattr(credit, 'total_paye', 0),
                    'reste_a_payer': reste_a_payer
                })
            
        except (ValueError, TypeError):
            messages.error(request, 'Format de données invalide.')
            return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                'credit': credit,
                'today': date.today(),
                'reglements': credit.reglements.all().order_by('-date_reglement'),
                'total_paye': getattr(credit, 'total_paye', 0),
                'reste_a_payer': getattr(credit, 'reste_a_payer', credit.montant_total)
            })
        
        # Créer le paiement selon le type
        try:
            if type_paiement == 'especes':
                # Créer un règlement en espèces
                reglement = Reglement.objects.create(
                    credit=credit,
                    montant=montant,
                    date_reglement=date_paiement,
                    mode_paiement='especes',
                    commentaire=f"Paiement en espèces - {commentaire}",
                    agent=request.user
                )
                
                # Créer une alerte pour le paiement
                Alerte.objects.create(
                    echeance=None,
                    type_alerte='paiement',
                    message=f'Paiement en espèces de {montant:.2f} DH reçu pour {credit.client.nom_complet}',
                    date_alerte=date.today(),
                    date_rappel=date_paiement,
                    agent=request.user
                )
            
                messages.success(request, f'Paiement en espèces de {montant:.2f} DH ajouté avec succès.')
                
            elif type_paiement == 'effet':
                # Récupérer les informations de l'effet
                banque = request.POST.get('banque')
                numero_effet = request.POST.get('numero_effet')
                date_emission_str = request.POST.get('date_emission')
                date_echeance_str = request.POST.get('date_echeance')
                statut_cheque = request.POST.get('statut_cheque', 'non_verse')
                
                # Validation des champs obligatoires pour les effets
                if not all([banque, numero_effet, date_emission_str, date_echeance_str]):
                    messages.error(request, 'Tous les champs pour l\'effet sont obligatoires.')
                    return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                        'credit': credit,
                        'today': date.today(),
                        'reglements': credit.reglements.all().order_by('-date_reglement'),
                        'total_paye': getattr(credit, 'total_paye', 0),
                        'reste_a_payer': reste_a_payer
                    })
                
                try:
                    date_emission = datetime.strptime(date_emission_str, '%Y-%m-%d').date()
                    date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
                    
                    # Validation des dates
                    if date_emission > date.today():
                        messages.error(request, 'La date d\'émission ne peut pas être dans le futur.')
                        return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                            'credit': credit,
                            'today': date.today(),
                            'reglements': credit.reglements.all().order_by('-date_reglement'),
                            'total_paye': getattr(credit, 'total_paye', 0),
                            'reste_a_payer': reste_a_payer
                        })
                    
                    if date_echeance < date.today():
                        messages.error(request, 'La date d\'échéance ne peut pas être dans le passé.')
                        return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                            'credit': credit,
                            'today': date.today(),
                            'reglements': credit.reglements.all().order_by('-date_reglement'),
                            'total_paye': getattr(credit, 'total_paye', 0),
                            'reste_a_payer': reste_a_payer
                        })
                    
                except (ValueError, TypeError):
                    messages.error(request, 'Format de dates invalide pour l\'effet.')
                    return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                        'credit': credit,
                        'today': date.today(),
                        'reglements': credit.reglements.all().order_by('-date_reglement'),
                        'total_paye': getattr(credit, 'total_paye', 0),
                        'reste_a_payer': reste_a_payer
                    })
                
                # Créer un règlement par effet avec le statut approprié
                reglement = Reglement.objects.create(
                    credit=credit,
                    montant=montant,
                    date_reglement=date_echeance,
                    mode_paiement='cheque',
                    statut=statut_cheque,
                    commentaire=f"Effet {numero_effet} - {banque} - {commentaire}",
                    agent=request.user
                )
                
                # Créer le chèque
                cheque = ChequeGarantie.objects.create(
                    credit=credit,
                    numero=numero_effet,
                    montant=montant,
                    banque=banque,
                    date_emission=date_emission,
                    date_echeance=date_echeance,
                    commentaire=f"Effet pour {credit.client.nom_complet} - {commentaire}"
                )
                
                # Créer une alerte pour l'effet seulement si non versé
                if statut_cheque == 'non_verse':
                    Alerte.objects.create(
                        echeance=None,
                        type_alerte='cheque_garantie',
                        message=f'Effet {numero_effet} de {montant:.2f} DH à encaisser pour {credit.client.nom_complet}',
                        date_alerte=date.today(),
                        date_rappel=date_echeance,
                        agent=request.user
                    )
                
                # Message de succès adapté au statut
                if statut_cheque == 'verse':
                    messages.success(request, f'Effet de {montant:.2f} DH déjà versé ajouté avec succès.')
                else:
                    messages.success(request, f'Effet de {montant:.2f} DH à encaisser ajouté avec succès.')
            
            # Mettre à jour le reste à payer du crédit
            credit.reste_a_payer = max(0, reste_a_payer - montant)
            credit.save()
            
            # Créer un log d'action
            ActionLog.objects.create(
                type_action='paiement_ajoute',
                description=f'Paiement de {montant:.2f} DH ajouté pour {credit.client.nom_complet} - Police {credit.numero_police}',
                statut='succes',
                agent=request.user,
                client=credit.client,
                credit=credit,
                donnees_apres={
                    'montant': str(montant),
                    'type_paiement': type_paiement,
                    'reste_a_payer': str(credit.reste_a_payer),
                    'date_paiement': date_paiement.strftime('%Y-%m-%d')
                }
            )
            
            return redirect('gestion_credits:credit_detail', pk=credit.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du paiement : {str(e)}')
            return render(request, 'gestion_credits/echeance_create_for_credit.html', {
                'credit': credit,
                'today': date.today(),
                'reglements': credit.reglements.all().order_by('-date_reglement'),
                'total_paye': getattr(credit, 'total_paye', 0),
                'reste_a_payer': getattr(credit, 'reste_a_payer', credit.montant_total)
            })
    
    # Récupérer l'historique des paiements
    reglements = credit.reglements.all().order_by('-date_reglement')
    
    # Récupérer les chèques de garantie et les diviser par statut
    cheques_garantie = credit.cheques_garantie.all()
    cheques_verses = []
    cheques_non_verses = []
    
    for cheque in cheques_garantie:
        # Déterminer le statut du chèque en regardant les règlements correspondants
        statut_cheque = 'non_verse'  # Par défaut
        for reglement in reglements:
            if (reglement.mode_paiement == 'cheque' and 
                reglement.commentaire and 
                cheque.numero in reglement.commentaire):
                statut_cheque = reglement.statut or 'non_verse'
                break
        
        if statut_cheque == 'verse':
            cheques_verses.append(cheque)
        else:
            cheques_non_verses.append(cheque)
    
    # Calculer le total payé et le reste à payer
    total_paye = getattr(credit, 'total_paye', 0)
    reste_a_payer = getattr(credit, 'reste_a_payer', credit.montant_total)
    
    context = {
        'credit': credit,
        'today': date.today(),
        'reglements': reglements,
        'total_paye': total_paye,
        'reste_a_payer': reste_a_payer,
        'cheques_garantie': cheques_garantie,
        'cheques_verses': cheques_verses,
        'cheques_non_verses': cheques_non_verses
    }
    
    return render(request, 'gestion_credits/echeance_create_for_credit.html', context)


@login_required
def alerte_list(request):
    """Système d'alertes professionnel et optimisé pour les paiements proches"""
    today = date.today()
    
    # === FILTRES ET RECHERCHE ===
    statut_filter = request.GET.get('statut', '')
    type_filter = request.GET.get('type', '')
    urgence_filter = request.GET.get('urgence', '')
    search_query = request.GET.get('search', '')
    agent_filter = request.GET.get('agent', '')
    
    # === ALERTES URGENTES (AUJOURD'HUI ET EN RETARD) ===
    alertes_urgentes = []
    
    # Chèques arrivant à échéance aujourd'hui
    cheques_aujourd_hui = ChequeGarantie.objects.filter(
        date_echeance=today
    ).select_related('credit__client', 'credit__agent').order_by('montant')
    
    for cheque in cheques_aujourd_hui:
        alertes_urgentes.append({
            'type': 'cheque_echeance_aujourd_hui',
            'urgence': 'critique',
            'titre': f'Chèque à échéance aujourd\'hui',
            'message': f'Chèque {cheque.numero} de {cheque.montant} DH',
            'client': cheque.credit.client,
            'credit': cheque.credit,
            'agent': cheque.credit.agent,
            'date_rappel': today,
            'montant': cheque.montant,
            'banque': cheque.banque,
            'numero_cheque': cheque.numero,
            'objet': cheque
        })
    
    # Chèques en retard
    cheques_en_retard = ChequeGarantie.objects.filter(
        date_echeance__lt=today
    ).select_related('credit__client', 'credit__agent').order_by('date_echeance')
    
    for cheque in cheques_en_retard:
        jours_retard = (today - cheque.date_echeance).days
        alertes_urgentes.append({
            'type': 'cheque_en_retard',
            'urgence': 'critique',
            'titre': f'Chèque en retard de {jours_retard} jour(s)',
            'message': f'Chèque {cheque.numero} de {cheque.montant} DH',
            'client': cheque.credit.client,
            'credit': cheque.credit,
            'agent': cheque.credit.agent,
            'date_rappel': cheque.date_echeance,
            'montant': cheque.montant,
            'banque': cheque.banque,
            'numero_cheque': cheque.numero,
            'jours_retard': jours_retard,
            'objet': cheque
        })
    
    # === ALERTES IMPORTANTES (7 PROCHAINS JOURS) ===
    alertes_importantes = []
    
    # Chèques arrivant à échéance dans les 7 prochains jours
    cheques_semaine_prochaine = ChequeGarantie.objects.filter(
        date_echeance__range=[today + timedelta(days=1), today + timedelta(days=7)]
    ).select_related('credit__client', 'credit__agent').order_by('date_echeance')
    
    for cheque in cheques_semaine_prochaine:
        jours_restants = (cheque.date_echeance - today).days
        alertes_importantes.append({
            'type': 'cheque_echeance_proche',
            'urgence': 'importante',
            'titre': f'Chèque à échéance dans {jours_restants} jour(s)',
            'message': f'Chèque {cheque.numero} de {cheque.montant} DH',
            'client': cheque.credit.client,
            'credit': cheque.credit,
            'agent': cheque.credit.agent,
            'date_rappel': cheque.date_echeance,
            'montant': cheque.montant,
            'banque': cheque.banque,
            'numero_cheque': cheque.numero,
            'jours_restants': jours_restants,
            'objet': cheque
        })
    
    # === ALERTES INFORMATIVES (30 PROCHAINS JOURS) ===
    alertes_informatives = []
    
    # Chèques arrivant à échéance dans les 30 prochains jours
    cheques_mois_prochain = ChequeGarantie.objects.filter(
        date_echeance__range=[today + timedelta(days=8), today + timedelta(days=30)]
    ).select_related('credit__client', 'credit__agent').order_by('date_echeance')
    
    for cheque in cheques_mois_prochain:
        jours_restants = (cheque.date_echeance - today).days
        alertes_informatives.append({
            'type': 'cheque_echeance_mensuelle',
            'urgence': 'informatif',
            'titre': f'Chèque à échéance dans {jours_restants} jour(s)',
            'message': f'Chèque {cheque.numero} de {cheque.montant} DH',
            'client': cheque.credit.client,
            'credit': cheque.credit,
            'agent': cheque.credit.agent,
            'date_rappel': cheque.date_echeance,
            'montant': cheque.montant,
            'banque': cheque.banque,
            'numero_cheque': cheque.numero,
            'jours_restants': jours_restants,
            'objet': cheque
        })
    
    # === FILTRAGE DES ALERTES ===
    toutes_alertes = alertes_urgentes + alertes_importantes + alertes_informatives
    
    # Filtre par agent
    if agent_filter:
        toutes_alertes = [a for a in toutes_alertes if a['agent'].username == agent_filter]
    
    # Filtre par urgence
    if urgence_filter == 'critique':
        toutes_alertes = [a for a in toutes_alertes if a['urgence'] == 'critique']
    elif urgence_filter == 'importante':
        toutes_alertes = [a for a in toutes_alertes if a['urgence'] in ['critique', 'importante']]
    
    # Filtre par recherche
    if search_query:
        toutes_alertes = [a for a in toutes_alertes if 
            search_query.lower() in a['client'].nom_complet.lower() or
            search_query.lower() in a['credit'].numero_police.lower() or
            search_query.lower() in a['numero_cheque'].lower()
        ]
    
    # === STATISTIQUES ===
    total_alertes = len(toutes_alertes)
    alertes_critiques = len([a for a in toutes_alertes if a['urgence'] == 'critique'])
    alertes_importantes = len([a for a in toutes_alertes if a['urgence'] == 'importante'])
    alertes_informatives = len([a for a in toutes_alertes if a['urgence'] == 'informatif'])
    
    montant_total_urgent = sum(a['montant'] for a in toutes_alertes if a['urgence'] == 'critique')
    montant_total_important = sum(a['montant'] for a in toutes_alertes if a['urgence'] == 'importante')
    
    # === PAGINATION ===
    paginator = Paginator(toutes_alertes, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # === AGENTS DISPONIBLES POUR FILTRE ===
    agents_disponibles = User.objects.filter(
        credits_geres__isnull=False
    ).distinct().order_by('username')
    
    context = {
        'page_obj': page_obj,
        'total_alertes': total_alertes,
        'alertes_critiques': alertes_critiques,
        'alertes_importantes': alertes_importantes,
        'alertes_informatives': alertes_informatives,
        'montant_total_urgent': montant_total_urgent,
        'montant_total_important': montant_total_important,
        
        # Filtres
        'statut_filter': statut_filter,
        'type_filter': type_filter,
        'urgence_filter': urgence_filter,
        'search_query': search_query,
        'agent_filter': agent_filter,
        'agents_disponibles': agents_disponibles,
        
        # Date
        'today': today,
        'date_plus_7': today + timedelta(days=7),
        'date_plus_30': today + timedelta(days=30),
    }
    
    return render(request, 'gestion_credits/alerte_list.html', context)


@login_required
def alerte_traiter(request, pk):
    """Traiter une alerte"""
    alerte = get_object_or_404(Alerte, pk=pk)
    
    if request.method == 'POST':
        form = AlerteForm(request.POST, instance=alerte)
        if form.is_valid():
            alerte = form.save(commit=False)
            alerte.date_traitement = timezone.now()
            alerte.save()
            
            messages.success(request, 'Alerte traitée avec succès.')
            return redirect('gestion_credits:alerte_list')
    else:
        form = AlerteForm(instance=alerte)
    
    context = {'form': form, 'alerte': alerte}
    return render(request, 'gestion_credits/alerte_traiter.html', context)


def user_login(request):
    """Connexion utilisateur"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('gestion_credits:dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'gestion_credits/login.html')


def user_register(request):
    """Inscription utilisateur"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('gestion_credits:user_login')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'gestion_credits/register.html')


def user_logout(request):
    """Déconnexion utilisateur"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('gestion_credits:user_login')


# Vues AJAX pour le tableau de bord
@login_required
def dashboard_stats(request):
    """Statistiques AJAX pour le tableau de bord"""
    today = date.today()
    
    stats = {
        'echeances_aujourd_hui': Echeance.objects.filter(
            date_echeance=today, est_traitee=False
        ).count(),
        'echeances_semaine': Echeance.objects.filter(
            date_echeance__range=[today, today + timedelta(days=7)],
            est_traitee=False
        ).count(),
        'echeances_retard': Echeance.objects.filter(
            date_echeance__lt=today, est_traitee=False
        ).count(),
        'alertes_en_attente': Alerte.objects.filter(statut='en_attente').count(),
    }
    
    return JsonResponse(stats)


@login_required
def gerer_cheque_garantie(request, pk):
    """Gérer un chèque de garantie (modifier, changer le statut)"""
    cheque = get_object_or_404(Cheque, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'encaisser':
            # Marquer le chèque comme "à encaisser"
            cheque.statut = 'encaisser'
            cheque.save()
            
            # Créer une alerte pour le dépôt
            Alerte.objects.create(
                echeance=cheque.echeance,
                type_alerte='cheque_garantie',
                message=f'Déposer le chèque de garantie pour {cheque.echeance.credit.client.nom_complet}',
                date_alerte=date.today(),
                date_rappel=date.today() + timedelta(days=1),
                agent=request.user
            )
            
            messages.success(request, 'Chèque marqué pour encaissement. Alerte créée pour le dépôt.')
            
        elif action == 'contacter_client':
            # Créer une alerte pour contacter le client
            Alerte.objects.create(
                echeance=cheque.echeance,
                type_alerte='rappel',
                message=f'Contacter {cheque.echeance.credit.client.nom_complet} pour règlement en espèces (chèque de garantie)',
                date_alerte=date.today(),
                date_rappel=date.today() + timedelta(days=1),
                agent=request.user
            )
            
            messages.success(request, 'Alerte créée pour contacter le client.')
            
        elif action == 'reporter':
            # Reporter la date de règlement
            nouvelle_date = request.POST.get('nouvelle_date')
            if nouvelle_date:
                try:
                    nouvelle_date = datetime.strptime(nouvelle_date, '%Y-%m-%d').date()
                    if nouvelle_date > date.today():
                        cheque.date_reglement_prevu = nouvelle_date
                        cheque.save()
                        
                        # Créer une nouvelle alerte
                        Alerte.objects.create(
                            echeance=cheque.echeance,
                            type_alerte='cheque_garantie',
                            message=f'Contacter {cheque.echeance.credit.client.nom_complet} pour règlement reporté (chèque de garantie)',
                            date_alerte=date.today(),
                            date_rappel=nouvelle_date,
                            agent=request.user
                        )
                        
                        messages.success(request, f'Date de règlement reportée au {nouvelle_date}.')
                    else:
                        messages.error(request, 'La nouvelle date doit être dans le futur.')
                except ValueError:
                    messages.error(request, 'Format de date invalide.')
            else:
                messages.error(request, 'Veuillez spécifier une nouvelle date.')
        
        return redirect('gestion_credits:credit_detail', pk=cheque.echeance.credit.pk)
    
    context = {'cheque': cheque}
    return render(request, 'gestion_credits/gerer_cheque_garantie.html', context)


@login_required
def historique_actions(request):
    """Vue pour afficher l'historique des actions des agents et clients"""
    
    # Récupération des paramètres de filtrage
    type_action_filter = request.GET.get('type_action', '')
    statut_filter = request.GET.get('statut', '')
    agent_filter = request.GET.get('agent', '')
    client_filter = request.GET.get('client', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    search_query = request.GET.get('search', '')
    
    # Récupération des actions avec relations
    actions = ActionLog.objects.all().select_related(
        'agent', 'client', 'credit', 'echeance'
    ).order_by('-date_action')
    
    # Application des filtres
    if type_action_filter:
        actions = actions.filter(type_action=type_action_filter)
    
    if statut_filter:
        actions = actions.filter(statut=statut_filter)
    
    if agent_filter:
        actions = actions.filter(agent__username__icontains=agent_filter)
    
    if client_filter:
        actions = actions.filter(
            Q(client__nom__icontains=client_filter) |
            Q(client__prenom__icontains=client_filter)
        )
    
    if date_debut:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            actions = actions.filter(date_action__date__gte=date_debut_obj)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            actions = actions.filter(date_action__date__lte=date_fin_obj)
        except ValueError:
            pass
    
    if search_query:
        actions = actions.filter(
            Q(description__icontains=search_query) |
            Q(agent__username__icontains=search_query) |
            Q(client__nom__icontains=search_query) |
            Q(client__prenom__icontains=search_query) |
            Q(credit__numero_police__icontains=search_query)
        )
    
    # Statistiques globales
    total_actions = actions.count()
    actions_aujourd_hui = actions.filter(date_action__date=date.today()).count()
    actions_cette_semaine = actions.filter(
        date_action__date__gte=date.today() - timedelta(days=7)
    ).count()
    
    # Répartition par type d'action
    repartition_types = actions.values('type_action').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Répartition par statut
    repartition_statuts = actions.values('statut').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Actions urgentes (nécessitant une attention)
    actions_urgentes = actions.filter(
        type_action__in=['echeance_paiement', 'alerte_creation', 'credit_validation'],
        statut__in=['en_cours', 'en_attente']
    )[:5]
    
    # Pagination
    paginator = Paginator(actions, 25)  # 25 actions par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
        # Préparation du contexte
    context = {
        'page_obj': page_obj,
        'total_actions': total_actions,
        'actions_aujourd_hui': actions_aujourd_hui,
        'actions_cette_semaine': actions_cette_semaine,
        'repartition_types': repartition_types,
        'repartition_statuts': repartition_statuts,
        'actions_urgentes': actions_urgentes,
        
        # Filtres appliqués
        'type_action_filter': type_action_filter,
        'statut_filter': statut_filter,
        'agent_filter': agent_filter,
        'client_filter': client_filter,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'search_query': search_query,
        
        # Choix pour les filtres
        'type_action_choices': ActionLog.TYPE_ACTION_CHOICES,
        'statut_choices': ActionLog.STATUT_CHOICES,
        
        # Agents disponibles pour le filtre
        'agents_disponibles': User.objects.filter(
            actions_effectuees__isnull=False
        ).distinct().order_by('username'),
        
        # Clients disponibles pour le filtre
        'clients_disponibles': Client.objects.filter(
            actions_historique__isnull=False
        ).distinct().order_by('nom')[:50],  # Limiter à 50 clients
    }
    
    return render(request, 'gestion_credits/historique_actions.html', context)


@login_required
def paiement_echeance_create(request, credit_id):
    """Créer un système professionnel de paiement des échéances"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        form = PaiementEcheanceForm(request.POST, credit=credit)
        if form.is_valid():
            try:
                mode_paiement = form.cleaned_data['mode_paiement']
                type_echeance = form.cleaned_data['type_echeance']
                
                if type_echeance == 'unique':
                    # Créer une seule échéance
                    montant = form.cleaned_data['montant_echeance_unique']
                    date_echeance = form.cleaned_data['date_echeance_unique']
                    
                    # Créer l'échéance
                    echeance = Echeance.objects.create(
                        credit=credit,
                        numero_partie=credit.echeances.count() + 1,
                        montant=montant,
                        date_echeance=date_echeance,
                        est_especes=(mode_paiement == 'especes'),
                        commentaire=form.cleaned_data.get('commentaire', '')
                    )
                    
                    # Créer le règlement correspondant
                    Reglement.objects.create(
                        credit=credit,
                        montant=montant,
                        date_reglement=date.today(),
                        mode_paiement='especes' if mode_paiement == 'especes' else 'cheque',
                        statut='verse' if mode_paiement == 'especes' else 'non_verse',
                        commentaire=f"Échéance unique - {form.cleaned_data.get('commentaire', '')}",
                        agent=request.user
                    )
                    
                    # Si c'est un effet, créer un chèque de garantie
                    if mode_paiement == 'effets':
                        Cheque.objects.create(
                            echeance=echeance,
                            numero_cheque=form.cleaned_data['numero_effet'],
                            banque=form.cleaned_data['banque_emetteur'],
                            date_emission=form.cleaned_data['date_emission_effet'],
                            date_reglement_prevu=date_echeance,
                            montant=montant,
                            statut='garantie',
                            remarques=form.cleaned_data.get('commentaire', '')
                        )
                    
                    # Créer l'alerte
                    Alerte.objects.create(
                        echeance=echeance,
                        type_alerte='echeance',
                        message=f'Échéance unique pour {credit.client.nom_complet} - {montant} DH',
                        date_alerte=date.today(),
                        date_rappel=date_echeance,
                        agent=request.user
                    )
                    
                    messages.success(request, f'Échéance unique créée avec succès pour {montant} DH.')
                    
                elif type_echeance == 'multiple':
                    # Créer plusieurs échéances échelonnées
                    nombre_echeances = form.cleaned_data['nombre_echeances']
                    frequence = form.cleaned_data['frequence_paiement']
                    date_premiere = form.cleaned_data['date_premiere_echeance']
                    montant_total = credit.reste_a_payer
                    montant_partie = montant_total / nombre_echeances
                    
                    # Calculer les intervalles selon la fréquence
                    if frequence == 'hebdomadaire':
                        intervalle_jours = 7
                    elif frequence == 'bimensuelle':
                        intervalle_jours = 15
                    elif frequence == 'mensuelle':
                        intervalle_jours = 30
                    elif frequence == 'trimestrielle':
                        intervalle_jours = 90
                    
                    for i in range(nombre_echeances):
                        # Calculer la date de cette échéance
                        date_echeance = date_premiere + timedelta(days=i * intervalle_jours)
                        
                        # Créer l'échéance
                        echeance = Echeance.objects.create(
                            credit=credit,
                            numero_partie=credit.echeances.count() + 1,
                            montant=montant_partie,
                            date_echeance=date_echeance,
                            est_especes=(mode_paiement == 'especes'),
                            commentaire=f"Échéance {i+1}/{nombre_echeances} - {frequence} - {form.cleaned_data.get('commentaire', '')}"
                        )
                        
                        # Créer le règlement correspondant
                        Reglement.objects.create(
                            credit=credit,
                            montant=montant_partie,
                            date_reglement=date.today(),
                            mode_paiement='especes' if mode_paiement == 'especes' else 'cheque',
                            statut='verse' if mode_paiement == 'especes' else 'non_verse',
                            commentaire=f"Échéance {i+1}/{nombre_echeances} - {frequence}",
                            agent=request.user
                        )
                        
                        # Si c'est un effet, créer un chèque de garantie
                        if mode_paiement == 'effets':
                            Cheque.objects.create(
                                echeance=echeance,
                                numero_cheque=f"{form.cleaned_data['numero_effet']}-{i+1}",
                                banque=form.cleaned_data['banque_emetteur'],
                                date_emission=form.cleaned_data['date_emission_effet'],
                                date_reglement_prevu=date_echeance,
                                montant=montant_partie,
                                statut='garantie',
                                remarques=f"Échéance {i+1}/{nombre_echeances} - {form.cleaned_data.get('commentaire', '')}"
                            )
                        
                        # Créer l'alerte
                        Alerte.objects.create(
                            echeance=echeance,
                            type_alerte='echeance',
                            message=f'Échéance {i+1}/{nombre_echeances} pour {credit.client.nom_complet} - {montant_partie} DH',
                            date_alerte=date.today(),
                            date_rappel=date_echeance,
                            agent=request.user
                        )
                    
                    messages.success(request, f'{nombre_echeances} échéances créées avec succès selon un échéancier {frequence}.')
                
                # Recalculer le reste à payer du crédit
                credit.recalculer_reste_a_payer()
                
                return redirect('gestion_credits:credit_detail', pk=credit.pk)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création des échéances: {str(e)}')
    else:
        form = PaiementEcheanceForm(credit=credit)
    
    context = {
        'form': form,
        'credit': credit,
    }
    return render(request, 'gestion_credits/paiement_echeance_form.html', context)


@login_required
def ajout_paiement_create(request, credit_id):
    """Ajouter un paiement simplifié (espèces ou effets)"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        form = AjoutPaiementForm(request.POST, credit=credit)
        if form.is_valid():
            try:
                mode_paiement = form.cleaned_data['mode_paiement']
                montant = form.cleaned_data['montant']
                date_paiement = form.cleaned_data['date_paiement']
                commentaire = form.cleaned_data.get('commentaire', '')
                
                # Vérifier que le montant ne dépasse pas le reste à payer
                if montant > credit.reste_a_payer:
                    messages.error(request, f'Le montant ({montant} DH) ne peut pas dépasser le reste à payer ({credit.reste_a_payer} DH).')
                    return render(request, 'gestion_credits/ajout_paiement_form.html', {'form': form, 'credit': credit})
                
                # Créer le règlement
                reglement = Reglement.objects.create(
                    credit=credit,
                    montant=montant,
                    date_reglement=date_paiement,
                    mode_paiement='especes' if mode_paiement == 'especes' else 'cheque',
                    statut='verse' if mode_paiement == 'especes' else 'non_verse',
                    commentaire=commentaire,
                    agent=request.user
                )
                
                # Si c'est un effet, créer un chèque de garantie
                if mode_paiement == 'effets':
                    numero_effet = form.cleaned_data['numero_effet']
                    banque = form.cleaned_data['banque_emetteur']
                    date_emission = form.cleaned_data['date_emission_effet']
                    
                    # Créer le chèque de garantie
                    ChequeGarantie.objects.create(
                        credit=credit,
                        numero=numero_effet,
                        montant=montant,
                        banque=banque,
                        date_emission=date_emission,
                        date_echeance=date_paiement,
                        commentaire=f"Effet pour paiement: {commentaire}"
                    )
                
                # Recalculer le reste à payer du crédit
                credit.recalculer_reste_a_payer()
                
                # Créer un log d'action
                ActionLog.objects.create(
                    agent=request.user,
                    action='ajout_paiement',
                    donnees_avant={
                        'numero_police': credit.numero_police,
                        'reste_a_payer_avant': str(credit.reste_a_payer + montant),
                        'client': credit.client.nom_complet
                    },
                    donnees_apres={
                        'numero_police': credit.numero_police,
                        'mode_paiement': mode_paiement,
                        'montant': str(montant),
                        'date_paiement': str(date_paiement),
                        'reste_a_payer_apres': str(credit.reste_a_payer),
                        'client': credit.client.nom_complet
                    }
                )
                
                messages.success(request, f'Paiement de {montant} DH ajouté avec succès en mode {mode_paiement}.')
                return redirect('gestion_credits:credit_detail', pk=credit.pk)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout du paiement: {str(e)}')
    else:
        form = AjoutPaiementForm(credit=credit)
    
    context = {
        'form': form,
        'credit': credit,
    }
    return render(request, 'gestion_credits/ajout_paiement_form.html', context)


@login_required
def payer_cheque_especes(request, credit_id):
    """Permettre à un agent de marquer un chèque non versé comme payé en espèces par le client"""
    credit = get_object_or_404(Credit, pk=credit_id)
    
    if request.method == 'POST':
        try:
            cheque_id = request.POST.get('cheque_id')
            montant_str = request.POST.get('montant', '0')
            date_paiement_str = request.POST.get('date_paiement', '')
            commentaire = request.POST.get('commentaire', '')
            
            # Validation des données
            if not cheque_id or not montant_str or not date_paiement_str:
                messages.error(request, "Données manquantes pour le traitement du paiement.")
                return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
            # Nettoyer et valider le montant
            montant_str = montant_str.strip().replace(',', '.')
            if not montant_str or montant_str == '':
                messages.error(request, 'Le montant ne peut pas être vide.')
                return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
            try:
                montant = Decimal(montant_str)
                if montant <= 0:
                    messages.error(request, 'Le montant doit être supérieur à 0.')
                    return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            except (ValueError, TypeError, Exception) as e:
                messages.error(request, f'Format de montant invalide : {montant_str}. Utilisez un nombre décimal valide (ex: 100.50).')
                return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
            try:
                date_paiement = datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Format de date invalide.')
                return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
            # Récupérer le chèque de garantie
            cheque = get_object_or_404(ChequeGarantie, pk=cheque_id, credit=credit)
            
            # Vérifier que le chèque n'est pas déjà versé
            if hasattr(cheque, 'reglement') and cheque.reglement.statut == 'verse':
                messages.error(request, 'Ce chèque est déjà versé.')
                return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
            # Trouver le règlement existant pour ce chèque (s'il existe)
            reglement_existant = None
            for reglement in credit.reglements.all():
                if (reglement.mode_paiement == 'cheque' and 
                    reglement.commentaire and 
                    cheque.numero in reglement.commentaire):
                    reglement_existant = reglement
                    break
            
            # Si un règlement existe, le mettre à jour en espèces
            if reglement_existant:
                reglement_existant.mode_paiement = 'especes'
                reglement_existant.statut = 'verse'
                reglement_existant.date_reglement = date_paiement
                reglement_existant.commentaire = f"Paiement en espèces du chèque {cheque.numero} - {commentaire}"
                reglement_existant.save()
                reglement = reglement_existant
            else:
                # Créer un nouveau règlement en espèces
                reglement = Reglement.objects.create(
                    credit=credit,
                    montant=montant,
                    date_reglement=date_paiement,
                    mode_paiement='especes',
                    statut='verse',
                    commentaire=f"Paiement en espèces du chèque {cheque.numero} - {commentaire}",
                    agent=request.user
                )
            
            # Supprimer le chèque de garantie car il a été payé en espèces
            # Le règlement en espèces remplace complètement le chèque
            numero_cheque_supprime = cheque.numero
            cheque.delete()
            
            # Créer une alerte pour notifier le paiement
            Alerte.objects.create(
                echeance=None,
                type_alerte='paiement_especes_cheque',
                message=f'Chèque {numero_cheque_supprime} payé en espèces de {montant:.2f} DH par {credit.client.nom_complet}',
                date_alerte=date.today(),
                date_rappel=date_paiement,
                agent=request.user
            )
            
            # Créer un log d'action
            ActionLog.objects.create(
                type_action='cheque_paye_especes',
                description=f'Chèque {numero_cheque_supprime} de {montant:.2f} DH payé en espèces pour {credit.client.nom_complet}',
                statut='succes',
                agent=request.user,
                client=credit.client,
                credit=credit,
                donnees_apres={
                    'numero_cheque': numero_cheque_supprime,
                    'montant': str(montant),
                    'date_paiement': date_paiement.strftime('%Y-%m-%d'),
                    'mode_paiement': 'especes',
                    'commentaire': commentaire
                }
            )
            
            messages.success(request, f'Chèque {numero_cheque_supprime} supprimé et remplacé par un paiement en espèces de {montant:.2f} DH !')
            return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
            
        except (ValueError, TypeError) as e:
            messages.error(request, f'Format de données invalide : {str(e)}')
        except Exception as e:
            messages.error(request, f'Erreur lors du traitement du paiement : {str(e)}')
    
    # Si erreur ou méthode GET, rediriger vers la page du crédit
    return redirect('gestion_credits:echeance_create_for_credit', credit_id=credit.pk)
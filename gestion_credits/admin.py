from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Client, Credit, Echeance, Cheque, Alerte, ReportEcheance
from django.utils import timezone


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'cin', 'telephone', 'email', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['nom', 'prenom', 'cin', 'telephone', 'email']
    readonly_fields = ['date_creation', 'date_modification']
    ordering = ['nom', 'prenom']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'cin', 'telephone', 'email')
        }),
        ('Adresse', {
            'fields': ('adresse',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'type_credit', 'montant_total', 'agent', 'date_creation', 'statut_credit']
    list_filter = ['type_credit', 'date_creation', 'agent']
    search_fields = ['client__nom', 'client__prenom', 'description']
    readonly_fields = ['date_creation', 'date_modification']
    ordering = ['-date_creation']
    
    def statut_credit(self, obj):
        """Afficher le statut du crédit basé sur les échéances"""
        echeances = obj.echeances.all()
        if not echeances:
            return format_html('<span style="color: orange;">En attente d\'échéances</span>')
        
        total_echeances = echeances.count()
        echeances_traitees = echeances.filter(est_traitee=True).count()
        
        if echeances_traitees == 0:
            return format_html('<span style="color: red;">En cours</span>')
        elif echeances_traitees == total_echeances:
            return format_html('<span style="color: green;">Terminé</span>')
        else:
            return format_html('<span style="color: orange;">Partiellement traité ({}/{})</span>', 
                            echeances_traitees, total_echeances)
    
    statut_credit.short_description = 'Statut'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('client', 'type_credit', 'montant_total', 'description', 'agent')
        }),
        ('Type unique', {
            'fields': ('duree_jours', 'duree_semaines', 'duree_mois', 'date_echeance'),
            'classes': ('collapse',),
            'description': 'Remplir ces champs uniquement pour un crédit unique'
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):
    list_display = ['numero_partie', 'credit', 'montant', 'date_echeance', 'est_especes', 'est_traitee', 'statut_echeance']
    list_filter = ['est_especes', 'est_traitee', 'date_echeance', 'credit__type_credit']
    search_fields = ['credit__client__nom', 'credit__client__prenom']
    readonly_fields = ['date_rappel']
    ordering = ['credit', 'numero_partie']
    
    def statut_echeance(self, obj):
        """Afficher le statut de l'échéance"""
        if obj.est_traitee:
            return format_html('<span style="color: green;">Traité</span>')
        elif obj.date_echeance < timezone.now().date():
            return format_html('<span style="color: red;">En retard</span>')
        elif obj.date_echeance == timezone.now().date():
            return format_html('<span style="color: orange;">Aujourd\'hui</span>')
        else:
            return format_html('<span style="color: blue;">À venir</span>')
    
    statut_echeance.short_description = 'Statut'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('credit', 'numero_partie', 'montant', 'est_espeses')
        }),
        ('Dates', {
            'fields': ('date_echeance', 'date_rappel', 'date_traitement')
        }),
        ('Statut', {
            'fields': ('est_traitee', 'commentaire')
        }),
    )


@admin.register(Cheque)
class ChequeAdmin(admin.ModelAdmin):
    list_display = ['numero_cheque', 'echeance', 'banque', 'montant', 'date_emission', 'statut', 'statut_cheque']
    list_filter = ['statut', 'banque', 'date_emission', 'date_reglement_prevu']
    search_fields = ['numero_cheque', 'banque', 'echeance__credit__client__nom']
    ordering = ['-date_emission']
    
    def statut_cheque(self, obj):
        """Afficher le statut du chèque avec couleur"""
        if obj.statut == 'encaisse':
            return format_html('<span style="color: green;">Encaissé</span>')
        elif obj.statut == 'encaisser':
            return format_html('<span style="color: orange;">À Encaisser</span>')
        elif obj.statut == 'garantie':
            return format_html('<span style="color: blue;">Garantie</span>')
        elif obj.statut == 'reporte':
            return format_html('<span style="color: purple;">Reporté</span>')
        else:
            return format_html('<span style="color: red;">Annulé</span>')
    
    statut_cheque.short_description = 'Statut'
    
    fieldsets = (
        ('Informations du chèque', {
            'fields': ('echeance', 'numero_cheque', 'banque', 'montant', 'remarques')
        }),
        ('Dates', {
            'fields': ('date_emission', 'date_reglement_prevu', 'date_encaissement')
        }),
        ('Statut', {
            'fields': ('statut', 'date_modification')
        }),
    )


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ['type_alerte', 'echeance', 'date_alerte', 'date_rappel', 'statut', 'agent', 'statut_alerte']
    list_filter = ['type_alerte', 'statut', 'date_alerte', 'agent']
    search_fields = ['message', 'echeance__credit__client__nom']
    readonly_fields = ['date_alerte']
    ordering = ['-date_alerte']
    
    def statut_alerte(self, obj):
        """Afficher le statut de l'alerte avec couleur"""
        if obj.statut == 'traitee':
            return format_html('<span style="color: green;">Traitée</span>')
        elif obj.statut == 'reporter':
            return format_html('<span style="color: orange;">Reportée</span>')
        elif obj.date_rappel <= timezone.now().date():
            return format_html('<span style="color: red;">Urgente</span>')
        else:
            return format_html('<span style="color: blue;">En attente</span>')
    
    statut_alerte.short_description = 'Statut'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('echeance', 'type_alerte', 'message', 'agent')
        }),
        ('Dates', {
            'fields': ('date_alerte', 'date_rappel', 'date_traitement')
        }),
        ('Statut', {
            'fields': ('statut', 'commentaire_traitement', 'date_report')
        }),
    )


@admin.register(ReportEcheance)
class ReportEcheanceAdmin(admin.ModelAdmin):
    list_display = ['echeance', 'ancienne_date', 'nouvelle_date', 'raison', 'agent', 'date_report']
    list_filter = ['date_report', 'agent']
    search_fields = ['raison', 'echeance__credit__client__nom']
    readonly_fields = ['ancienne_date', 'date_report']
    ordering = ['-date_report']
    
    fieldsets = (
        ('Informations du report', {
            'fields': ('echeance', 'ancienne_date', 'nouvelle_date', 'raison', 'agent')
        }),
        ('Date du report', {
            'fields': ('date_report',),
            'classes': ('collapse',)
        }),
    )


# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration Sanlam Crédits"
admin.site.site_title = "Sanlam Crédits"
admin.site.index_title = "Gestion des crédits clients"

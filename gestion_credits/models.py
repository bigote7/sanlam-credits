from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class Client(models.Model):
    """Modèle pour gérer les clients"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=20, unique=True, verbose_name="CIN")
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.cin})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Credit(models.Model):
    """Modèle pour gérer les crédits"""
    TYPE_CHOICES = [
        ('divise', 'Crédit divisé en plusieurs parties'),
        ('unique', 'Crédit unique avec date ou durée'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='credits')
    numero_police = models.CharField(max_length=100, default='0000', unique=True, verbose_name="Numéro de police", help_text="Numéro de police unique attribué par l'agent Sanlam")
    type_credit = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    reste_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credits_geres')
    
    # Pour le type unique
    duree_jours = models.PositiveIntegerField(blank=True, null=True, 
                                            validators=[MinValueValidator(1), MaxValueValidator(3650)])
    duree_semaines = models.PositiveIntegerField(blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(520)])
    duree_mois = models.PositiveIntegerField(blank=True, null=True,
                                           validators=[MinValueValidator(1), MaxValueValidator(120)])
    date_echeance = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Crédit"
        verbose_name_plural = "Crédits"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Police {self.numero_police} - {self.client.nom_complet} ({self.montant_total} DH)"

    def save(self, *args, **kwargs):
        if self.type_credit == 'unique' and not self.date_echeance:
            # Calculer la date d'échéance basée sur la durée
            if self.duree_jours:
                self.date_echeance = timezone.now().date() + timedelta(days=self.duree_jours)
            elif self.duree_semaines:
                self.date_echeance = timezone.now().date() + timedelta(weeks=self.duree_semaines)
            elif self.duree_mois:
                # Approximation : 30 jours par mois
                self.date_echeance = timezone.now().date() + timedelta(days=self.duree_mois * 30)
        
        # Calculer le reste à payer si c'est une nouvelle instance
        if not self.pk:
            self.reste_a_payer = self.montant_total
        
        super().save(*args, **kwargs)
    
    @property
    def nombre_parties(self):
        """Nombre de parties pour un crédit divisé"""
        if self.type_credit == 'divise':
            # Par défaut, diviser en 3 parties
            return 3
        return 1
    
    @property
    def montant_partie(self):
        """Montant de chaque partie pour un crédit divisé"""
        if self.type_credit == 'divise':
            return self.montant_total / self.nombre_parties
        return self.montant_total
    
    @property
    def nombre_parties_range(self):
        """Range pour itérer sur les parties"""
        return range(1, self.nombre_parties + 1)
    
    @property
    def total_paye(self):
        """Calculer le total payé"""
        return self.montant_total - self.reste_a_payer
    
    def recalculer_reste_a_payer(self):
        """Recalculer le reste à payer basé sur les règlements"""
        total_reglements = sum(reglement.montant for reglement in self.reglements.all())
        self.reste_a_payer = max(0, self.montant_total - total_reglements)
        self.save(update_fields=['reste_a_payer'])


class Reglement(models.Model):
    """Modèle pour gérer les règlements de crédit"""
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
    ]
    
    STATUT_CHOICES = [
        ('verse', 'Versé'),
        ('non_verse', 'Non versé'),
    ]
    
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='reglements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_reglement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reglements_crees')
    
    class Meta:
        verbose_name = "Règlement"
        verbose_name_plural = "Règlements"
        ordering = ['-date_reglement']
    
    def __str__(self):
        return f"Règlement {self.montant} DH - {self.credit} ({self.get_mode_paiement_display()})"
    
    def save(self, *args, **kwargs):
        # Le statut n'est applicable que pour les chèques
        if self.mode_paiement != 'cheque':
            self.statut = None
        
        super().save(*args, **kwargs)
        
        # Recalculer le reste à payer du crédit
        self.credit.recalculer_reste_a_payer()
    
    def delete(self, *args, **kwargs):
        credit = self.credit
        super().delete(*args, **kwargs)
        # Recalculer le reste à payer après suppression
        credit.recalculer_reste_a_payer()


class ChequeGarantie(models.Model):
    """Modèle pour gérer les chèques de garantie"""
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='cheques_garantie')
    numero = models.CharField(max_length=50, verbose_name="Numéro de chèque")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    banque = models.CharField(max_length=100, verbose_name="Banque émettrice")
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chèque de garantie"
        verbose_name_plural = "Chèques de garantie"
        ordering = ['date_echeance']
    
    def __str__(self):
        return f"Chèque {self.numero} - {self.montant} DH - {self.credit}"
    
    @property
    def est_en_retard(self):
        """Vérifier si le chèque est en retard"""
        return self.date_echeance < timezone.now().date()


class Echeance(models.Model):
    """Modèle pour gérer les échéances de paiement"""
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='echeances')
    numero_partie = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_echeance = models.DateField()
    date_rappel = models.DateField()
    est_especes = models.BooleanField(default=False)
    est_traitee = models.BooleanField(default=False)
    date_traitement = models.DateTimeField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Échéance"
        verbose_name_plural = "Échéances"
        ordering = ['date_echeance']
        unique_together = ['credit', 'numero_partie']

    def __str__(self):
        return f"Échéance {self.numero_partie} - {self.credit} ({self.date_echeance})"

    def save(self, *args, **kwargs):
        if not self.date_rappel:
            # Date de rappel = date d'échéance - 3 jours
            self.date_rappel = self.date_echeance - timedelta(days=3)
        super().save(*args, **kwargs)


class Cheque(models.Model):
    """Modèle pour gérer les chèques de garantie"""
    STATUT_CHOICES = [
        ('garantie', 'Chèque de Garantie'),
        ('encaisser', 'À Encaisser'),
        ('encaisse', 'Encaissé'),
        ('reporte', 'Reporté'),
        ('annule', 'Annulé'),
    ]
    
    echeance = models.OneToOneField(Echeance, on_delete=models.CASCADE, related_name='cheque')
    numero_cheque = models.CharField(max_length=50, verbose_name="Numéro de référence")
    banque = models.CharField(max_length=100, verbose_name="Banque émettrice")
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_encaissement = models.DateField(blank=True, null=True, verbose_name="Date d'encaissement")
    date_reglement_prevu = models.DateField(verbose_name="Date prévue pour règlement", null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='garantie', verbose_name="Statut")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    remarques = models.TextField(blank=True, verbose_name="Remarques")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Chèque"
        verbose_name_plural = "Chèques"
        ordering = ['date_emission']

    def __str__(self):
        return f"Chèque {self.numero_cheque} - {self.montant} DH ({self.get_statut_display()})"
    
    @property
    def est_garantie(self):
        """Vérifie si c'est un chèque de garantie"""
        return self.statut == 'garantie'
    
    @property
    def est_a_encaisser(self):
        """Vérifie si le chèque doit être encaissé"""
        return self.statut == 'encaisser'
    
    @property
    def est_encaisse(self):
        """Vérifie si le chèque est encaissé"""
        return self.statut == 'encaisse'


class Alerte(models.Model):
    """Modèle pour gérer les alertes et rappels"""
    TYPE_CHOICES = [
        ('echeance', 'Échéance de paiement'),
        ('rappel', 'Rappel de paiement'),
        ('cheque_garantie', 'Chèque de garantie à échéance'),
        ('retard', 'Paiement en retard'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('traitee', 'Traitée'),
        ('reporter', 'Reportée'),
    ]
    
    echeance = models.ForeignKey(Echeance, on_delete=models.CASCADE, related_name='alertes', null=True, blank=True)
    type_alerte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    date_alerte = models.DateField()
    date_rappel = models.DateField()
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertes_assignees')
    date_traitement = models.DateTimeField(blank=True, null=True)
    commentaire_traitement = models.TextField(blank=True, null=True)
    date_report = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-date_alerte']

    def __str__(self):
        return f"Alerte {self.type_alerte} - {self.echeance} ({self.date_alerte})"


class ReportEcheance(models.Model):
    """Modèle pour gérer les reports d'échéances"""
    echeance = models.ForeignKey(Echeance, on_delete=models.CASCADE, related_name='reports')
    ancienne_date = models.DateField()
    nouvelle_date = models.DateField()
    raison = models.TextField()
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_crees')
    date_report = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Report d'échéance"
        verbose_name_plural = "Reports d'échéances"
        ordering = ['-date_report']

    def __str__(self):
        return f"Report {self.echeance} : {self.ancienne_date} → {self.nouvelle_date}"


class ActionLog(models.Model):
    """Modèle pour tracer l'historique des actions des agents et clients"""
    
    TYPE_ACTION_CHOICES = [
        # Actions sur les crédits
        ('credit_creation', 'Création de crédit'),
        ('credit_modification', 'Modification de crédit'),
        ('credit_suppression', 'Suppression de crédit'),
        ('credit_validation', 'Validation de crédit'),
        
        # Actions sur les échéances
        ('echeance_creation', 'Création d\'échéance'),
        ('echeance_paiement', 'Paiement d\'échéance'),
        ('echeance_report', 'Report d\'échéance'),
        ('echeance_annulation', 'Annulation d\'échéance'),
        
        # Actions sur les chèques
        ('cheque_encaissement', 'Encaissement de chèque'),
        ('cheque_report', 'Report de chèque'),
        ('cheque_annulation', 'Annulation de chèque'),
        
        # Actions sur les alertes
        ('alerte_creation', 'Création d\'alerte'),
        ('alerte_traitement', 'Traitement d\'alerte'),
        ('alerte_rappel', 'Envoi de rappel'),
        
        # Actions sur les clients
        ('client_creation', 'Création de client'),
        ('client_modification', 'Modification de client'),
        ('client_contact', 'Contact client'),
        
        # Actions système
        ('connexion', 'Connexion agent'),
        ('deconnexion', 'Déconnexion agent'),
        ('export_donnees', 'Export de données'),
        ('import_donnees', 'Import de données'),
    ]
    
    STATUT_CHOICES = [
        ('succes', 'Succès'),
        ('echec', 'Échec'),
        ('en_cours', 'En cours'),
        ('annule', 'Annulé'),
        ('en_attente', 'En attente'),
    ]
    
    # Informations de base
    type_action = models.CharField(max_length=50, choices=TYPE_ACTION_CHOICES, verbose_name="Type d'action")
    description = models.TextField(verbose_name="Description détaillée")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='succes', verbose_name="Statut")
    
    # Qui a fait l'action
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='actions_effectuees', verbose_name="Agent responsable")
    
    # Sur quoi porte l'action
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='actions_historique', verbose_name="Client concerné")
    credit = models.ForeignKey(Credit, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='actions_historique', verbose_name="Crédit concerné")
    echeance = models.ForeignKey(Echeance, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='actions_historique', verbose_name="Échéance concernée")
    
    # Données de l'action
    donnees_avant = models.JSONField(null=True, blank=True, verbose_name="Données avant modification")
    donnees_apres = models.JSONField(null=True, blank=True, verbose_name="Données après modification")
    
    # Informations de traçabilité
    date_action = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure de l'action")
    ip_adresse = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="Navigateur/Appareil")
    
    # Métadonnées
    session_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID de session")
    remarques = models.TextField(null=True, blank=True, verbose_name="Remarques additionnelles")
    
    class Meta:
        verbose_name = "Log d'action"
        verbose_name_plural = "Logs d'actions"
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['date_action']),
            models.Index(fields=['type_action']),
            models.Index(fields=['agent']),
            models.Index(fields=['client']),
            models.Index(fields=['credit']),
        ]
    
    def __str__(self):
        return f"{self.get_type_action_display()} - {self.agent.username if self.agent else 'Système'} - {self.date_action.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duree_action(self):
        """Calculer la durée de l'action si elle est en cours"""
        if self.statut == 'en_cours':
            return timezone.now() - self.date_action
        return None
    
    @property
    def est_urgent(self):
        """Déterminer si l'action nécessite une attention immédiate"""
        actions_urgentes = ['echeance_paiement', 'alerte_creation', 'credit_validation']
        return self.type_action in actions_urgentes and self.statut in ['en_cours', 'en_attente']
    
    def get_icone_action(self):
        """Retourner l'icône appropriée selon le type d'action"""
        icones = {
            'credit_creation': 'bi-plus-circle-fill',
            'credit_modification': 'bi-pencil-square',
            'credit_suppression': 'bi-trash-fill',
            'credit_validation': 'bi-check-circle-fill',
            'echeance_creation': 'bi-calendar-plus',
            'echeance_paiement': 'bi-cash-coin',
            'echeance_report': 'bi-calendar-x',
            'echeance_annulation': 'bi-x-circle-fill',
            'cheque_encaissement': 'bi-bank',
            'cheque_report': 'bi-calendar-range',
            'cheque_annulation': 'bi-x-octagon-fill',
            'alerte_creation': 'bi-exclamation-triangle-fill',
            'alerte_traitement': 'bi-check2-all',
            'alerte_rappel': 'bi-bell-fill',
            'client_creation': 'bi-person-plus-fill',
            'client_modification': 'bi-person-gear',
            'client_contact': 'bi-telephone-fill',
            'connexion': 'bi-box-arrow-in-right',
            'deconnexion': 'bi-box-arrow-left',
            'export_donnees': 'bi-download',
            'import_donnees': 'bi-upload',
        }
        return icones.get(self.type_action, 'bi-info-circle')
    
    def get_couleur_statut(self):
        """Retourner la couleur Bootstrap appropriée pour le statut"""
        couleurs = {
            'succes': 'success',
            'echec': 'danger',
            'en_cours': 'warning',
            'annule': 'secondary',
            'en_attente': 'info',
        }
        return couleurs.get(self.statut, 'primary')
    
    def get_resume_action(self):
        """Retourner un résumé concis de l'action"""
        if self.client:
            return f"{self.get_type_action_display()} pour {self.client.nom_complet}"
        elif self.credit:
            return f"{self.get_type_action_display()} - Police {self.credit.numero_police}"
        else:
            return self.get_type_action_display()

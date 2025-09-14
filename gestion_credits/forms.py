from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Credit, Echeance, Cheque, Alerte, ReportEcheance, Reglement, ChequeGarantie
from datetime import date, timedelta


class ClientForm(forms.ModelForm):
    """Formulaire pour créer/modifier un client"""
    
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'cin', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom du client'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CIN'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse'}),
        }

    def clean_cin(self):
        cin = self.cleaned_data['cin']
        if Client.objects.filter(cin=cin).exists() and self.instance.pk is None:
            raise forms.ValidationError("Un client avec ce CIN existe déjà.")
        return cin

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        if Client.objects.filter(telephone=telephone).exists() and self.instance.pk is None:
            raise forms.ValidationError("Un client avec ce téléphone existe déjà.")
        return telephone


class CreditForm(forms.ModelForm):
    """Formulaire de base pour créer/modifier un crédit"""
    
    class Meta:
        model = Credit
        fields = ['client', 'numero_police', 'montant_total', 'description']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'numero_police': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: POL-2024-001',
                'title': 'Numéro de police unique attribué par l\'agent Sanlam'
            }),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du crédit'}),
        }
    
    def clean_numero_police(self):
        numero_police = self.cleaned_data['numero_police']
        if not numero_police:
            raise forms.ValidationError("Le numéro de police est obligatoire.")
        
        # Vérifier l'unicité du numéro de police
        if Credit.objects.filter(numero_police=numero_police).exists() and self.instance.pk is None:
            raise forms.ValidationError("Ce numéro de police existe déjà.")
        
        # Validation du format (optionnel mais recommandé)
        if len(numero_police.strip()) < 3:
            raise forms.ValidationError("Le numéro de police doit contenir au moins 3 caractères.")
        
        return numero_police.strip()


class CreditUniqueForm(CreditForm):
    """Formulaire pour créer un crédit unique avec date ou durée"""
    
    TYPE_DUREE_CHOICES = [
        ('duree', 'Durée'),
        ('date_exacte', 'Date exacte'),
    ]
    
    type_duree = forms.ChoiceField(
        choices=TYPE_DUREE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type de durée"
    )
    
    duree_valeur = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Valeur de la durée"
    )
    
    type_unite = forms.ChoiceField(
        choices=[
            ('jours', 'Jours'),
            ('semaines', 'Semaines'),
            ('mois', 'Mois'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Unité de durée"
    )
    
    date_echeance = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'échéance exacte"
    )
    
    # Nouveaux champs pour le chèque de garantie
    has_cheque_garantie = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Le client fournit un chèque de garantie"
    )
    
    numero_cheque_garantie = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de référence du chèque'}),
        label="Numéro de référence du chèque"
    )
    
    banque_garantie = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: BMCE, Attijariwafa Bank...'}),
        label="Banque émettrice"
    )
    
    date_emission_garantie = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'émission du chèque"
    )
    
    date_reglement_prevu_garantie = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement"
    )
    
    remarques_garantie = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Remarques sur le chèque de garantie...'}),
        label="Remarques (optionnel)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        type_duree = cleaned_data.get('type_duree')
        has_cheque = cleaned_data.get('has_cheque_garantie')
        
        if type_duree == 'duree':
            if not cleaned_data.get('duree_valeur') or not cleaned_data.get('type_unite'):
                raise forms.ValidationError("Pour une durée, veuillez spécifier la valeur et l'unité.")
        elif type_duree == 'date_exacte':
            if not cleaned_data.get('date_echeance'):
                raise forms.ValidationError("Pour une date exacte, veuillez spécifier la date d'échéance.")
        
        # Validation des champs de chèque de garantie
        if has_cheque:
            if not cleaned_data.get('numero_cheque_garantie'):
                raise forms.ValidationError("Si un chèque de garantie est fourni, le numéro de référence est obligatoire.")
            if not cleaned_data.get('banque_garantie'):
                raise forms.ValidationError("Si un chèque de garantie est fourni, la banque émettrice est obligatoire.")
            if not cleaned_data.get('date_emission_garantie'):
                raise forms.ValidationError("Si un chèque de garantie est fourni, la date d'émission est obligatoire.")
            if not cleaned_data.get('date_reglement_prevu_garantie'):
                raise forms.ValidationError("Si un chèque de garantie est fourni, la date prévue de règlement est obligatoire.")
        
        return cleaned_data
    
    def save(self, commit=True):
        credit = super().save(commit=False)
        credit.type_credit = 'unique'
        
        if self.cleaned_data['type_duree'] == 'duree':
            duree_valeur = self.cleaned_data['duree_valeur']
            type_unite = self.cleaned_data['type_unite']
            
            if type_unite == 'jours':
                credit.duree_jours = duree_valeur
            elif type_unite == 'semaines':
                credit.duree_semaines = duree_valeur
            elif type_unite == 'mois':
                credit.duree_mois = duree_valeur
        else:
            credit.date_echeance = self.cleaned_data['date_echeance']
        
        if commit:
            credit.save()
        return credit


class CreditDiviseForm(CreditForm):
    """Formulaire pour créer un crédit divisé"""
    
    nombre_parties = forms.IntegerField(
        min_value=2,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '2', 'max': '5'}),
        label="Nombre de parties",
        help_text="Entre 2 et 5 parties (la première sera en espèces)"
    )


class CreditDiviseCompletForm(CreditForm):
    """Formulaire pour créer un crédit divisé avec montant espèces et chèques de garantie"""
    
    # Montant payé en espèces en premier
    montant_especes = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant payé en espèces (DH) *",
        help_text="Montant que le client paie immédiatement en espèces"
    )
    
    # Choix du type de garantie
    TYPE_GARANTIE_CHOICES = [
        ('unique', 'Un seul chèque de garantie'),
        ('multiple', 'Plusieurs chèques de garantie'),
    ]
    
    type_garantie = forms.ChoiceField(
        choices=TYPE_GARANTIE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Type de garantie",
        initial='unique'
    )
    
    # Nombre de chèques de garantie (visible seulement si multiple)
    nombre_cheques = forms.IntegerField(
        min_value=2,
        max_value=10,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '2', 'max': '10'}),
        label="Nombre de chèques de garantie",
        help_text="Entre 2 et 10 chèques"
    )
    
    # Champs pour le chèque unique
    numero_cheque_unique = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence du chèque"
    )
    
    banque_unique = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice"
    )
    
    date_emission_unique = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'émission"
    )
    
    montant_garantie_unique = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant de la garantie (DH)"
    )
    
    date_reglement_prevu_unique = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement"
    )
    
    commentaire_unique = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Commentaire (optionnel)"
    )
    

    
    def clean(self):
        """Validation personnalisée du formulaire"""
        cleaned_data = super().clean()
        montant_total = cleaned_data.get('montant_total')
        montant_especes = cleaned_data.get('montant_especes')
        type_garantie = cleaned_data.get('type_garantie')
        nombre_cheques = cleaned_data.get('nombre_cheques')
        
        # Validation du montant total
        if montant_total and montant_total <= 0:
            self.add_error('montant_total', 'Le montant total doit être supérieur à 0.')
        
        # Validation du montant en espèces
        if montant_especes and montant_total:
            if montant_especes >= montant_total:
                self.add_error('montant_especes', 'Le montant en espèces doit être inférieur au montant total du crédit.')
            if montant_especes <= 0:
                self.add_error('montant_especes', 'Le montant en espèces doit être supérieur à 0.')
        
        # Validation selon le type de garantie
        if type_garantie == 'unique':
            # Validation des champs obligatoires pour le chèque unique
            champs_obligatoires = ['numero_cheque_unique', 'banque_unique', 'date_emission_unique', 'montant_garantie_unique', 'date_reglement_prevu_unique']
            for champ in champs_obligatoires:
                if not cleaned_data.get(champ):
                    self.add_error(champ, f'Ce champ est obligatoire pour un chèque de garantie unique.')
            
            # Validation du montant de garantie
            montant_garantie = cleaned_data.get('montant_garantie_unique')
            if montant_garantie and montant_total and montant_especes:
                montant_reste = montant_total - montant_especes
                if montant_garantie > montant_reste:
                    self.add_error('montant_garantie_unique', f'Le montant de la garantie ne peut pas dépasser le reste à payer ({montant_reste} DH).')
        
        elif type_garantie == 'multiple':
            # Validation du nombre de chèques
            if not nombre_cheques:
                self.add_error('nombre_cheques', 'Le nombre de chèques est obligatoire pour plusieurs chèques de garantie.')
            elif nombre_cheques < 2 or nombre_cheques > 10:
                self.add_error('nombre_cheques', 'Le nombre de chèques doit être entre 2 et 10.')
        
        return cleaned_data
    
    # Champs pour les chèques multiples (parties 2 à 5)
    numero_cheque_2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence chèque partie 2"
    )
    
    banque_2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice partie 2"
    )
    
    date_reglement_prevu_2 = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement partie 2"
    )
    
    montant_partie_2 = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant partie 2 (DH)"
    )
    
    besoins_cheque_2 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Besoins/Remarques partie 2"
    )
    
    numero_cheque_3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence chèque partie 3"
    )
    
    banque_3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice partie 3"
    )
    
    date_reglement_prevu_3 = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement partie 3"
    )
    
    montant_partie_3 = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant partie 3 (DH)"
    )
    
    besoins_cheque_3 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Besoins/Remarques partie 3"
    )
    
    numero_cheque_4 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence chèque partie 4"
    )
    
    banque_4 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice partie 4"
    )
    
    date_reglement_prevu_4 = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement partie 4"
    )
    
    montant_partie_4 = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant partie 4 (DH)"
    )
    
    besoins_cheque_4 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Besoins/Remarques partie 4"
    )
    
    numero_cheque_5 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence chèque partie 5"
    )
    
    banque_5 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice partie 5"
    )
    
    date_reglement_prevu_5 = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue de règlement partie 5"
    )
    
    montant_partie_5 = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant partie 5 (DH)"
    )
    
    besoins_cheque_5 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Besoins/Remarques partie 5"
    )











class EcheanceForm(forms.ModelForm):
    """Formulaire pour créer/modifier une échéance"""
    
    class Meta:
        model = Echeance
        fields = ['numero_partie', 'montant', 'date_echeance', 'est_especes', 'commentaire']
        widgets = {
            'numero_partie': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'est_especes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.credit = kwargs.pop('credit', None)
        super().__init__(*args, **kwargs)
        if self.credit:
            # Limiter le numéro de partie selon le type de crédit
            if self.credit.type_credit == 'divise':
                max_parties = 5
            else:
                max_parties = 1
            self.fields['numero_partie'].widget.attrs['max'] = max_parties


class ChequeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un chèque"""
    
    class Meta:
        model = Cheque
        fields = ['numero_cheque', 'banque', 'date_emission', 'date_reglement_prevu', 'statut', 'montant', 'remarques']
        widgets = {
            'numero_cheque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de référence du chèque'}),
            'banque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Banque émettrice'}),
            'date_emission': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_reglement_prevu': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Remarques optionnelles'}),
        }
    
    def clean_date_reglement_prevu(self):
        date_reglement = self.cleaned_data['date_reglement_prevu']
        if date_reglement <= date.today():
            raise forms.ValidationError("La date de règlement prévue doit être dans le futur.")
        return date_reglement





class EcheanceAvecChequeForm(forms.Form):
    """Formulaire pour une échéance avec ou sans chèque de garantie"""
    
    numero_partie = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Numéro de partie"
    )
    
    montant = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant (DH)"
    )
    
    date_echeance = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'échéance"
    )
    
    est_especes = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Paiement en espèces"
    )
    
    # Champs pour le chèque de garantie (si applicable)
    numero_cheque = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro de référence du chèque"
    )
    
    banque = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Banque émettrice"
    )
    
    date_reglement_prevu = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date prévue pour règlement"
    )
    
    remarques = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Remarques (optionnel)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        est_especes = cleaned_data.get('est_especes')
        
        if not est_especes:
            # Si ce n'est pas en espèces, les champs du chèque sont obligatoires
            champs_obligatoires = ['numero_cheque', 'banque', 'date_reglement_prevu']
            for champ in champs_obligatoires:
                if not cleaned_data.get(champ):
                    self.add_error(champ, f"Ce champ est obligatoire pour un chèque de garantie.")
        
        return cleaned_data


class AlerteForm(forms.ModelForm):
    """Formulaire pour traiter une alerte"""
    
    class Meta:
        model = Alerte
        fields = ['statut', 'commentaire_traitement', 'date_report']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'commentaire_traitement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_report': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer le champ date_report si le statut n'est pas 'reporter'
        if 'instance' in kwargs and kwargs['instance']:
            if kwargs['instance'].statut != 'reporter':
                self.fields['date_report'].widget = forms.HiddenInput()


class ReportEcheanceForm(forms.ModelForm):
    """Formulaire pour reporter une échéance"""
    
    class Meta:
        model = ReportEcheance
        fields = ['nouvelle_date', 'raison']
        widgets = {
            'nouvelle_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'raison': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Raison du report'}),
        }

    def clean_nouvelle_date(self):
        nouvelle_date = self.cleaned_data['nouvelle_date']
        if nouvelle_date <= date.today():
            raise forms.ValidationError("La nouvelle date doit être dans le futur.")
        return nouvelle_date


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription des utilisateurs"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field, 'widget'):
                field.widget.attrs.update({'class': 'form-control'})


class ReglementForm(forms.ModelForm):
    """Formulaire pour ajouter un règlement"""
    
    class Meta:
        model = Reglement
        fields = ['montant', 'date_reglement', 'mode_paiement', 'statut', 'commentaire']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant en DH'
            }),
            'date_reglement': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'mode_paiement': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Commentaire optionnel'
            })
        }
    
    def __init__(self, *args, **kwargs):
        credit = kwargs.pop('credit', None)
        super().__init__(*args, **kwargs)
        
        if credit:
            # Limiter le montant maximum au reste à payer
            self.fields['montant'].widget.attrs['max'] = str(credit.reste_a_payer)
            self.fields['montant'].help_text = f"Montant maximum autorisé : {credit.reste_a_payer} DH"
        
        # Rendre le champ statut conditionnel
        self.fields['statut'].required = False
        self.fields['statut'].widget.attrs['style'] = 'display: none;'
    
    def clean(self):
        cleaned_data = super().clean()
        montant = cleaned_data.get('montant')
        mode_paiement = cleaned_data.get('mode_paiement')
        statut = cleaned_data.get('statut')
        
        # Validation du montant
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        
        # Validation du statut pour les chèques
        if mode_paiement == 'cheque' and not statut:
            raise forms.ValidationError("Le statut est obligatoire pour les règlements par chèque.")
        
        # Le statut ne doit être défini que pour les chèques
        if mode_paiement != 'cheque' and statut:
            cleaned_data['statut'] = None
        
        return cleaned_data


class ChequeGarantieForm(forms.ModelForm):
    """Formulaire pour ajouter un chèque de garantie"""
    
    class Meta:
        model = ChequeGarantie
        fields = ['numero', 'montant', 'banque', 'date_emission', 'date_echeance', 'commentaire']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro du chèque'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant en DH'
            }),
            'banque': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la banque'
            }),
            'date_emission': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_echeance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Commentaire optionnel'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_emission = cleaned_data.get('date_emission')
        date_echeance = cleaned_data.get('date_echeance')
        montant = cleaned_data.get('montant')
        
        # Validation des dates
        if date_emission and date_echeance and date_emission > date_echeance:
            raise forms.ValidationError("La date d'émission ne peut pas être postérieure à la date d'échéance.")
        
        # Validation du montant
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        
        return cleaned_data


class PaiementEcheanceForm(forms.Form):
    """Formulaire professionnel pour le paiement des échéances"""
    
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Paiement en Espèces'),
        ('effets', 'Paiement par Effets (Chèques/Virements)'),
    ]
    
    TYPE_ECHEANCE_CHOICES = [
        ('unique', 'Une seule échéance'),
        ('multiple', 'Plusieurs échéances échelonnées'),
    ]
    
    # Informations de base
    mode_paiement = forms.ChoiceField(
        choices=MODE_PAIEMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Mode de Paiement",
        initial='especes'
    )
    
    type_echeance = forms.ChoiceField(
        choices=TYPE_ECHEANCE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Type d'Échéance",
        initial='unique'
    )
    
    # Montant et date
    montant_total = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'readonly': 'readonly'
        }),
        label="Montant Total à Payer (DH)",
        help_text="Montant restant du crédit"
    )
    
    # Pour échéance unique
    montant_echeance_unique = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        label="Montant de l'Échéance (DH)"
    )
    
    date_echeance_unique = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date d'Échéance"
    )
    
    # Pour échéances multiples
    nombre_echeances = forms.IntegerField(
        min_value=2,
        max_value=12,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '2',
            'max': '12'
        }),
        label="Nombre d'Échéances",
        help_text="Entre 2 et 12 échéances"
    )
    
    frequence_paiement = forms.ChoiceField(
        choices=[
            ('hebdomadaire', 'Hebdomadaire'),
            ('bimensuelle', 'Bimensuelle'),
            ('mensuelle', 'Mensuelle'),
            ('trimestrielle', 'Trimestrielle'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Fréquence de Paiement"
    )
    
    date_premiere_echeance = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de la Première Échéance"
    )
    
    # Informations pour les effets (chèques/virements)
    numero_effet = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro de chèque ou référence virement'
        }),
        label="Numéro/Référence de l'Effet"
    )
    
    banque_emetteur = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de la banque'
        }),
        label="Banque Émettrice"
    )
    
    date_emission_effet = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date d'Émission de l'Effet"
    )
    
    commentaire = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Commentaires sur le paiement...'
        }),
        label="Commentaire"
    )
    
    def __init__(self, *args, **kwargs):
        credit = kwargs.pop('credit', None)
        super().__init__(*args, **kwargs)
        
        if credit:
            # Pré-remplir le montant total avec le reste à payer
            self.fields['montant_total'].initial = credit.reste_a_payer
            self.fields['montant_echeance_unique'].initial = credit.reste_a_payer
            
            # Pré-remplir la date de première échéance avec aujourd'hui
            from datetime import date
            self.fields['date_premiere_echeance'].initial = date.today()
            self.fields['date_echeance_unique'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        mode_paiement = cleaned_data.get('mode_paiement')
        type_echeance = cleaned_data.get('type_echeance')
        montant_total = cleaned_data.get('montant_total')
        
        # Validation pour échéance unique
        if type_echeance == 'unique':
            montant_echeance = cleaned_data.get('montant_echeance_unique')
            date_echeance = cleaned_data.get('date_echeance_unique')
            
            if not montant_echeance:
                self.add_error('montant_echeance_unique', 'Le montant de l\'échéance est obligatoire.')
            elif montant_echeance <= 0:
                self.add_error('montant_echeance_unique', 'Le montant doit être supérieur à 0.')
            elif montant_echeance > montant_total:
                self.add_error('montant_echeance_unique', f'Le montant ne peut pas dépasser {montant_total} DH.')
            
            if not date_echeance:
                self.add_error('date_echeance_unique', 'La date d\'échéance est obligatoire.')
        
        # Validation pour échéances multiples
        elif type_echeance == 'multiple':
            nombre_echeances = cleaned_data.get('nombre_echeances')
            frequence = cleaned_data.get('frequence_paiement')
            date_premiere = cleaned_data.get('date_premiere_echeance')
            
            if not nombre_echeances:
                self.add_error('nombre_echeances', 'Le nombre d\'échéances est obligatoire.')
            if not frequence:
                self.add_error('frequence_paiement', 'La fréquence de paiement est obligatoire.')
            if not date_premiere:
                self.add_error('date_premiere_echeance', 'La date de première échéance est obligatoire.')
        
        # Validation pour les effets
        if mode_paiement == 'effets':
            numero_effet = cleaned_data.get('numero_effet')
            banque = cleaned_data.get('banque_emetteur')
            date_emission = cleaned_data.get('date_emission_effet')
            
            if not numero_effet:
                self.add_error('numero_effet', 'Le numéro/référence de l\'effet est obligatoire.')
            if not banque:
                self.add_error('banque_emetteur', 'La banque émettrice est obligatoire.')
            if not date_emission:
                self.add_error('date_emission_effet', 'La date d\'émission de l\'effet est obligatoire.')
        
        return cleaned_data


class AjoutPaiementForm(forms.Form):
    """Formulaire simplifié pour ajouter un paiement"""
    
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Paiement en Espèces'),
        ('effets', 'Paiement par Effets (Chèques/Virements)'),
    ]
    
    # Mode de paiement
    mode_paiement = forms.ChoiceField(
        choices=MODE_PAIEMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Mode de Paiement",
        initial='especes'
    )
    
    # Montant du paiement
    montant = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Montant en DH'
        }),
        label="Montant du Paiement (DH)",
        help_text="Montant maximum autorisé: {{ reste_a_payer }} DH"
    )
    
    # Date du paiement
    date_paiement = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date du Paiement",
        initial=date.today
    )
    
    # Informations pour les effets (chèques/virements)
    numero_effet = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro de chèque ou référence virement'
        }),
        label="Numéro/Référence de l'Effet"
    )
    
    banque_emetteur = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de la banque'
        }),
        label="Banque Émettrice"
    )
    
    date_emission_effet = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date d'Émission de l'Effet"
    )
    
    # Commentaire
    commentaire = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Commentaires sur le paiement...'
        }),
        label="Commentaire"
    )
    
    def __init__(self, *args, **kwargs):
        credit = kwargs.pop('credit', None)
        super().__init__(*args, **kwargs)
        
        if credit:
            # Pré-remplir la date d'émission avec aujourd'hui
            from datetime import date
            self.fields['date_emission_effet'].initial = date.today()
            
            # Mettre à jour l'aide du montant
            self.fields['montant'].help_text = f"Montant maximum autorisé: {credit.reste_a_payer} DH"
    
    def clean(self):
        cleaned_data = super().clean()
        mode_paiement = cleaned_data.get('mode_paiement')
        
        # Validation pour les effets
        if mode_paiement == 'effets':
            numero_effet = cleaned_data.get('numero_effet')
            banque = cleaned_data.get('banque_emetteur')
            date_emission = cleaned_data.get('date_emission_effet')
            
            if not numero_effet:
                self.add_error('numero_effet', 'Le numéro/référence de l\'effet est obligatoire.')
            if not banque:
                self.add_error('banque_emetteur', 'La banque émettrice est obligatoire.')
            if not date_emission:
                self.add_error('date_emission_effet', 'La date d\'émission de l\'effet est obligatoire.')
        
        return cleaned_data

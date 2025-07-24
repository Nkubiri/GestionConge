from django import forms
from django.contrib.auth.forms import UserCreationForm # Importe UserCreationForm
from .models import Leave

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave # Ce formulaire est basé sur le modèle Leave
        fields = ['start_date', 'end_date', 'leave_type', 'reason'] # Champs que l'utilisateur peut remplir
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'leave_type': forms.Select(attrs={'class': 'form-input'}),
            'reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }
        labels = {
            'start_date': "Date de Début",
            'end_date': "Date de Fin",
            'leave_type': "Type de Congé",
            'reason': "Raison (optionnel)",
        }

    # Vous pouvez ajouter des validations personnalisées ici
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
        return cleaned_data

# Nouveau formulaire pour l'inscription avec prénom et nom
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label="Prénom",
                                 widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=100, required=True, label="Nom",
                                widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(required=True, label="Email",
                             widget=forms.EmailInput(attrs={'class': 'form-input'}))


    class Meta(UserCreationForm.Meta):
        # Utilise le modèle User de Django, mais ajoute nos champs personnalisés
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)
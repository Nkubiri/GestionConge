from django.db import models
from django.contrib.auth.models import User # Importe le modèle User par défaut de Django

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="ID Employé")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de Téléphone")
    date_of_hire = models.DateField(verbose_name="Date d'Embauche")
    position = models.CharField(max_length=100, verbose_name="Poste")
    department = models.CharField(max_length=100, verbose_name="Département")
    leave_balance = models.IntegerField(default=20, verbose_name="Solde de Congés")
    # Nouveau champ pour identifier si l'employé est un responsable
    is_manager = models.BooleanField(default=False, verbose_name="Est Responsable") # <-- Nouveau champ

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['last_name', 'first_name']


# Modèle pour représenter une Demande de Congé
class Leave(models.Model):
    # Types de congés possibles
    LEAVE_TYPES = (
        ('VACATION', 'Congé Payé / Vacances'),
        ('SICK', 'Congé Maladie'),
        ('PERSONAL', 'Congé Personnel'),
        ('FAMILY', 'Congé Familial'),
        ('UNPAID', 'Congé Sans Solde'),
    )

    # Statuts possibles d'une demande de congé
    LEAVE_STATUSES = (
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('CANCELLED', 'Annulé'),
    )

    # Liaison avec l'employé qui demande le congé
    # on_delete=models.CASCADE signifie que si l'employé est supprimé, ses congés le sont aussi.
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves', verbose_name="Employé")

    # Détails du congé
    start_date = models.DateField(verbose_name="Date de Début")
    end_date = models.DateField(verbose_name="Date de Fin")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='VACATION', verbose_name="Type de Congé")
    reason = models.TextField(blank=True, null=True, verbose_name="Raison")
    status = models.CharField(max_length=20, choices=LEAVE_STATUSES, default='PENDING', verbose_name="Statut")
    # Date à laquelle la demande a été soumise
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Demandé le")
    # Date à laquelle la demande a été approuvée/rejetée
    approved_rejected_at = models.DateTimeField(blank=True, null=True, verbose_name="Approuvé/Rejeté le")
    # Personne qui a approuvé/rejeté le congé (peut être un autre utilisateur Django)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name="Approuvé par")
    # Commentaires du responsable
    manager_comments = models.TextField(blank=True, null=True, verbose_name="Commentaires du Responsable")

    # Méthode pour calculer la durée du congé en jours
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    # Méthode pour afficher une représentation lisible de l'objet Leave
    def __str__(self):
        return f"Congé de {self.employee.first_name} {self.employee.last_name} du {self.start_date} au {self.end_date} ({self.status})"

    class Meta:
        verbose_name = "Demande de Congé"
        verbose_name_plural = "Demandes de Congé"
        ordering = ['-requested_at'] # Tri par défaut (les plus récents en premier)
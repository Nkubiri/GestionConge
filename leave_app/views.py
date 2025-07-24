from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Employee, Leave
from .forms import LeaveRequestForm, CustomUserCreationForm
from django.utils import timezone

# Fonction utilitaire pour vérifier si l'utilisateur est un responsable
def is_manager_check(user):
    try:
        return user.is_authenticated and user.employee.is_manager
    except Employee.DoesNotExist:
        return False

# Vue pour la page d'accueil
def home_view(request):
    return render(request, 'home.html')

# Vue pour l'inscription d'un nouvel utilisateur/employé
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # <-- Utilise CustomUserCreationForm
        if form.is_valid():
            user = form.save() # Sauvegarde l'utilisateur (username, password)
            # Sauvegarde l'email sur l'objet User si ce n'est pas déjà fait
            user.email = form.cleaned_data.get('email')
            user.save()

            # Créer un profil Employee pour le nouvel utilisateur
            Employee.objects.create(
                user=user,
                first_name=form.cleaned_data.get('first_name'), # <-- Utilise le prénom du formulaire
                last_name=form.cleaned_data.get('last_name'),   # <-- Utilise le nom du formulaire
                employee_id=f'EMP-{user.id}',
                email=form.cleaned_data.get('email'), # <-- Utilise l'email du formulaire
                date_of_hire=timezone.now().date(), # Date d'embauche par défaut à aujourd'hui
                position='Personnel',
                department='Général'
            )
            login(request, user)
            messages.success(request, "Votre compte a été créé et vous êtes connecté(e) !")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur sur le champ '{field}': {error}")
    else:
        form = CustomUserCreationForm() # <-- Utilise CustomUserCreationForm
    return render(request, 'registration/register.html', {'form': form})

# Vue pour la connexion
def login_view(request): # <-- Assurez-vous que cette fonction est bien présente
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Vous êtes maintenant connecté(e) !")
            return redirect('home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Vue pour la déconnexion
@login_required
def logout_view(request): # <-- Assurez-vous que cette fonction est bien présente
    logout(request)
    messages.info(request, "Vous avez été déconnecté(e).")
    return redirect('home')

# Vue pour demander un congé
@login_required
def request_leave_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Votre profil employé n'a pas été trouvé. Veuillez contacter l'administrateur.")
        return redirect('home')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'PENDING'
            leave.save()
            messages.success(request, "Votre demande de congé a été soumise avec succès et est en attente d'approbation.")
            return redirect('my_leaves')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LeaveRequestForm()

    context = {
        'form': form,
        'employee_leave_balance': employee.leave_balance
    }
    return render(request, 'leave_app/request_leave.html', context)

# Vue pour afficher les congés de l'utilisateur connecté
@login_required
def my_leaves_view(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Votre profil employé n'a pas été trouvé. Veuillez contacter l'administrateur.")
        return redirect('home')

    my_leaves = Leave.objects.filter(employee=employee).order_by('-requested_at')

    context = {
        'my_leaves': my_leaves,
        'employee_leave_balance': employee.leave_balance
    }
    return render(request, 'leave_app/my_leaves.html', context)

# Vue pour lister les congés à approuver (pour les responsables)
@login_required
@user_passes_test(is_manager_check, login_url='home')
def leaves_to_approve_view(request):
    pending_leaves = Leave.objects.filter(status='PENDING').order_by('requested_at')

    context = {
        'pending_leaves': pending_leaves
    }
    return render(request, 'leave_app/leaves_to_approve.html', context)

# Vue pour approuver ou rejeter un congé spécifique
@login_required
@user_passes_test(is_manager_check, login_url='home')
def manage_leave_view(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        manager_comments = request.POST.get('manager_comments', '')

        if action == 'approve':
            leave.status = 'APPROVED'
            leave.approved_by = request.user
            leave.approved_rejected_at = timezone.now()
            leave.manager_comments = manager_comments
            leave.save()

            if leave.leave_type in ['VACATION', 'PERSONAL', 'FAMILY']:
                employee = leave.employee
                if employee.leave_balance >= leave.duration_days:
                    employee.leave_balance -= leave.duration_days
                    employee.save()
                    messages.success(request, f"Le congé de {leave.employee.first_name} {leave.employee.last_name} a été approuvé et {leave.duration_days} jours ont été déduits de son solde.")
                else:
                    messages.warning(request, f"Le congé a été approuvé, mais le solde de {leave.employee.first_name} {leave.employee.last_name} est insuffisant ({employee.leave_balance} jours restants).")
            else:
                messages.success(request, f"Le congé de {leave.employee.first_name} {leave.employee.last_name} a été approuvé.")

        elif action == 'reject':
            leave.status = 'REJECTED'
            leave.approved_by = request.user
            leave.approved_rejected_at = timezone.now()
            leave.manager_comments = manager_comments
            leave.save()
            messages.info(request, f"Le congé de {leave.employee.first_name} {leave.employee.last_name} a été rejeté.")
        else:
            messages.error(request, "Action non valide.")

        return redirect('leaves_to_approve')

    context = {
        'leave': leave
    }
    return render(request, 'leave_app/manage_leave.html', context)

# Nouvelle vue pour afficher tous les congés des employés (pour les responsables)
@login_required
@user_passes_test(is_manager_check, login_url='home') # Seuls les responsables peuvent accéder à cette vue
def all_employees_leaves_view(request):
    # Récupère toutes les demandes de congé, triées par date de demande la plus récente
    all_leaves = Leave.objects.all().order_by('-requested_at')

    context = {
        'all_leaves': all_leaves
    }
    return render(request, 'leave_app/all_employees_leaves.html', context)

# Nouvelle vue pour modifier un congé (pour les responsables)
@login_required
@user_passes_test(is_manager_check, login_url='home')
def edit_leave_view(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave) # Pré-remplit le formulaire avec l'instance existante
        if form.is_valid():
            form.save() # Sauvegarde les modifications
            messages.success(request, "Le congé a été modifié avec succès.")
            return redirect('all_employees_leaves') # Redirige vers la liste de tous les congés
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LeaveRequestForm(instance=leave) # Affiche le formulaire pré-rempli

    context = {
        'form': form,
        'leave': leave, # Passe l'objet congé au template pour afficher les détails
    }
    return render(request, 'leave_app/edit_leave.html', context)

# Nouvelle vue pour supprimer un congé (pour les responsables)
@login_required
@user_passes_test(is_manager_check, login_url='home')
def delete_leave_view(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    if request.method == 'POST':
        # Vérifiez que le congé n'est pas déjà approuvé ou rejetté si vous voulez éviter la suppression
        # if leave.status == 'APPROVED' or leave.status == 'REJECTED':
        #     messages.error(request, "Impossible de supprimer un congé déjà traité.")
        #     return redirect('all_employees_leaves')

        leave.delete()
        messages.success(request, "Le congé a été supprimé avec succès.")
        return redirect('all_employees_leaves')

    context = {
        'leave': leave
    }
    # Pour une confirmation simple, on peut afficher une page de confirmation
    return render(request, 'leave_app/confirm_delete_leave.html', context)
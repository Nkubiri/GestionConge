"""
URL configuration for ElieSchoolProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include # Importe include pour inclure les URLs de l'application
from django.conf import settings # Pour accéder aux paramètres de settings
from django.conf.urls.static import static # Pour servir les fichiers statiques en mode développement

urlpatterns = [
    path('admin/', admin.site.urls), # L'URL d'administration de Django
    path('', include('leave_app.urls')), # Inclut les URLs de notre application leave_app
]

# Servir les fichiers statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
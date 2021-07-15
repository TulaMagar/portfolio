"""portfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from personalportfolio import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

APP_NAME = 'portfolio'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/login/', LoginView.as_view(), name='login'),
    path('registration/register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('movie', views.movies, name='movie'),
    path('store', views.store, name='store'),
    path('logout', views.logout_request, name='logout'),
    path('PhysicalActivity', views.PhysicalActivity, name='PhysicalActivity'),
    path("upload", views.upload, name="upload"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

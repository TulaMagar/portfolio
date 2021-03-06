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
    path("project", views.project, name="project"),
    path("question", views.question, name="question"),
    path("programming", views.programming, name="programming"),
    path("python/python/", views.python, name="python"),
    path("python/syntax/", views.pythonsyntax, name="pythonsyntax"),
    path("python/comment/", views.pythoncomment, name="pythoncomment"),
    path("python/variable/", views.pythonvariable, name="pythonvariable"),
    path('physicalactivity/walk/', views.walk, name='walk'),
    path('physicalactivity/run/', views.run, name='run'),
    path('physicalactivity/jogging/', views.jogging, name='jogging'),
    path('physicalactivity/gym/app/', views.app, name='app'),
    path("physicalactivity/gym/chess/", views.chess, name="chess"),
    path("physicalactivity/gym/leg/", views.leg, name="leg"),
    path("physicalactivity/gym/muscle/", views.muscle, name="muscle"),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

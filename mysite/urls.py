"""
URL configuration for mysite project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path("cities/", include("apps.cities.urls")),
    path("places/", include("apps.places.urls")),
    path("hobbies/", include("apps.hobbies.urls")),
    path("evaluation/", include("apps.evaluation.urls")),
    # Branded sign-in / sign-up / sign-out (the canonical account routes).
    path("accounts/", include("apps.users.auth_urls")),
    path("", views.home, name="home"),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    # Legacy aliases for links published before the redesign.
    path('users/', include('apps.users.urls')),
    path('info/', include('apps.info.urls')),
]

handler404 = "mysite.views.error_404"
handler500 = "mysite.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


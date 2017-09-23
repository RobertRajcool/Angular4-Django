"""redington_uber URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from cloudapp.urls import cloudapp_router
from django.conf.urls.static import static
from django.conf import settings
from users.views import api_password_reset, api_password_reset_verify, api_password_reset_confirm
from cloudapp.generics.constant import AppContants
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-password-reset/', api_password_reset),
    url(r'^api-password-reset-verify/', api_password_reset_verify),
    url(r'^api-password-reset-confirm/', api_password_reset_confirm),
    url(r'^', include(cloudapp_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
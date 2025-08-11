"""
URL configuration for qms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views import RegisterView, OrganisationDetailView, CustomLoginView
from system.views import HomeView, RegisterCompany, PackageView, PaymentView, PaymentProcessView

urlpatterns = [
    path('admin/account/customer/<int:pk>/detail/', (OrganisationDetailView.as_view()), name="customer_detail"),
    path('admin/', admin.site.urls),
    path('account/', include('django.contrib.auth.urls')),  # <-- Built-in views

    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='signup_register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path("", HomeView.as_view(), name="home"),
    path("register/company/", RegisterCompany.as_view(), name="register_company"),
    path("packages/", PackageView.as_view(), name="package-view"),
    path("payment/", PaymentView.as_view(), name="payment-view"),
    path("process/payment/", PaymentProcessView.as_view(), name="process-payment"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

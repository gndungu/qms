import traceback

from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render, redirect
from django.db import transaction
from django.urls import reverse_lazy
from django.views import View
from django.contrib import admin, messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, DetailView

from .forms import RegistrationForm
from .models import Organisation


class CustomLoginView(LoginView):
    template_name = "admin/login.html"

    def form_valid(self, form):
        # Call the parent class's form_valid method to perform standard login
        self.request.session['otp_verified'] = False
        response = super().form_valid(form)
        return response  # Redirect to the default success URL

    def get_success_url(self):
        # Define the custom success URL where you want to redirect the user
        # return reverse_lazy('otp-verification')  # Replace 'custom_dashboard' with your desired URL name
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        # Get the parent context data
        context = super().get_context_data(**kwargs)

        # Add custom context data
        context['title'] = 'Login'

        return context


class OrganisationDetailView(DetailView):
    template_name = 'admin/organisation/organisation_detail.html'
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailView, self).get_context_data(**kwargs)
        context['available_apps'] = admin.site.get_app_list(self.request)
        context['title'] = "Home"
        return context

#
# class CustomLoginView(LoginView):
#     template_name = 'account/login.html'
#     redirect_authenticated_user = True
#     success_url = reverse_lazy('home')  # replace 'home' with your actual home URL name



class RegisterView(View):
    template_name = 'registration/register.html'
    title = "Sign Up"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin:index')  # Redirect to the index page if the user is already logged in
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form, 'title': self.title})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.register_user()
                    org = Organisation(representative=user)
                    org.name = form.cleaned_data.get('company_name')
                    org.save()
                    messages.success(request, "Sign Up successful, Your password has been sent to your email")
                return redirect(reverse_lazy("login"))  # Redirect to login page after successful registration

            except Exception as e:
                messages.error(request, "Sorry, something went wrong")
                print("Exception occurred:")
                traceback.print_exc()  # <-- This prints full traceback to the console
                # Handle any exceptions that might occur during registration
                # You can log the error or display an error message to the user
                pass

        return render(request, self.template_name, {'form': form, 'title': self.title})

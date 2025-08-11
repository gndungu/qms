# myapp/middleware.py
from django.shortcuts import redirect
from django.urls import reverse_lazy
from urllib.parse import urlparse
from system.models import Organisation, Subscription

class ActiveSubscriptionMiddleware:
    """
    Middleware to ensure the logged-in user has an active subscription
    before accessing certain views.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            reverse_lazy('package-view'),
            reverse_lazy('payment-view'),
            reverse_lazy('process-payment'),
            reverse_lazy('logout'),
            reverse_lazy('login'),
        ]

    def __call__(self, request):
        path_only = urlparse(request.get_full_path()).path  # removes query string

        if (
            request.user.is_authenticated
            and path_only not in self.exempt_paths
            and not path_only.startswith("/admin/")
        ):
            try:
                organisation = Organisation.objects.get(representative=request.user)
                has_subscription = Subscription.objects.filter(
                    organisation=organisation,
                    is_active=True
                ).exists()
                if not has_subscription:
                    return redirect(reverse_lazy('package-view'))
            except Organisation.DoesNotExist:
                return redirect(reverse_lazy('package-view'))

        return self.get_response(request)

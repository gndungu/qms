# forms.py
import random
import string
import traceback

from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import transaction
from django.forms import inlineformset_factory

from account.models import CustomUser, Organisation, Department, OrganisationLocation


class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='Full Name')
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Phone Number')
    company_name = forms.CharField(label="Company Name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('company_name', css_class='form-group col-md-12 mb-3'),
            ),
            Submit('register', 'Register', css_class='btn btn-primary btn-block')
        )
    #
    def send_password_email(self, password):
        subject = 'Your Password for Registration'
        message = f'Hello {self.cleaned_data["full_name"]}, your password is: {password}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.cleaned_data["email"]]
        # Sample data for the SMS
        sms_data = {
            'recipient': self.cleaned_data["phone_number"],  # Phone number of the recipient
            'message': message,  # Content of the message
        }
        # Call the send_sms function with the sample data
        # sent_message = send_sms(sms_data)
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    def register_user(self):
        # Generate a random password
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        try:
            with transaction.atomic():
                # Create a new user with the provided information
                user = CustomUser.objects.create(email=self.cleaned_data['email'], is_active=True, is_staff=True, account_type=CustomUser.AccountType.CUSTOMER)
                user.full_name= f"{self.cleaned_data['full_name']} "
                user.set_password(password)

                self.send_password_email(password)

                # Create or get the "SMS users" group
                sms_users_group, created = Group.objects.get_or_create(name=CustomUser.AccountType.CUSTOMER)

                # Add the user to the "SMS users" group
                user.groups.add(sms_users_group)
                user.save()
        except Exception as e:
            print("Exception occurred:")
            traceback.print_exc()  # <-- This prints full traceback to the console


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['name', 'address', 'tin_number', 'region', 'phone', 'email', 'sector', 'evaluation_level', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # important for formsets
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-6')),
            Row(Column('tin_number', css_class='form-group col-md-6')),
            Row(Column('address', css_class='form-group col-md-12')),
            Row(Column('phone', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6')),
            Row(Column('region', css_class='form-group col-md-6'),
                Column('sector', css_class='form-group col-md-6')),
            Row(Column('evaluation_level', css_class='form-group col-md-6')),
            Row(Column('notes', css_class='form-group col-md-12')),
        )

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'coordinator']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-6'),
                Column('coordinator', css_class='form-group col-md-6')),
        )

class OrganisationLocationForm(forms.ModelForm):
    class Meta:
        model = OrganisationLocation
        fields = ['address', 'city', 'district', 'region', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('address', css_class='form-group col-md-6'),
                Column('city', css_class='form-group col-md-6')),
            Row(Column('district', css_class='form-group col-md-6'),
                Column('region', css_class='form-group col-md-6')),
            Row(Column('notes', css_class='form-group col-md-12')),
        )


DepartmentFormSet = inlineformset_factory(
    Organisation, Department, form=DepartmentForm,
    fields=['name', 'coordinator'], extra=1, can_delete=True
)

LocationFormSet = inlineformset_factory(
    Organisation, OrganisationLocation, form=OrganisationLocationForm,
    fields=['address', 'city', 'district', 'region', 'notes'], extra=1, can_delete=True
)
from django import forms


class RegisterSaloonForm(forms.Form):
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last Name")
    saloon_name = forms.CharField()
    phone = forms.CharField()
    email = forms.CharField()
    address = forms.CharField()
    opening_hours = forms.TimeField()
    closing_hours = forms.TimeField()


class RegisterClientOrAdminForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    email = forms.CharField()
    date_of_birth = forms.DateField()
    gender = forms.CharField()
    password = forms.CharField()


class UpdateClientInfoForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.CharField(required=False)


class UpdateSaloonInfo(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.CharField(required=False)
    address = forms.CharField(required=False)
    opening_hours = forms.TimeField(required=False)
    closing_hours = forms.TimeField(required=False)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()


class SearchAppointment(forms.Form):
    date = forms.DateField(required=True)

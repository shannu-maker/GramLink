from django import forms
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order, State, District, Mandal, Village

class ShopkeeperForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Select State", required=True)
    district = forms.ModelChoiceField(queryset=District.objects.none(), empty_label="Select District", required=True)
    mandal = forms.ModelChoiceField(queryset=Mandal.objects.none(), empty_label="Select Mandal", required=True)
    village = forms.ModelChoiceField(queryset=Village.objects.none(), empty_label="Select Village", required=True)

    class Meta:
        model = Shopkeeper
        fields = ['name', 'email', 'address', 'password', 'state', 'district', 'mandal', 'village']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.none()
        self.fields['mandal'].queryset = Mandal.objects.none()
        self.fields['village'].queryset = Village.objects.none()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomerForm(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Select State", required=True)
    district = forms.ModelChoiceField(queryset=District.objects.none(), empty_label="Select District", required=True)
    mandal = forms.ModelChoiceField(queryset=Mandal.objects.none(), empty_label="Select Mandal", required=True)
    village = forms.ModelChoiceField(queryset=Village.objects.none(), empty_label="Select Village", required=True)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'password', 'state', 'district', 'mandal', 'village']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.none()
        self.fields['mandal'].queryset = Mandal.objects.none()
        self.fields['village'].queryset = Village.objects.none()

class DeliveryPartnerForm(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Select State", required=True)
    district = forms.ModelChoiceField(queryset=District.objects.none(), empty_label="Select District", required=True)
    mandal = forms.ModelChoiceField(queryset=Mandal.objects.none(), empty_label="Select Mandal", required=True)
    village = forms.ModelChoiceField(queryset=Village.objects.none(), empty_label="Select Village", required=True)

    class Meta:
        model = DeliveryPartner
        fields = ['name', 'email', 'vehicle', 'password', 'state', 'district', 'mandal', 'village']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.none()
        self.fields['mandal'].queryset = Mandal.objects.none()
        self.fields['village'].queryset = Village.objects.none()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['shopkeeper', 'name', 'image', 'price', 'quantity', 'description']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'shopkeeper', 'delivery_partner', 'delivery_address', 'delivery_phone', 'delivery_time', 'status']

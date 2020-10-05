import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from saloon.models import SaloonService, Style, File, Rating, Appointment
from .Form import RegisterClientOrAdminForm, LoginForm, RegisterSaloonForm
from .models import ClientAccount, CustomUser, ManagerAccount, Saloon, Notification
from django.contrib.auth import authenticate, login
import uuid
from django.contrib import messages
import os
from datetime import date
from .Serializer import serialize_style
from salon.settings import BASE_DIR
# Create your views here.


def home_page(request, *args, **kwargs):
    return render(request, 'saloon/index.html')


class ManagerDashboard(View, LoginRequiredMixin):
    def get(self, request):
        saloon = Saloon.objects.get(owner=request.user)
        notifications = Notification.objects.filter(destination=request.user, seen=False)
        Notification.objects.filter(destination=request.user, seen=False).update(seen=True)
        return render(request, 'saloon/salonOwner_dashboard.html', {"saloon": saloon, "notifications": notifications})


class CustomerDashboard(View, LoginRequiredMixin):
    def get(self, request):
        customer = ClientAccount.objects.get(owner=request.user)
        notifications = Notification.objects.filter(destination=request.user, seen=False)
        Notification.objects.filter(destination=request.user, seen=False).update(seen=True)
        return render(request, 'saloon/customer_dashboard.html', {"customer": customer, "notifications": notifications})


class CreateManagerAccount(View):
    def get(self, request):
        return render(request, 'saloon/salonOwner_register_salon.html')

    def post(self, request):
        form = RegisterSaloonForm(data=request.POST)
        password = uuid.uuid4().hex[:6].upper()

        try:
            print(request.POST)
            if form.is_valid():

                CustomUser.objects.create_user(email=form.cleaned_data.get('email'),
                                               password=password,
                                               first_name=form.cleaned_data.get("first_name"),
                                               last_name=form.cleaned_data.get("last_name"),
                                               phone=form.cleaned_data.get("phone"),

                                               )
                user = authenticate(request, email=form.cleaned_data["email"], password=password)
                print(password)
                if user is not None:
                    login(request, user)
                    Saloon.objects.create(
                                          owner=user, address=form.cleaned_data.get('address'),
                                          saloon_name=form.cleaned_data.get('saloon_name'),
                                          opening_hours=form.cleaned_data.get('opening_hours'),
                                          closing_hours=form.cleaned_data.get('closing_hours'),
                                          )
                    messages.success(request, 'Your password is'+password, )
                    return redirect('saloon-dashboard')
                    # return render(request, 'saloon/salonOwner_dashboard.html', {"saloon": saloon, "password": password})
                else:
                    return redirect('home-page')
            else:
                return render(request, 'saloon/salonOwner_register_salon.html', {"errors": form.errors})
        except Exception as e:
            print(str(e))
            return render(request, 'saloon/salonOwner_register_salon.html', {"errors": [str(e)]})


class CreateCustomerAccount(View):
    def get(self, request):
        return render(request, 'saloon/customer_register.html')

    def post(self, request):
        data = RegisterClientOrAdminForm(data=request.POST)
        if data.is_valid():
            try:
                CustomUser.objects.create_user(email=data.cleaned_data.get('email'),
                                               password=data.cleaned_data.get('password'),
                                               first_name=data.cleaned_data.get("first_name"),
                                               last_name=data.cleaned_data.get("last_name"),
                                               gender=data.cleaned_data.get("gender"),
                                               date_of_birth=data.cleaned_data.get("date_of_birth"),
                                               phone=data.cleaned_data.get("phone"))
                user = authenticate(request, email=data.cleaned_data["email"], password=data.cleaned_data["password"])
            except Exception as e:
                print(request.POST)
                print(str(e))
                return render(request, 'saloon/customer_register.html',
                              {
                                  "form": data,
                                  "errors": ["can not create this account, use other credentials pleas and try again"]
                              })
            if user is not None:
                # user.phone = data.cleaned_data.get("phone")
                # user.gender = data.cleaned_data.get("gender")
                # user.date_of_birth = data.cleaned_data.get("date_of_birth"),

                ClientAccount.objects.create(owner=user)
                customer = ClientAccount.objects.get(owner=user)
                login(request, user)
                return render(request, 'saloon/customer_dashboard.html', {"customer": customer})
            else:
                return render(request, 'saloon/customer_register.html')

        else:
            print("Noo ", data.errors)
            # print(data)
            return render(request, 'saloon/customer_register.html', {"form": data, "errors": data.errors})


class LoginView(View):
    def get(self, request, user_type):
        return render(request, 'saloon/customerlogin.html', {"as": user_type})

    def post(self, request, user_type=None):
        form = LoginForm(data=request.POST)
        try:
            if form.is_valid():
                user = authenticate(request, email=form.cleaned_data["email"], password=form.cleaned_data["password"])
                print(user)
                if user is not None:
                    login(request, user)
                else:
                    return render(request, 'saloon/customerlogin.html',
                                  {"errors": ["can not find user with the provided credentials"]})

                if Saloon.objects.filter(owner=user).exists():
                    # manager = Saloon.objects.get(owner=user)
                    return redirect('saloon-dashboard')
                    # return render(request, 'saloon/salonOwner_dashboard.html', {"manager": manager})
                if ClientAccount.objects.filter(owner=user).exists():
                    # customer = ClientAccount.objects.get(owner=user)
                    # return render(request, )
                    return redirect('customer-dashboard')
                if ManagerAccount.objects.filter(owner=user).exists():
                    return render(request, '')
            else:
                print(form.errors)
                return render(request, 'saloon/customerlogin.html', {"errors": form.errors})
        except Exception as e:
            print(e)
            return render(request, 'saloon/customerlogin.html')


class DisplayServices(View, LoginRequiredMixin):
    def get(self, request):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                saloon = saloons.first()
                services = SaloonService.objects.filter(saloon=saloon)
                print(services)
                return render(request, 'saloon/salon_services.html', {"services": services, "isClient": False})
            else:
                messages.error(request, 'You can not access this page')
                return redirect('home-page')
        except Exception as e:
            print(str(e))
            messages.error(redirect, str(e))
            return redirect('home-page')


class CreateService(View, LoginRequiredMixin):
    def get(self, request):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                return render(request, 'saloon/salonOwner_record_service.html')
            else:
                messages.error(request, 'Can not access this page')
                return redirect('home-page')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')

    def post(self, request):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                saloon = saloons.first()
                name = request.POST.get('name')
                price = request.POST.get('price')
                SaloonService.objects.create(saloon=saloon, name=name, price=price)
                # services = SaloonService.objects.filter(saloon=saloon)
                # print(services)
                # return render(request, 'saloon/salon_services.html', {"services": services})
                messages.success(request, 'Create successfully')
                return redirect('services-view')
            else:
                messages.error(request, 'can not access the page')
                return redirect('home-page')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class CreateStyles(View, LoginRequiredMixin):
    def get(self, request):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                saloon = saloons.first()
                services = SaloonService.objects.filter(saloon=saloon)
                return render(request, 'saloon/salonOwner_record_service_styles.html', {"services": services})
            else:
                messages.error(request, 'can not access this page')
                return redirect('home-page')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')

    def post(self, request):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                service = SaloonService.objects.get(id=request.POST.get('services'))
                name = request.POST.get('style')
                Style.objects.create(service=service, name=name)
                messages.error(request, 'Style added ')
                return redirect('saloon-dashboard')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class ServiceStyles(View, LoginRequiredMixin):
    def get(self, request, service_id):
        saloons = Saloon.objects.filter(owner=request.user)
        if saloons.exists():
            service = SaloonService.objects.get(id=service_id)
            styles = Style.objects.filter(service=service)
            return render(request, 'saloon/service_styles.html', {"styles": styles, "isClient": False})
        else:
            service = SaloonService.objects.get(id=service_id)
            styles = Style.objects.filter(service=service)
            return render(request, 'saloon/service_styles.html', {"styles": styles, "isClient": True})


class StylesPictures(View, LoginRequiredMixin):
    def get(self, request, style_id):
        try:
            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                style = Style.objects.get(id=style_id)
                pictures = File.objects.filter(style=style)

                return render(request, 'saloon/style_pictures.html',
                              {"pictures": pictures, "isClient": False})
            else:
                style = Style.objects.get(id=style_id)
                pictures = File.objects.filter(style=style)
                saloon = style.service.saloon
                return render(request, 'saloon/style_pictures.html',
                              {"pictures": pictures, "isClient": True, "saloon": saloon})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')

    def post(self, request, style_id):
        try:

            saloons = Saloon.objects.filter(owner=request.user)
            if saloons.exists():
                style = Style.objects.get(id=style_id)
                # print(request.FILES)
                file = request.FILES.get('image')

                fs = FileSystemStorage()
                # print(request.META['HTTP_HOST'])
                filename = fs.save('pictures/'+file.name, file)
                uploaded_file_url = fs.url(filename)
                File.objects.create(url=uploaded_file_url, style=style, name="SALOON STYLE")
                pictures = File.objects.filter(style=style)
                return render(request, 'saloon/style_pictures.html', {"pictures": pictures})
            else:
                messages.error(request, 'Can not access this page')
                return redirect('home-page')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class DeletePicture(View, LoginRequiredMixin):
    def post(self, request, style_id):
        saloons = Saloon.objects.filter(owner=request.user)
        if saloons.exists():
            url = File.objects.get(id=style_id).url
            new_url = 'pictures/'
            i = 0
            for u in url:
                i = i+1
                if i >= 8:
                    new_url += u
            os.remove(new_url)
            File.objects.get(id=style_id).delete()
            messages.success(request, 'File deleted')
            return redirect('saloon-dashboard')
        else:
            return redirect('home-page')


class DisplaySaloon(View, LoginRequiredMixin):
    def get(self, request):
        try:
            ratings = Rating.objects.filter(rate__gte=3)
            saloons = []
            if ratings.exists():
                for rating in ratings:
                    saloons.append(rating.saloon)
            else:
                saloons.extend(Saloon.objects.all()[:5])
            saloons = list(dict.fromkeys(saloons))
            return render(request, 'saloon/all_salons.html', {"saloons": saloons})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class DisplaySaloonServicesToCustomer(View, LoginRequiredMixin):
    def get(self, request, saloon_id):
        try:
            saloon = Saloon.objects.get(id=saloon_id)
            services = SaloonService.objects.filter(saloon=saloon)
            print(services)
            return render(request, 'saloon/salon_services.html', {"services": services, "isClient": True})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class SearchSaloon(View, LoginRequiredMixin):
    def get(self, request):
        try:
            data = request.GET

            value = data.get('value')
            owner = CustomUser.objects.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))

            saloons = Saloon.objects.filter(
                Q(saloon_name__icontains=value) |
                Q(address__icontains=value) |
                Q(owner=owner.first())
            )
            if saloons.exists():
                return render(request, 'saloon/all_salons.html', {"saloons": saloons})
            else:
                messages.warning(request, 'No result found')
                return render(request, 'saloon/all_salons.html', {"saloons": []})
        except Exception as e:
            print(str(e))
            messages.error(request, str(e))
            return redirect('home-page')


class MakeAppointment(View, LoginRequiredMixin):
    def get(self, request, saloon_id):
        try:
            saloon = Saloon.objects.get(id=saloon_id)
            services = SaloonService.objects.filter(saloon=saloon)
            return render(request, 'saloon/customer_make_appointment.html', {
                "saloon": saloon,
                "services": services
            })
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home-page')

    def post(self, request, saloon_id):
        try:
            client = ClientAccount.objects.get(owner=request.user)
            saloon = Saloon.objects.get(id=saloon_id)
            style = Style.objects.get(id=request.POST.get('style'))
            time = request.POST.get('time')
            date = request.POST.get('date')
            date_time = date()
            comment = request.POST.get('comment')
            Appointment.objects.create(saloon=saloon, style=style, client=client, comment=comment, time=time)
            messages.success(request, 'Appointment sent to the saloon successfully ')
            return redirect('customer-dashboard')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class GetStylesFromServiceAjax(View, LoginRequiredMixin):
    def get(self, request, service_id):
        try:
            service = SaloonService.objects.get(id=service_id)
            styles = Style.objects.filter(service=service)
            if styles is None:
                return JsonResponse({"styles": []})
            styles_list = [serialize_style(style) for style in styles]
            return JsonResponse({"styles": styles_list})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)

import json
from django.core.mail import send_mail as sm
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
from .Serializer import serialize_style

import datetime
# Create your views here.
# tools


def make_date_time(date):
    date_only = date.split(' ')[0]
    hours = date.split(' ')[1]
    year = date_only.split('/')[0]
    month = date_only.split('/')[1]
    day = date_only.split('/')[2]
    hour = hours.split(':')[0]
    minuets = hours.split(':')[1]
    final_date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minuets))
    return final_date


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
        appointments = Appointment.objects.filter(client=customer, deleted=False, approved=True, seen=False)
        badge = 0
        for appointment in appointments:
            appointment.seen = True
            if (datetime.datetime.now().timestamp() * 1000) < (appointment.time.timestamp() * 1000):
                badge = badge + 1
            appointment.save()
        return render(request, 'saloon/customer_dashboard.html',
                      {"customer": customer, "notifications": notifications, "appointment_badge": badge})


class CreateManagerAccount(View):
    def get(self, request):
        return render(request, 'saloon/salonOwner_register_salon.html')

    def post(self, request):
        form = RegisterSaloonForm(data=request.POST)
        password = uuid.uuid4().hex[:6].upper()

        try:
            if form.is_valid():
                message = 'Welcome to Saloon and Hair style Finder and Reservation System\n Your username is ' \
                          '' + form.cleaned_data["email"] + ' Your password is ' \
                        '' + password + ' \nPlease wait patiently for the approval.\n' \
                        'You can now log in to http://127.0.0.1:8000/login/customer/MANAGER'
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
                    messages.success(request, 'Your password is '+password+'. A welcome message was sent to your email.')

                    res = sm(
                        subject='Welcome To S.H.F.R.S',
                        message=message,
                        from_email='kayitarelie20657@gmail.com',
                        recipient_list=[form.cleaned_data["email"], ],
                        fail_silently=False,
                    )

                    return redirect('saloon-dashboard')
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

                if user is not None:
                    login(request, user)
                else:
                    return render(request, 'saloon/customerlogin.html',
                                  {"errors": ["can not find user with the provided credentials"]})

                if user.is_superuser:
                    return redirect('/admin/')

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
                saloon = saloons.first()
                style = Style.objects.get(id=style_id)
                # print(request.FILES)
                file = request.FILES.get('image')

                fs = FileSystemStorage()
                # print(request.META['HTTP_HOST'])
                filename = fs.save('pictures/'+file.name, file)
                uploaded_file_url = fs.url(filename)
                File.objects.create(url=uploaded_file_url, style=style, name="SALOON STYLE")
                pictures = File.objects.filter(style=style)
                return render(request, 'saloon/style_pictures.html', {
                    "pictures": pictures, "isClient": False, "saloon": saloon})
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
            date = request.POST.get('date')
            time = make_date_time(date)
            client = ClientAccount.objects.get(owner=request.user)
            saloon = Saloon.objects.get(id=saloon_id)
            style = Style.objects.get(id=request.POST.get('style'))
            comment = request.POST.get('comment')
            Appointment.objects.create(saloon=saloon, style=style, client=client, comment=comment, time=time)
            messages.success(request, 'Appointment sent to the saloon ; please wait as the saloon responds!')
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


class ListAppointments(View, LoginRequiredMixin):
    def get(self, request):
        try:
            saloon = Saloon.objects.get(owner=request.user)
        except:
            messages.error(request, 'You can not access this page')
            return redirect('home-page')

        appointments = Appointment.objects.filter(approved=False, saloon=saloon, deleted=False)
        approved_appointments = Appointment.objects.filter(approved=True, saloon=saloon, deleted=False)
        return render(request, 'saloon/salonOwner_view_appointments.html',
                      {"approved_appointments":  approved_appointments,
                       "appointments": appointments})

    def post(self, request, appointment_id, accepted):
        try:
            saloon = Saloon.objects.get(owner=request.user)
        except:
            messages.error(request, 'You can not access this page')
            return redirect('home-page')

        appointment = Appointment.objects.get(id=appointment_id)
        if accepted == "accepted":
            appointment.approved = True
        else:
            appointment.deleted = True
        appointment.save()
        return redirect('saloon-appointments')


class AppointmentDetails(View, LoginRequiredMixin):
    def get(self, request, appointment_id):
        try:
            saloon = Saloon.objects.get(owner=request.user)
        except:
            messages.error(request, 'You can not access this page')
            return redirect('home-page')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            in_past = ((datetime.datetime.now().timestamp() * 1000) > (appointment.time.timestamp() * 1000))
            return render(request, 'saloon/saloon_appointment_details.html',
                          {"appointment": appointment, "in_past": in_past})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home-page')


class CustomerAppointments(View, LoginRequiredMixin):
    def get(self, request):
        try:
            customer = ClientAccount.objects.get(owner=request.user)
        except:
            messages.error(request, 'Can not access this page')
            return redirect('home-page')

        appointments = Appointment.objects.filter(client=customer)
        return render(request, 'saloon/manage_appointment.html', {"appointments": appointments})


class CustomerAppointmentDetails(View, LoginRequiredMixin):
    def get(self, request, appointment_id):
        try:
            customer = ClientAccount.objects.get(owner=request.user)
        except:
            messages.error(request, 'Can not access this page')
            return redirect('home-page')

        appointment = Appointment.objects.get(id=appointment_id)
        return render(request, 'saloon/customer_change_appointment.html', {"appointment": appointment})

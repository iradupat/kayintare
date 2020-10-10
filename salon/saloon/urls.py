from django.urls import path
from .views import (home_page, CreateCustomerAccount, DeletePicture,
                    LoginView, CreateManagerAccount, CustomerDashboard, ManagerDashboard,
                    DisplayServices, CreateService, CreateStyles, ServiceStyles, StylesPictures,
                    DisplaySaloon, DisplaySaloonServicesToCustomer, SearchSaloon, MakeAppointment,
                    GetStylesFromServiceAjax, ListAppointments, AppointmentDetails, CustomerAppointments,
                    CustomerAppointmentDetails, RateSaloon, CheckRateSaloon, QuickAuthentication,
                    AnnouncementBoard,
                    )
urlpatterns = [

    path('', home_page, name="home-page"),
    path('register/customer/', CreateCustomerAccount.as_view(), name="create-customer-account"),
    path('register/saloon/', CreateManagerAccount.as_view(), name="register-saloon"),
    path('login/customer/<str:user_type>', LoginView.as_view(), name="system-login"),
    path('customer/dashboard/', CustomerDashboard.as_view(), name="customer-dashboard"),
    path('customer/appointments/', CustomerAppointments.as_view(), name="customer-appointments"),
    path('customer/appointment-details/<int:appointment_id>', CustomerAppointmentDetails.as_view(),
         name='customer-appointment-details'),
    path('saloon/dashboard/', ManagerDashboard.as_view(), name="saloon-dashboard"),
    path('saloon/services/', DisplayServices.as_view(), name="services-view"),
    path('saloon/create/service', CreateService.as_view(), name="create-service"),
    path('saloon/service/add/style', CreateStyles.as_view(), name="create-style"),
    path('saloon/service/styles/<int:service_id>', ServiceStyles.as_view(), name="service-styles"),
    path('saloon/style/pictures/<int:style_id>', StylesPictures.as_view(), name="style-pictures"),
    path('saloon/style/delete/<int:style_id>', DeletePicture.as_view(), name="delete-style"),
    path('saloon/display/', DisplaySaloon.as_view(), name="display-saloons"),
    path('saloon/services/<int:saloon_id>', DisplaySaloonServicesToCustomer.as_view(), name="services-saloon"),
    path('saloon/search/', SearchSaloon.as_view(), name="search-saloon"),
    path('saloon/make_appointment/<int:saloon_id>', MakeAppointment.as_view(), name="make-appointment"),
    path('saloon/list-appointment/', ListAppointments.as_view(), name="saloon-appointments"),
    path('saloon/appointment-details/<int:appointment_id>', AppointmentDetails.as_view(), name="appointment-details"),
    path('saloon/update-appointment/<int:appointment_id>/<str:accepted>',
         ListAppointments.as_view(), name="accept-decline-appointment"),
    path('customer/rating/<int:saloon_id>/<int:style_id>', RateSaloon.as_view(), name="customer-rate-saloon"),
    path('customer/quick-authentication/', QuickAuthentication.as_view(), name="quick-auth"),

    path('admin/announcement-board/', AnnouncementBoard.as_view(), name="announcement-board"),
    # ajax call
    path('ajax/styles/<int:service_id>', GetStylesFromServiceAjax.as_view(), name="get-styles-ajax"),
    path('ajax/rating/<int:saloon_id>', CheckRateSaloon.as_view(), name="rate-saloon")

]

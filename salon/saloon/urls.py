from django.urls import path, include
from .views import (home_page, CreateCustomerAccount, DeletePicture,
                    LoginView, CreateManagerAccount, CustomerDashboard, ManagerDashboard,
                    DisplayServices, CreateService, CreateStyles, ServiceStyles, StylesPictures,
                    DisplaySaloon, DisplaySaloonServicesToCustomer, SearchSaloon, MakeAppointment,
                    GetStylesFromServiceAjax,
                    )
urlpatterns = [

    path('', home_page, name="home-page"),
    path('register/customer/', CreateCustomerAccount.as_view(), name="create-customer-account"),
    path('register/saloon/', CreateManagerAccount.as_view(), name="register-saloon"),
    path('login/customer/<str:user_type>', LoginView.as_view(), name="system-login"),
    path('customer/dashboard/', CustomerDashboard.as_view(), name="customer-dashboard"),
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

    #ajax call
    path('ajax/styles/<int:service_id>', GetStylesFromServiceAjax.as_view(), name="get-styles-ajax")

]

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns=[
    path('', views.home,),
    path('signup/', views.signup),
    path('createUser/', views.createUser, name="create_user"),
    path('loginUser/', views.loginUser, name="login_user"),
    path('roomspage/', views.roomspage, name="roomspage"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('reservation/', views.reservation, name="reservation"),
    path('updatereservation/', views.updatereservation, name="updatereservation"),
    path('processupdatereservation/', views.process_update_reservation, name="processupdatereservation"),
    path('processReservation/', views.processReservation),
    path('cancelreservation/', views.cancel_reservation, name='cancel_reservation'),
    path('adminlogin/', views.adminLogin, name="adminlogin"),
    path('processadminlogin/', views.processAdminLogin, name="process_admin_login"),
    path('admindashboard/', views.adminDashboard, name="admindashboard"),
    path('admindashboard/admincreateguest/', views.adminCreateGuest, name="admincreateguest"),
    path('admindashboard/adminupdateguest/', views.adminUpdateGuest, name="adminupdateguest"),
    path('admindashboard/admindeleteguest/', views.adminDeleteGuest, name="admindeleteguest"),
    path('sendmessage/', views.send_message),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
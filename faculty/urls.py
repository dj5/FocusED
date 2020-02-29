from django.contrib import admin
from django.urls import path
from faculty import views

urlpatterns = [
    path('',views.login),
    path('login',views.login),
    path('logout',views.logout),
    path('forgot',views.forgot),
    path('dashboard',views.dashboard),
    # path('webcam',views.webcam),
    path('statistics',views.statistics),
    path('cards',views.cards),
    path('student_overview',views.student_overview),
    path('student_attentiveness',views.student_attentiveness),
    path('settings',views.settings),
    path('attendance',views.attendance),
    path('get-avg-attentiveness',views.getAvgAttentiveness),
    path('get-std-attentiveness',views.getStdAttentiveness),
    path('notifications',views.notifications),
    path('dummy-record-ins',views.dummyRecordIns),
    path('create_post',views.create_post),
    path('create_post_Attentiveness',views.create_post_Attentiveness),
    path('create_post_Emotion',views.create_post_Emotion),
    path('create_post_Interaction',views.create_post_Interaction),
    path('create_post_Total',views.create_post_Total),
    path('create_post_BarChart',views.create_post_BarChart),
    path('create_post_room',views.create_post_room)
]
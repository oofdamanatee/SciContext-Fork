""" SciContext Project URL Configuration """
from django.urls import path, include
from contexts import views

urlpatterns = [
    path('', views.home, name='SciContext homepage'),
    path('tutorial', views.tutorial, name='SciContext tutorial'),

    path('contexts/', include('contexts.urls')),
    path('fields/', include('fields.urls')),
    path('onts/', include('onts.urls')),
    path('projects/', include('projects.urls')),
    path('servers/', include('servers.urls')),
    path('terms/', include('terms.urls')),
]

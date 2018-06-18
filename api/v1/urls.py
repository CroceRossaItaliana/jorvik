from django.conf.urls import url

from api.v1 import views


urlpatterns = [
    url(r'^me/anagrafica/base/', views.MiaAnagraficaBase.as_view()),
    url(r'^me/anagrafica/completa/', views.MiaAnagraficaCompleta.as_view()),
    url(r'^me/appartenenze/attuali/', views.MieAppartenenzeAttuali.as_view()),
]

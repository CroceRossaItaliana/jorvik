from django.conf.urls import url

from api.v1 import views

urlpatterns = [
    url(r'^me/anagrafica/base/', views.MiaAnagraficaBase.as_view()),
    url(r'^me/anagrafica/completa/', views.MiaAnagraficaCompleta.as_view()),
    url(r'^me/appartenenze/attuali/', views.MieAppartenenzeAttuali.as_view()),
    url(r'^me/appartenenza/completa/', views.MiaAppartenenzaComplaeta.as_view()),
    url(r'^user/anagrafica/base/', views.UserAnagraficaBase.as_view()),
    url(r'^user/anagrafica/completa/', views.UserAnagraficaCompleta.as_view()),
    url(r'^user/appartenenze/attuali/', views.UserAppartenenzeAttuali.as_view()),
    url(r'^user/appartenenza/completa/', views.UserAppartenenzaCompleta.as_view()),
    url(r'^search/users/', views.SearchUserAppartenenzaCompleta.as_view()),
]

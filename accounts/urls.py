from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'login/$', views.sign_in),
    url(r'sign_in/$', views.sign_in, name='sign_in'),
    url(r'sign_up/$', views.sign_up, name='sign_up'),
    url(r'sign_out/$', views.sign_out, name='sign_out'),
    url(r'profile/$', views.profile, name='profile'),
    url(r'profile_crop/$', views.profile_crop, name='profile_crop'),
    url(r'profile/edit/$', views.profile_edit, name='profile_edit'),
    url(r'profile/password_change/$',
        views.password_change, name='password_change'),
    url(r'$', views.profile),
]

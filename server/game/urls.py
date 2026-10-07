from django.urls import path

from game import ad_views, auth_views, views


app_name = "game"

urlpatterns = [
    path("ads/preview/", ad_views.ad_preview, name="ad-preview"),
    path("api/ads/decision/", ad_views.ad_decision, name="ad-decision"),
    path("", views.delivery_dashboard, name="delivery-dashboard"),
    path("api/auth/csrf/", auth_views.csrf_token, name="csrf"),
    path("api/auth/login/", auth_views.login_view, name="login"),
    path("api/auth/logout/", auth_views.logout_view, name="logout"),
    path("play/", views.play, name="play"),
    path("api/player/", views.player_view, name="player"),
    path("api/delivery/", views.delivery_view, name="delivery"),
    path("api/history/", views.history, name="history"),
    path("api/auth/csrf/",views.csrf_view,name="csrf",),
    path("api/auth/login/",views.api_login,name="api-login",),
]

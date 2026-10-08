from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Smart Restaurant Admin"
admin.site.site_title = "Smart Restaurant Portal"
admin.site.index_title = "Restaurant Management & Kitchen Ops"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),
]

from django.contrib import admin
from django.urls import path, include
from ui.views import index as ui_index

urlpatterns = [
    path('', ui_index, name="index"),
    path('ui/', include('ui.urls')),
    path('admin/', admin.site.urls),
]

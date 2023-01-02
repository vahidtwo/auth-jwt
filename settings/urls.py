from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.authentication import JWTAuthentication

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Accounting API",
#         default_version='v1',
#         description="Test description",
#         terms_of_service="",
#         contact=openapi.Contact(email="vahidtwo@gmail.com"),
#         license=openapi.License(name="Test License"),
#     ),
#     public=True,
#     authentication_classes=[JWTAuthentication],
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    # path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('api/api.json/', schema_view.without_ui(cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

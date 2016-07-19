from django.contrib import admin
from release.models import *
from guardian.models import *

# Register your models here.

admin.site.register(Host)
admin.site.register(Project)
admin.site.register(ProjectGroup)
admin.site.register(UserObjectPermission)
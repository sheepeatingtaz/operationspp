from django.contrib import admin

# Register your models here.
from spy.models import TrailStep


class TrailStepAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'directions', 'clue', 'answer']


admin.site.register(TrailStep, TrailStepAdmin)

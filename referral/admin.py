from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):

    # title of the columns in common list
    list_display = ('id', 'username', 'personal_code', 'referral_code',
                    'token', )

    # create links on the column
    list_display_links = ('id', 'username', )

    # create searche field on the top
    search_fields = ('username', 'personal_code', )


admin.site.register(User, UserAdmin)

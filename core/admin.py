from django.contrib import admin
from core.models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_username', 'user_email', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user__email')
    raw_id_fields = ('user',)  # Use raw_id_fields for ForeignKey fields for better performance

    def user_full_name(self, obj):
        """Returns the full name of the associated user."""
        return obj.user.get_full_name()

    user_full_name.short_description = 'Full Name'  # Customize the column header

    def user_username(self, obj):
        """Returns the username of the associated user."""
        return obj.user.username

    user_username.short_description = 'Username'

    def user_email(self, obj):
        """Returns the email of the associated user."""
        return obj.user.email

    user_email.short_description = 'Email'

    def is_active(self, obj):
        """Indicates if the associated user is active."""
        return obj.user.is_active

    is_active.boolean = True  # Display as a boolean in the admin interface
    is_active.short_description = 'Active'


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'status', 'date_time_created')
    list_filter = ('status',)  # Filter by status (Pending, Accepted, Rejected)
    search_fields = ('from_user__username', 'to_user__username')  # Search by usernames
    ordering = ('-date_time_created',)  # Order by creation date, newest first

    def from_user(self, obj):
        """Returns the username of the sender."""
        return obj.from_user.username

    from_user.short_description = 'From'

    def to_user(self, obj):
        """Returns the username of the recipient."""
        return obj.to_user.username

    to_user.short_description = 'To'


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'user_username', 
        'game_id', 
        'airline', 
        'departure_airport', 
        'arrival_airport', 
        'departure_date', 
        'departure_time', 
        'is_active'
    )
    list_filter = ('airline', 'departure_airport', 'arrival_airport', 'is_active', 'departure_date')
    search_fields = (
        'user__username', 
        'game_id', 
        'airline', 
        'departure_airport', 
        'arrival_airport'
    )
    raw_id_fields = ('user',)  # Optimized for large datasets

    def user_username(self, obj):
        """Returns the username of the associated user."""
        return obj.user.username
    user_username.short_description = 'Username'  # Customize column header
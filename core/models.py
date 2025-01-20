from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    date_time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Ensures only one request between two users

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"
    

class Flight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flights")  # Links flight to a user
    game_id = models.PositiveIntegerField()  # Stores the game ID from the frontend or API
    airline = models.CharField(max_length=50)
    departure_airport = models.CharField(max_length=50)
    arrival_airport = models.CharField(max_length=50)
    departure_time = models.TimeField()
    departure_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Flight for Game {self.game_id} by {self.user.username}"
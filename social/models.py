from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"


class Post(models.Model):
    POST_TYPES = [
        ('question', 'Question'),
        ('tip', 'Tip'),
        ('project', 'Project'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(
        'groups_app.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.post_type}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class PostInteraction(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(
        max_length=20,
        choices=[
            ('helpful', 'Helpful'),
            ('not_clear', 'Not Clear'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.reaction} on post {self.post.id}"

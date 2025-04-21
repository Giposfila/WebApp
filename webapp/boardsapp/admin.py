from django.contrib import admin
from .models import Board, Task, Attachment, Comment

admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Attachment)
admin.site.register(Comment)
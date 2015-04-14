from django.contrib import admin

from . import models


class ImageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('image', 'credit', 'caption')
        }),
    )

admin.site.register(models.Image, ImageAdmin)


class VideoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'youtube_id', 'caption')
        }),
    )

admin.site.register(models.Video, VideoAdmin)


class AudioAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'mp3', 'ogg', 'credit', 'caption')
        }),
    )

admin.site.register(models.Audio, AudioAdmin)


class ReviewAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Review, ReviewAdmin)


class PollAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_open']

admin.site.register(models.Poll, PollAdmin)


class PollChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice', 'votes', 'question']

admin.site.register(models.PollChoice, PollChoiceAdmin)
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

from .models import (Question, QuestionGroup, Survey, SurveyResult)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Question)
class AdminQuestion(admin.ModelAdmin):
    list_display = ['text', 'survey', 'is_active', 'order', 'question_group',
                    'question_type', 'anchor',]
    list_filter = ['is_active', ]


@admin.register(QuestionGroup)
class AdminQuestionGroup(admin.ModelAdmin):
    list_display = ['name',]


@admin.register(Survey)
class AdminSurvey(admin.ModelAdmin):
    inlines = [QuestionInline, ]
    list_display = ['text', 'is_active']
    list_filter = ['is_active',]


@admin.register(SurveyResult)
class AdminSurveyResult(admin.ModelAdmin):
    search_fields = ['=course__id',]
    list_display = ['course', 'user', 'question', 'response', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'survey', 'question', 'course']
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

from django.contrib import admin
from .models import Subject, Course, Module, Quiz, Question, Answer, ModuleAccess
# Register your models here.


class AnswerInline(admin.StackedInline):
    model = Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'label']
    inlines = [AnswerInline]

class QuizInline(admin.StackedInline):
    model = Quiz
    


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title', )}

class ModuleInline(admin.StackedInline):
    model = Module
    inlines = [QuizInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title', )}
    inlines = [ModuleInline, QuizInline]


@admin.register(ModuleAccess)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'mod_id']
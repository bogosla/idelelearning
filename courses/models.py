
from django.db import models
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType 
from django.contrib.contenttypes.fields import GenericForeignKey 
from django.template.loader import render_to_string  
from .fields import OrderField

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Course(models.Model):
    students = models.ManyToManyField(User, related_name='course_joined', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_created')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    views = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to='images/')
    paid = models.BooleanField(default=False)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        return f"{self.order}. {self.title} - {self.course}"
    class Meta:
        ordering = ['order']


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in':('text', 'video', 'file', 'image')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    
    class Meta:
        ordering = ['order']

class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html', {'item': self})

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()


class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name="quiz", on_delete=models.CASCADE, blank=True)
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name="m_quiz")
    description = models.CharField(max_length=250)
    pourcent = models.PositiveIntegerField(default=50)
    score_for_each = models.IntegerField(default=0)
    passes = models.ManyToManyField(User, blank=True)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    label = models.CharField(max_length=500)
    response = models.PositiveIntegerField(default=1)

class Answer(models.Model):
    quiz = models.ForeignKey(Question, on_delete=models.CASCADE,related_name="answers", null=True)
    label = models.CharField(max_length=500)
    position = models.PositiveIntegerField(default=1)

class ModuleAccess(models.Model):
    user = models.ForeignKey(User, related_name='access', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='access', on_delete=models.CASCADE)
    mod_id = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.first_name} - {self.course.title} - for: {self.course.modules.count()}"
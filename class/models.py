from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelStateFieldsCacheDescriptor
from django.db.models.fields.related import ForeignKey
# Create your models here.



class Teacher(models.Model):
    def __str__(self):
        return self.user.username

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

# TODO
# class Assignement(models.Model):
#     title = models.CharField(max_length=100)
#     description = models.TextField
#     due_date = models.da
#     added_date = 
#     grade = 

class Class(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, blank=True, null=True)

class ClassMaterialsChapter(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=100)
    className = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True, null=True, blank=True)


class ClassMaterialsModule(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=100)
    chapter = models.ForeignKey(ClassMaterialsChapter, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class ClassMaterials(models.Model):
    def __str__(self):
        return (self.chapter.name + ', ' + self.module.name)
    
    chapter = models.ForeignKey(ClassMaterialsChapter, on_delete=models.SET_NULL, null=True, blank=True)
    module = models.ForeignKey(ClassMaterialsModule, on_delete=models.SET_NULL, null=True, blank=True)
    className = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

class Files(models.Model):
    def __str__(self):
        if self.file_name == None:
            return ''
        return self.file_name
    class Meta:
        ordering = ['date_added']

    file_name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(blank=True)
    ClassMaterialsModule = models.ForeignKey(ClassMaterialsModule, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True, null=True, blank=True)


class Student(models.Model):
    def __str__(self):
        return self.user.username
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    className = models.ManyToManyField(Class, blank=True)

class Grade(models.Model):
    def __str__(self):
        return (self.studentName, '-', self.className, ': ', self.grade)
    
    grade = models.IntegerField(default=0)
    className = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
    studentName = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    
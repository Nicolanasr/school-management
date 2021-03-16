from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.base import ModelStateFieldsCacheDescriptor
from django.db.models.fields.related import ForeignKey
from django.db.models.signals import post_save
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
     

class Comments(models.Model):
    def all(self):
        qs = super(Comments, self).filter(parents=None)
        return qs
        
    class Meta:
        ordering = ['-date_added']

    author     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text       = models.TextField(max_length=5000, null=False, blank=False)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, blank=False, null=False)
    date_added = models.DateTimeField(auto_now_add=True)
    parent     = models.ForeignKey("self",on_delete=models.CASCADE, null=True, blank=True)

    def children(self): #replies
        return Comments.objects.filter(parent=self)
    
    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True




# assign each created user as a student
def create_user(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(username=instance)
        grp = Group.objects.get(name='Students')
        student = Student(user=user)
        student.save()
        student = Student.objects.get(user=user)
        grp.user_set.add(user)


post_save.connect(create_user, sender=User)
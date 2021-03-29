from datetime import datetime
from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.fields.json import HasKeyLookup
from django.db.models.fields.related import ForeignKey
from django.db.models.signals import post_save, m2m_changed, pre_save, pre_delete
from django.dispatch import receiver
from django.http.response import Http404, HttpResponse
# Create your models here.
import datetime



class Teacher(models.Model):
    def __str__(self):
        return self.user.username

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(default='noemail@email.com', null=True, blank=True)


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


class Times(models.Model):
    def __str__(self):
        return str(self.class_name) + ', ' + str(self.day) + ', ' + str(self.time)
    
    class Meta:
        ordering = ['-time']
    days = (
            ("Monday", "Monday"), 
            ("Tuesday", "Tuesday"), 
            ("Wednesday", "Wednesday"), 
            ("Thursday", "Thursday"), 
            ("Friday", "Friday"), 
            ("Saturday", "Saturday"), 
            ("Sunday", "Sunday"),
        )
    time_availble = (
        ("8:00 to 9:30", "8:00 to 9:30"),
        ("9:30 to 11:00", "9:30 to 11:00"),
        ("11:00 to 12:30", "11:00 to 12:30"),
        ("13:00 to 14:30", "13:00 to 14:30"),
        ("14:30 to 16:00", "14:30 to 16:00"),
    )

    @classmethod
    def get_all_days(self):
        return self.days


    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
    day = models.CharField(max_length=32, choices=days)
    time = models.CharField(max_length=32, default='00:00:00',  choices=time_availble)
    
    
    def filter_by_day(day):
        return Times.objects.filter(day=day)

class Assignment(models.Model):
    def __str__(self):
        return self.title
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    noted = models.BooleanField()
    points = models.IntegerField(blank=True, null=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    due_date = models.DateField()

class SubmittedAssignments(models.Model):
    stat = [
        ['awaiting submission', 'awaiting submission'],
        ['submitted', 'submitted'],
        ['graded', 'graded'],
        ['missed', 'missed'],
    ]
    def __str__(self):
        return ("by " + str(self.submitted_by) + " to: " + str(self.assignment.title))
    
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    files = models.FileField(upload_to='assignments_files/' , blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, default=stat[0], choices=stat)
    submitted_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
class Quiz(models.Model):
    def __str__(self):
        return f"{self.title}-{self.class_name}"
    
    title = models.CharField(max_length=120)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    #number_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="Quiz duration in minutes")
    points = models.IntegerField(default=100)
    created = models.DateTimeField(auto_now=True)
    max_time_to_take= models.DateTimeField(help_text="The maximum date and time the users will be able to take the quiz")

    def get_questions(self):
        return self.question_set.all()

class Question(models.Model):
    def __str__(self):
        return self.text

    text = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def get_answers(self):
        return self.answers_set.all()

class Answers(models.Model):
    def __str__(self):
        return f"question: {self.question.text}, answer: {self.text}, correct: {self.correct}"
    
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Results(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()
    submitted_date = models.DateTimeField(auto_now_add=True)

# TODO maybe add submitted answers


class Grade(models.Model):
    def __str__(self):
        return f"{self.studentName} {self.className} {self.grade}"
    
    grade = models.IntegerField(default=0)
    className = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
    studentName = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    number_of_total_grades = models.IntegerField(default=0)



# Create a teacher/student model when a user is added to one of these groups
@receiver(m2m_changed)
def add_model_when_grp(action, instance, pk_set, model, **kwargs):
    if model == Group:
        for pk in pk_set:
            id = pk
        if action == 'post_add':
            group = Group.objects.get(id=id)
            user = User.objects.get(username=instance)
            if str(group) == 'Teachers':
                tchr = Teacher.objects.filter(user=user)
                if len(tchr) != 0:
                    raise Http404('Teacher already exits!!')

                teacher = Teacher(user=user)
                teacher.save()
            elif str(group) == 'Students':
                std = Student.objects.filter(user=user)
                if len(std) != 0:
                    raise Http404('Student already exits!!')
                    
                student = Student(user=user)
                student.save()
        if action == 'post_remove':
            group = Group.objects.get(id=id)
            user = User.objects.get(username=instance)
            if str(group) == 'Teachers':
                Teacher.objects.filter(user=user).delete()
            elif str(group) == 'Students':
                Student.objects.filter(user=user).delete()

# Add the teacher/student to the corresponding group if teacher/student object is directly created
def add_to_grp_when_user(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(username=instance)
        try:
            grp = Group.objects.get(name='Students')
        except Group.DoesNotExist:
            grp = Group(name='Students')
            grp.save()
            grp = Group.objects.get(name='Students')
        student = Student.objects.get(user=user)
        grp.user_set.add(user)

def add_to_grp_when_user_teacher(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(username=instance)
        print(user)
        try:
            grp = Group.objects.get(name='Teachers')
        except Group.DoesNotExist:
            grp = Group(name='Teachers')
            grp.save()
            grp = Group.objects.get(name='Teachers')
        teacher = Teacher.objects.get(user=user)
        grp.user_set.add(user)


post_save.connect(add_to_grp_when_user_teacher, sender=Teacher)

# Remove the teacher/student to the corresponding group if teacher/student object is directly created
def remove_to_grp_when_user(sender, instance, **kwargs):
    user = User.objects.get(username=instance)
    try:
        grp = Group.objects.get(name='Students')
    except Group.DoesNotExist:
        grp = Group(name='Students')
        grp.save()
        grp = Group.objects.get(name='Students')
    student = Student.objects.get(user=user)
    grp.user_set.remove(user)


pre_delete.connect(remove_to_grp_when_user, sender=Student)

def remove_to_grp_when_user_teacher(sender, instance, **kwargs):
    user = User.objects.get(username=instance)
    try:
        grp = Group.objects.get(name='Teachers')
    except Group.DoesNotExist:
        grp = Group(name='Teachers')
        grp.save()
        grp = Group.objects.get(name='Teachers')
    teacher = Teacher.objects.get(user=user)
    grp.user_set.remove(user)


pre_delete.connect(remove_to_grp_when_user_teacher, sender=Teacher)

# assign each newly created account as a student
def create_user(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(username=instance)
        try:
            grp = Group.objects.get(name='Students')
        except Group.DoesNotExist:
            grp = Group(name='Students')
            grp.save()
            grp = Group.objects.get(name='Students')
        student = Student(user=user)
        student.save()
        student = Student.objects.get(user=user)
        grp.user_set.add(user)


post_save.connect(create_user, sender=User)


def create_times(sender, instance, **kwargs):
    try:
        Times.objects.get(time=instance.time, day=instance.day, class_name=instance.class_name)
        print('ok')
    except Times.DoesNotExist:
        pass
    else:
        raise Http404('This Time is already availble please check your schedules')
        

pre_save.connect(create_times, sender=Times)
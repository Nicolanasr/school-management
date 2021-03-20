from django.contrib import admin
from .models import Student, Teacher, Class, Grade, ClassMaterials, ClassMaterialsChapter, Files, ClassMaterialsModule, Comments, Times, Assignment, SubmittedAssignments
# Register your models here.

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Class)
admin.site.register(Grade)
admin.site.register(ClassMaterials)
admin.site.register(ClassMaterialsChapter)
admin.site.register(ClassMaterialsModule)
admin.site.register(Files)
admin.site.register(Comments)
admin.site.register(Times)
admin.site.register(Assignment)
admin.site.register(SubmittedAssignments)
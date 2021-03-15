from .models import Student, Teacher

# Create your views here.

def get_classes(request):
    is_teacher = False
    if request.user.is_authenticated:
        if(request.user.groups.filter(name='Teachers').exists()):
            is_teacher = True
        user_grp = request.user.groups.all()[0]
        # try:
        # except:
        #     user_grp = ''
        classes_list = []
        if str(user_grp) == 'Students':
            classes = Student.objects.get(user = request.user).className.all()
            for cl in classes:
                classes_list.append(cl)
        elif str(user_grp) == 'Teachers':
            teacher = Teacher.objects.get(user = request.user)
            classes = teacher.class_set.all()
            for cl in classes:
                classes_list.append(cl)
        # print(classes_list)
        
        return {'classes': classes_list, 'is_teacher': is_teacher}
    else:
        return {}
        
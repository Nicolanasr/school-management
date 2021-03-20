# from typing import Text
# from django.test import TestCase
# from .models import User, Comments, Student, Class, Teacher, Grade, ClassMaterials, ClassMaterialsChapter, ClassMaterialsModule, Files, Times



# class testModels(TestCase):

#     def test_model_str(self):
#         user = User.objects.create(username='uu', password="nicopl123_112")

#         teacher = Teacher.objects.create(user=user)
#         self.assertEqual(str(teacher), user.username)

#         class_name = Class.objects.create(name='classname')
#         self.assertEqual(str(class_name), 'classname')

#         class_mat_chap = ClassMaterialsChapter.objects.create(name='class_mat_chap')
#         self.assertEqual(str(class_mat_chap), 'class_mat_chap')

#         class_mat_mod = ClassMaterialsModule.objects.create(name='class_mat_mod')
#         self.assertEqual(str(class_mat_mod), 'class_mat_mod')

#         file = Files.objects.create(file_name=None)
#         self.assertEqual(str(file), '')
#         file = Files.objects.create(file_name='None')
#         self.assertEqual(str(file), 'None')

#         student = Student.objects.create(user=user)
#         self.assertEqual(str(student), user.username)

#         commets = Comments.objects.create(class_name=class_name, text='text')
#         print(commets.all())

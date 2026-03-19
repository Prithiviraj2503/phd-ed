from django import forms
from django.contrib.auth.models import User
from .models import Department, Course, CourseContent, Assignment, UserProfile


class CourseContentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        filename = obj.file.name.split('/')[-1] if obj.file else 'No file'
        return f"{obj.title} ({filename})"


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(
        choices=[('', 'Select role'), ('student', 'Student'), ('professor', 'Professor'), ('admin', 'Admin')],
        required=True
    )


class CreateUserForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='Select department'
    )

    def __init__(self, *args, **kwargs):
        self._role = kwargs.pop('role', 'student')
        super().__init__(*args, **kwargs)
        if self._role == 'student':
            self.fields['department'].required = True
            self.fields['department'].help_text = 'Student will see courses under this department.'
        elif self._role == 'professor':
            self.fields['department'].required = False
            self.fields['department'].help_text = 'Optional: assign the professor to a department.'


class CourseCreateForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    code = forms.CharField(max_length=50, required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    professor = forms.ModelChoiceField(
        queryset=None,
        required=True,
        help_text='Select a professor (users with professor role).'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prof_ids = UserProfile.objects.filter(role='professor').values_list('user_id', flat=True)
        self.fields['professor'].queryset = User.objects.filter(id__in=prof_ids)


class CourseContentForm(forms.Form):
    title = forms.CharField(max_length=200, required=True)
    file = forms.FileField(required=False, help_text='Optional: upload DOCX document')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False


class AssignmentCreateForm(forms.Form):
    title = forms.CharField(max_length=200, required=True)
    source_type = forms.ChoiceField(
        choices=[('docx', 'Course content Word file (auto-generate 20 MCQs via AI)'), ('excel', 'Upload Excel (qn, opt1, opt2, opt3, opt4, answer)')],
        widget=forms.RadioSelect,
        required=True
    )
    content_source = CourseContentChoiceField(
        queryset=CourseContent.objects.none(),
        required=False,
        empty_label='Select uploaded course content',
        label='Course content'
    )
    excel_file = forms.FileField(required=False, label='Excel file')

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course is not None:
            self.fields['content_source'].queryset = course.contents.exclude(file='').filter(file__isnull=False).order_by('title')

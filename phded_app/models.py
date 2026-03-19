from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code or self.name} - {self.name}"


class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_contents/%Y/%m/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    launched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    @property
    def is_launched(self):
        return self.launched_at is not None


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    # Score weight by difficulty (for weighted scoring)
    DIFFICULTY_WEIGHTS = {'easy': 1, 'medium': 2, 'hard': 3}

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    opt1 = models.CharField(max_length=500)
    opt2 = models.CharField(max_length=500)
    opt3 = models.CharField(max_length=500)
    opt4 = models.CharField(max_length=500)
    correct_answer = models.PositiveSmallIntegerField(help_text='1-4 for opt1-opt4')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question_text[:50] + '...' if len(self.question_text) > 50 else self.question_text

    @property
    def score_weight(self):
        return self.DIFFICULTY_WEIGHTS.get(self.difficulty, 1)


class StudentAssignmentAttempt(models.Model):
    """One attempt per student per assignment (re-submit not allowed)."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_attempts')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        unique_together = [['student', 'assignment']]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"

    @property
    def weighted_score(self):
        return sum(
            a.question.score_weight
            for a in self.answers.select_related('question')
            if a.selected_answer == a.question.correct_answer
        )

    @property
    def max_weighted_score(self):
        return sum(q.score_weight for q in self.assignment.questions.all())


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentAssignmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_answer = models.PositiveSmallIntegerField(help_text='1-4 for opt1-opt4')

    class Meta:
        unique_together = [['attempt', 'question']]

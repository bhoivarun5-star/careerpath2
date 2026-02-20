from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    CAREER_CHOICES = [
        ('software_engineer', 'Software Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('web_developer', 'Web Developer'),
        ('product_manager', 'Product Manager'),
        ('designer', 'UI/UX Designer'),
        ('devops', 'DevOps / Cloud Engineer'),
        ('cybersecurity', 'Cybersecurity Specialist'),
        ('ai_ml', 'AI / Machine Learning Engineer'),
        ('entrepreneur', 'Entrepreneur'),
        ('other', 'Other'),
    ]

    GOAL_CHOICES = [
        ('get_job', 'Land My First Job'),
        ('switch_career', 'Switch Careers'),
        ('freelance', 'Start Freelancing'),
        ('startup', 'Build a Startup'),
        ('upskill', 'Upskill & Grow'),
        ('research', 'Pursue Research / Academia'),
    ]

    INTEREST_CHOICES = [
        ('coding', 'Coding & Programming'),
        ('design', 'Design & Creativity'),
        ('data', 'Data & Analytics'),
        ('gaming', 'Gaming & Game Dev'),
        ('finance', 'Finance & Fintech'),
        ('health', 'Health & Biotech'),
        ('education', 'Education & E-Learning'),
        ('social_media', 'Social Media & Marketing'),
        ('robotics', 'Robotics & IoT'),
        ('blockchain', 'Blockchain & Web3'),
    ]

    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner (0–1 years)'),
        ('intermediate', 'Intermediate (2–4 years)'),
        ('experienced', 'Experienced (5–9 years)'),
        ('expert', 'Expert (10+ years)'),
    ]

    LEARNING_STYLE_CHOICES = [
        ('videos', 'Video Tutorials'),
        ('books', 'Books & Articles'),
        ('projects', 'Hands-on Projects'),
        ('courses', 'Structured Courses'),
        ('mentorship', 'Mentorship & Coaching'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Q1 – Career Path
    career_path = models.CharField(max_length=50, choices=CAREER_CHOICES, blank=True)

    # Q2 – Primary Goal
    primary_goal = models.CharField(max_length=50, choices=GOAL_CHOICES, blank=True)

    # Q3 – Interests (multiple, stored as comma-separated)
    interests = models.CharField(max_length=255, blank=True, help_text='Comma-separated list of interest keys')

    # Q4 – Experience Level
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True)

    # Q5 – Preferred Learning Style
    learning_style = models.CharField(max_length=30, choices=LEARNING_STYLE_CHOICES, blank=True)

    profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_interests_list(self):
        if self.interests:
            return [i.strip() for i in self.interests.split(',')]
        return []

    def get_interests_display_list(self):
        interest_map = dict(self.INTEREST_CHOICES)
        return [interest_map.get(i, i) for i in self.get_interests_list()]


class Roadmap(models.Model):
    """
    Stores a generated learning roadmap for a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    role = models.CharField(max_length=100)  # e.g., "AI / ML Engineer"
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')  # active, completed

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def get_progress(self):
        """Calculate percentage of completed tasks."""
        total_tasks = RoadmapTask.objects.filter(phase__roadmap=self).count()
        if total_tasks == 0:
            return 0
        completed_tasks = RoadmapTask.objects.filter(phase__roadmap=self, is_completed=True).count()
        return int((completed_tasks / total_tasks) * 100)


class RoadmapPhase(models.Model):
    """
    A phase within a roadmap (e.g., "Phase 1: Beginner").
    """
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='phases')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.roadmap.role} - {self.title}"


class RoadmapTask(models.Model):
    """
    A specific learning task within a phase.
    """
    phase = models.ForeignKey(RoadmapPhase, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)  # Video, Course, Book, Article
    resource_url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title




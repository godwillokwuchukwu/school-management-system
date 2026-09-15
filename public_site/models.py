from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class SchoolProfile(models.Model):
    """
    Singleton-ish record backing the public homepage/about content (Sections
    11-12). Enforced as a singleton via `pk=1` in `save()` rather than a
    hard DB constraint, since Django has no first-class "only one row" type
    -- this mirrors how most Django singleton-config patterns are done.
    """

    name = models.CharField(max_length=200, default="Riverside Academy")
    tagline = models.CharField(max_length=200, default="Learning with purpose")
    hero_heading = models.CharField(
        max_length=200, default="Inspiring excellence, building futures."
    )
    hero_subtext = models.TextField(
        default="Where every learner is seen, challenged, and prepared to make a meaningful difference in the world."
    )
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    history = models.TextField(blank=True)
    core_values = models.TextField(blank=True, help_text="One value per line.")

    founded_year = models.PositiveIntegerField(null=True, blank=True)
    total_students = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    graduation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)
    office_hours = models.CharField(max_length=200, blank=True)
    map_embed_url = models.URLField(blank=True)

    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School profile"
        verbose_name_plural = "School profile"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton row is never deleted through the app

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def years_of_excellence(self):
        if not self.founded_year:
            return None
        from datetime import date

        return date.today().year - self.founded_year

    def __str__(self):
        return self.name


class SlugModel(models.Model):
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        abstract = True

    def _slug_source(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self._slug_source())[:200]
            slug = base
            n = 1
            model = self.__class__
            while model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)


class NewsCategory(models.TextChoices):
    ANNOUNCEMENT = "announcement", "Announcement"
    ACADEMICS = "academics", "Academics"
    ACHIEVEMENT = "achievement", "Achievement"
    COMMUNITY = "community", "Community"
    ADMISSIONS = "admissions", "Admissions"


class NewsArticle(SlugModel):
    title = models.CharField(max_length=220)
    excerpt = models.CharField(max_length=400, blank=True)
    body = models.TextField()
    category = models.CharField(
        max_length=20, choices=NewsCategory.choices, default=NewsCategory.ANNOUNCEMENT
    )
    cover_image_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["is_published", "-published_at"])]

    def __str__(self):
        return self.title


class Event(SlugModel):
    title = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    cover_image_url = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    registration_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]
        indexes = [models.Index(fields=["is_published", "starts_at"])]

    def __str__(self):
        return self.title


class ProgramCategory(models.TextChoices):
    SPORTS = "sports", "Sports"
    MUSIC = "music", "Music"
    ARTS = "arts", "Arts"
    STEM = "stem", "STEM"
    DEBATE = "debate", "Debate"
    CLUBS = "clubs", "Clubs"
    LEADERSHIP = "leadership", "Leadership"
    COMMUNITY_SERVICE = "community_service", "Community Service"


class Program(SlugModel):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=ProgramCategory.choices)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def _slug_source(self):
        return self.name

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    class Role(models.TextChoices):
        PARENT = "parent", "Parent"
        STUDENT = "student", "Student"
        ALUMNUS = "alumnus", "Alumnus"

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices)
    quote = models.TextField()
    photo_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.role})"


class FAQCategory(models.TextChoices):
    GENERAL = "general", "General"
    ADMISSIONS = "admissions", "Admissions"
    ACADEMICS = "academics", "Academics"
    PAYMENTS = "payments", "Payments"


class FAQItem(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(
        max_length=20, choices=FAQCategory.choices, default=FAQCategory.GENERAL
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "order", "id"]

    def __str__(self):
        return self.question


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full Time"
    PART_TIME = "part_time", "Part Time"
    CONTRACT = "contract", "Contract"


class JobPosting(SlugModel):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=120, blank=True)
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME
    )
    location = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def _slug_source(self):
        return self.title

    def __str__(self):
        return self.title


def resume_upload_path(instance, filename):
    return f"careers/resumes/{instance.reference}/{filename}"


class JobApplication(models.Model):
    """
    Lightweight lead-capture for a public job posting. NOTE: this is not
    yet the full employment/recruitment workflow described in the master
    prompt (Section 22) -- there is no HR review pipeline, interview
    stages, or account provisioning wired to this model yet. That belongs
    to a dedicated `recruitment` app (see GAP_ANALYSIS_AND_ROADMAP.md,
    item #4). For now this simply records the application so an admin can
    follow up manually from Django admin.
    """

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REVIEWED = "reviewed", "Reviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"

    reference = models.CharField(max_length=20, unique=True, editable=False)
    job = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="applications"
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    qualifications = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to=resume_upload_path)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUBMITTED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _generate_reference("EMP")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.full_name}"


class AdmissionEnquiry(models.Model):
    """
    Preliminary admissions interest form shown on the public /admissions
    page. This intentionally captures a lead only -- it does NOT create an
    applicant account, does not accept documents, and does not accept
    payment. The full multi-step application (Section 19-21) belongs to a
    dedicated `admissions` app (see GAP_ANALYSIS_AND_ROADMAP.md, item #3)
    which will supersede this model's public-facing role once built.
    """

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CONVERTED = "converted", "Converted to application"
        CLOSED = "closed", "Closed"

    reference = models.CharField(max_length=20, unique=True, editable=False)
    student_name = models.CharField(max_length=200)
    student_dob = models.DateField(null=True, blank=True)
    class_applying_for = models.CharField(max_length=100)
    academic_session = models.CharField(max_length=20, blank=True)
    parent_name = models.CharField(max_length=200)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=30)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Admission enquiries"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _generate_reference("BFA")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.student_name}"


class ContactTopic(models.TextChoices):
    GENERAL = "general", "General Enquiry"
    ADMISSIONS = "admissions", "Admissions"
    CAREERS = "careers", "Careers"
    SUPPORT = "support", "Parent/Student Support"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    topic = models.CharField(
        max_length=20, choices=ContactTopic.choices, default=ContactTopic.GENERAL
    )
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or self.topic}"


def _generate_reference(prefix):
    """
    BFA-2026-000184 style reference (Section 19). Sequential per year,
    computed from existing row counts -- acceptable at this scale; a
    dedicated counter table would be the next step if concurrent writes
    ever become high enough to risk a collision window.
    """
    from datetime import date

    year = date.today().year
    if prefix == "BFA":
        count = AdmissionEnquiry.objects.filter(
            reference__startswith=f"{prefix}-{year}"
        ).count()
    else:
        count = JobApplication.objects.filter(
            reference__startswith=f"{prefix}-{year}"
        ).count()
    return f"{prefix}-{year}-{count + 1:06d}"

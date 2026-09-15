from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Role
from academics.models import Class, Subject
from students.models import Student
from public_site.models import (
    EmploymentType,
    Event,
    FAQCategory,
    FAQItem,
    JobPosting,
    NewsArticle,
    NewsCategory,
    Program,
    ProgramCategory,
    SchoolProfile,
    Testimonial,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed local dev database with users, classes, and complete public website content."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Accounts & Core Academic Records
        admin, created = User.objects.get_or_create(
            username="admin@school.example.com",
            defaults={
                "email": "admin@school.example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("ChangeMe123!")
            admin.save()
            admin.profile.role = Role.ADMIN
            admin.profile.save(update_fields=["role"])

        teacher, created = User.objects.get_or_create(
            username="teacher@school.example.com",
            defaults={
                "email": "teacher@school.example.com",
                "first_name": "Tara",
                "last_name": "Teacher",
            },
        )
        if created:
            teacher.set_password("ChangeMe123!")
            teacher.save()
            teacher.profile.role = Role.TEACHER
            teacher.profile.save(update_fields=["role"])

        student_user, created = User.objects.get_or_create(
            username="student@school.example.com",
            defaults={
                "email": "student@school.example.com",
                "first_name": "Sam",
                "last_name": "Student",
            },
        )
        if created:
            student_user.set_password("ChangeMe123!")
            student_user.save()
            student_user.profile.role = Role.STUDENT
            student_user.profile.save(update_fields=["role"])
            Student.objects.get_or_create(
                profile=student_user.profile,
                defaults={"admission_number": "ADM-0001", "dob": "2012-01-01"},
            )

        subject, _ = Subject.objects.get_or_create(
            code="MATH101", defaults={"name": "Mathematics"}
        )
        school_class, _ = Class.objects.get_or_create(
            code="G8B",
            academic_year="2025-2026",
            defaults={"name": "Grade 8B", "class_teacher": teacher},
        )
        school_class.subjects.add(subject)

        # 2. School Profile
        profile = SchoolProfile.load()
        profile.name = "Riverside Academy"
        profile.tagline = "Inspiring Minds, Shaping Tomorrow"
        profile.hero_heading = "Where Ambition Meets Opportunity."
        profile.hero_subtext = (
            "A vibrant, co-educational learning community dedicated to academic rigor, "
            "character development, and holistic success for learners aged 5 through 18."
        )
        profile.founded_year = 1998
        profile.total_students = 1250
        profile.total_teachers = 84
        profile.graduation_rate = 99.4
        profile.address = "Plot 14, Admiralty Way, Lekki Phase 1, Lagos, Nigeria"
        profile.phone = "+234 1 234 5678"
        profile.email = "hello@riversideacademy.edu"
        profile.emergency_phone = "+234 800 748 377"
        profile.office_hours = "Monday – Friday, 7:30am – 4:30pm"
        profile.map_embed_url = "https://maps.google.com/maps?q=Lekki+Phase+1+Lagos+Nigeria&t=&z=14&ie=UTF8&iwloc=&output=embed"
        profile.facebook_url = "https://facebook.com/riversideacademy"
        profile.twitter_url = "https://twitter.com/riversideacademy"
        profile.instagram_url = "https://instagram.com/riversideacademy"
        profile.linkedin_url = "https://linkedin.com/company/riversideacademy"
        profile.mission = (
            "To foster intellectual curiosity, moral courage, and compassionate leadership "
            "in every student through an inspiring, world-class academic journey."
        )
        profile.vision = (
            "To be Africa's leading preparatory academy, empowering innovative thinkers "
            "who shape a sustainable, globally connected future."
        )
        profile.history = (
            "Founded in 1998 with an initial class of 45 students, Riverside Academy has grown "
            "into a premier institution recognized for academic excellence, state-of-the-art facilities, "
            "and national championship robotics and sports teams."
        )
        profile.core_values = "Integrity\nIntellectual Curiosity\nEmpathy & Inclusion\nResilience & Grit\nExcellence in Service"
        profile.save()

        now = timezone.now()

        # 3. News Articles
        news_items = [
            {
                "title": "National Robotics Olympiad: Riverside Academy Wins First Place",
                "excerpt": "Our senior high robotics team triumphed over 40 schools to take the gold medal in autonomous engineering.",
                "body": (
                    "Riverside Academy's robotics engineering team, 'The CyberLions', clinched the gold medal "
                    "at the 2026 National STEM and Robotics Olympiad held this weekend.\n\n"
                    "Competing against 40 leading schools from across the country, our students designed and "
                    "programmed an autonomous navigation drone and rescue rover. We congratulate their mentor, "
                    "Mr. Michael Okoro, and the entire technology faculty for their dedicated coaching."
                ),
                "category": NewsCategory.ACHIEVEMENT,
                "cover_image_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80",
                "is_featured": True,
                "published_at": now - timedelta(days=2),
            },
            {
                "title": "2026/2027 Academic Year Admissions Now Formally Open",
                "excerpt": "Prospective parents and guardians can now submit applications online for Primary, Secondary, and Senior Secondary.",
                "body": (
                    "The admissions committee has officially opened the application window for the 2026/2027 academic session.\n\n"
                    "Interested families are invited to explore our curriculum tracks, schedule a campus visit, "
                    "or submit an online application through the admissions portal."
                ),
                "category": NewsCategory.ANNOUNCEMENT,
                "cover_image_url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
                "is_featured": True,
                "published_at": now - timedelta(days=5),
            },
            {
                "title": "New State-of-the-Art Science & Innovation Wing Unveiled",
                "excerpt": "Our campus expansion includes modern chemistry, physics, and bio-informatics laboratories.",
                "body": (
                    "Riverside Academy has formally commissioned its new 4-storey Science & Innovation Wing. "
                    "Equipped with interactive smart laboratories, 3D printing suites, and solar-powered research stations, "
                    "the facility will empower students to conduct collegiate-level research from Grade 9 onwards."
                ),
                "category": NewsCategory.ACADEMICS,
                "cover_image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80",
                "is_featured": False,
                "published_at": now - timedelta(days=12),
            },
            {
                "title": "Annual Cultural Day & Performing Arts Showcase",
                "excerpt": "A celebration of diversity, music, traditional dances, and student culinary creations.",
                "body": (
                    "Our annual Cultural Day brought together over 1,500 parents, students, and educators in a vibrant "
                    "celebration of heritage and creative expression. The afternoon featured original choral compositions, "
                    "theatrical plays, and traditional fashion showcases."
                ),
                "category": NewsCategory.COMMUNITY,
                "cover_image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
                "is_featured": False,
                "published_at": now - timedelta(days=18),
            },
            {
                "title": "Merit Scholarship Opportunities for Exceptional STEM Candidates",
                "excerpt": "Full and partial tuition awards available for high-achieving Grade 10 applicants.",
                "body": (
                    "Riverside Academy is proud to announce the 2026 Riverside Scholars Program. "
                    "Up to ten full-tuition scholarships will be awarded to exceptional students demonstrating academic "
                    "distinction and leadership aptitude."
                ),
                "category": NewsCategory.ADMISSIONS,
                "cover_image_url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?auto=format&fit=crop&w=800&q=80",
                "is_featured": False,
                "published_at": now - timedelta(days=24),
            },
        ]
        for data in news_items:
            NewsArticle.objects.get_or_create(title=data["title"], defaults=data)

        # 4. Events
        event_items = [
            {
                "title": "Open Campus Experience & Guided Tours",
                "description": "Meet faculty department heads, tour classroom facilities and labs, and attend our admissions briefing.",
                "category": "Admissions",
                "cover_image_url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
                "location": "Main Auditorium & Campus Quad",
                "starts_at": now + timedelta(days=7, hours=3),
                "ends_at": now + timedelta(days=7, hours=7),
                "registration_url": "https://riversideacademy.edu/admissions/apply",
            },
            {
                "title": "Inter-House Athletics Championship & Track Meet",
                "description": "The culminating annual sports day featuring sprint relays, high jump, gymnastics, and parent races.",
                "category": "Athletics",
                "cover_image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
                "location": "Riverside Sports Complex",
                "starts_at": now + timedelta(days=15, hours=2),
                "ends_at": now + timedelta(days=15, hours=8),
            },
            {
                "title": "Junior & Senior Science Fair 2026",
                "description": "Student-led investigations in robotics, sustainable energy, organic chemistry, and computer algorithms.",
                "category": "Academic",
                "cover_image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
                "location": "Science & Innovation Center",
                "starts_at": now + timedelta(days=25, hours=4),
                "ends_at": now + timedelta(days=25, hours=9),
            },
            {
                "title": "Alumni Mentorship Roundtable: Pathways to Global Universities",
                "description": "Recent graduates currently attending Oxford, MIT, and Toronto return to share advice with Grade 11 & 12 students.",
                "category": "Mentorship",
                "cover_image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
                "location": "Collegiate Library Hall",
                "starts_at": now - timedelta(days=8, hours=2),
                "ends_at": now - timedelta(days=8, hours=5),
            },
        ]
        for data in event_items:
            Event.objects.get_or_create(title=data["title"], defaults=data)

        # 5. Programs
        programs_data = [
            {
                "name": "Robotics & Artificial Intelligence Lab",
                "category": ProgramCategory.STEM,
                "summary": "Hands-on engineering, micro-controllers, drone navigation, and machine learning principles.",
                "description": "Students work in competitive teams building autonomous machines, solving real-world mechanical problems.",
                "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80",
                "order": 1,
            },
            {
                "name": "Symphonic Orchestra & Music Conservatory",
                "category": ProgramCategory.MUSIC,
                "summary": "String ensembles, brass, woodwinds, and classical vocal training with certified instructors.",
                "description": "Providing personalized musical education from beginner solfege to national concert performances.",
                "image_url": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=800&q=80",
                "order": 2,
            },
            {
                "name": "Elite Swimming & Water Polo Academy",
                "category": ProgramCategory.SPORTS,
                "summary": "Olympic-length heated swimming pool and certified coaching for all swimming competencies.",
                "description": "Focusing on stroke technique, cardiovascular fitness, and inter-school championship competitions.",
                "image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=800&q=80",
                "order": 3,
            },
            {
                "name": "Parliamentary Debate & Model United Nations",
                "category": ProgramCategory.DEBATE,
                "summary": "Honing rhetorical analysis, international diplomacy, policy drafting, and confident public speech.",
                "description": "Delegates participate in national conferences and sharpen structured arguments on global affairs.",
                "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=800&q=80",
                "order": 4,
            },
            {
                "name": "Studio Arts, Ceramics & Digital Media",
                "category": ProgramCategory.ARTS,
                "summary": "Oil painting, pottery wheel throwing, digital illustration, and portfolio curation.",
                "description": "Encouraging authentic creative voices with regular campus gallery openings and exhibitions.",
                "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=800&q=80",
                "order": 5,
            },
            {
                "name": "Community Leadership & Civic Service",
                "category": ProgramCategory.LEADERSHIP,
                "summary": "Student-directed outreach initiatives supporting local literacy drives and environmental conservation.",
                "description": "Nurturing socially conscious citizens through meaningful, structured community partnerships.",
                "image_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=800&q=80",
                "order": 6,
            },
        ]
        for data in programs_data:
            Program.objects.get_or_create(name=data["name"], defaults=data)

        # 6. Testimonials
        testimonials_data = [
            {
                "name": "Mrs. Ngozi Adeleke",
                "role": Testimonial.Role.PARENT,
                "quote": "Riverside Academy transformed my daughter's confidence. Her teachers nurtured both her love for mathematics and her passion for public speaking.",
                "photo_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
                "order": 1,
            },
            {
                "name": "David Kalu",
                "role": Testimonial.Role.STUDENT,
                "quote": "The robotics lab and competitive debate program gave me skills I never thought possible in high school. Teachers treat us as capable problem solvers.",
                "photo_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
                "order": 2,
            },
            {
                "name": "Dr. Amina Bello",
                "role": Testimonial.Role.PARENT,
                "quote": "The pastoral care and academic rigor are unmatched. Both my children have grown into empathetic, ambitious young leaders.",
                "photo_url": "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?auto=format&fit=crop&w=300&q=80",
                "order": 3,
            },
            {
                "name": "Tunde Williams",
                "role": Testimonial.Role.ALUMNUS,
                "quote": "My time at Riverside laid the bedrock for my engineering degree at Imperial College. The discipline and intellectual ambition stay with you for life.",
                "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
                "order": 4,
            },
        ]
        for data in testimonials_data:
            Testimonial.objects.get_or_create(name=data["name"], defaults=data)

        # 7. FAQs
        faq_data = [
            {
                "question": "What are the standard school operating hours?",
                "answer": "Classes begin promptly at 8:00am and conclude at 3:15pm Monday through Friday. Extracurricular clubs and athletic practices run until 4:45pm.",
                "category": FAQCategory.GENERAL,
                "order": 1,
            },
            {
                "question": "How do I apply for student admission?",
                "answer": "Applications can be submitted online via our Admissions portal. After creating an applicant account, complete the student details form, upload required previous academic transcripts, and pay the evaluation fee.",
                "category": FAQCategory.ADMISSIONS,
                "order": 2,
            },
            {
                "question": "What curriculum framework is taught at Riverside Academy?",
                "answer": "We offer a blended international and national curriculum, integrating rigorous Cambridge IGCSE / British guidelines with the Nigerian National Curriculum, leading into Cambridge A-Levels and WASSCE certification.",
                "category": FAQCategory.ACADEMICS,
                "order": 3,
            },
            {
                "question": "Are payment plans or installment options available for school fees?",
                "answer": "Yes. While fees are invoiced on a per-term basis, parents may request a structured termly installment schedule through the school bursary prior to term commencement.",
                "category": FAQCategory.PAYMENTS,
                "order": 4,
            },
            {
                "question": "Is school bus transportation available across the city?",
                "answer": "Yes, Riverside operates modern, air-conditioned school buses equipped with GPS tracking and trained chaperones covering major residential zones.",
                "category": FAQCategory.GENERAL,
                "order": 5,
            },
            {
                "question": "What is the average teacher-to-student class ratio?",
                "answer": "Our maximum class size is capped at 22 students in Primary and 24 in Secondary, ensuring every learner receives individualized mentorship and attention.",
                "category": FAQCategory.ACADEMICS,
                "order": 6,
            },
        ]
        for data in faq_data:
            FAQItem.objects.get_or_create(question=data["question"], defaults=data)

        # 8. Job Postings
        jobs_data = [
            {
                "title": "Head of Science Faculty & Advanced Physics Teacher",
                "department": "Academics",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Lekki Campus, Lagos",
                "description": "Lead a team of 12 dedicated science educators and teach Cambridge A-Level and Senior Secondary Physics.",
                "requirements": "Minimum Bachelor's degree in Physics or Education with 5+ years of demonstrable classroom teaching in an international curriculum.",
                "application_deadline": (now + timedelta(days=45)).date(),
            },
            {
                "title": "Robotics & Computer Science Instructor",
                "department": "Technology & Innovation",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Lekki Campus, Lagos",
                "description": "Inspire students from Grade 5 through 12 in Python coding, algorithm design, Arduino, and robotics.",
                "requirements": "Degree in Computer Science, Software Engineering, or related technical field with passion for secondary STEM education.",
                "application_deadline": (now + timedelta(days=30)).date(),
            },
            {
                "title": "Lead College Counselor & University Placement Advisor",
                "department": "Student Welfare",
                "employment_type": EmploymentType.FULL_TIME,
                "location": "Lekki Campus, Lagos",
                "description": "Guide Grade 10-12 students through international university selection, personal statements, and standardized admissions tests.",
                "requirements": "Experience in UK UCAS, US Common App, and Canadian university admissions processes with strong communication skills.",
                "application_deadline": (now + timedelta(days=60)).date(),
            },
        ]
        for data in jobs_data:
            JobPosting.objects.get_or_create(title=data["title"], defaults=data)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded successfully:\n"
                "  - Users: admin@school.example.com, teacher@school.example.com, student@school.example.com (pw: ChangeMe123!)\n"
                "  - School Profile (Riverside Academy)\n"
                "  - 5 News Articles\n"
                "  - 4 Events\n"
                "  - 6 Programs\n"
                "  - 4 Testimonials\n"
                "  - 6 FAQs\n"
                "  - 3 Job Postings"
            )
        )

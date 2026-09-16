from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import AdminNotification, AdminNotificationType, AuditLog, Role
from admissions.models import AdmissionApplication, ApplicationStatus
from students.models import Student
from services import admission_service

User = get_user_model()


class StudentPortalAuthTests(APITestCase):
    def test_student_registration_success(self):
        payload = {
            "first_name": "Mary",
            "last_name": "Smith",
            "email": "mary.smith@example.com",
            "phone": "+2348012345678",
            "dob": "2009-04-12",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
            "student_id": "RVS-2026-050",
            "agree_terms": True,
        }
        resp = self.client.post("/api/auth/student/register/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("Account created successfully", resp.data["message"])

        user = User.objects.get(email="mary.smith@example.com")
        self.assertEqual(user.profile.role, Role.STUDENT)
        self.assertEqual(user.profile.student_id, "RVS-2026-050")
        self.assertIsNotNone(user.profile.email_verification_token)

        notif = AdminNotification.objects.filter(
            notification_type=AdminNotificationType.STUDENT_REGISTERED,
            user=user,
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("Mary Smith", notif.message)

    def test_student_registration_password_mismatch(self):
        payload = {
            "first_name": "Mary",
            "last_name": "Smith",
            "email": "mary2@example.com",
            "phone": "+2348012345678",
            "dob": "2009-04-12",
            "password": "StrongPassword123!",
            "confirm_password": "DifferentPassword123!",
            "agree_terms": True,
        }
        resp = self.client.post("/api/auth/student/register/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("confirm_password", resp.data)

    def test_verify_email_success(self):
        user = User.objects.create_user(
            username="verify_test@student.edu",
            email="verify_test@student.edu",
            password="Password123!",
        )
        token = "valid-verification-token-xyz"
        user.profile.email_verification_token = token
        user.profile.email_verification_token_expires = timezone.now() + timedelta(
            hours=24
        )
        user.profile.save()

        resp = self.client.get(f"/api/auth/verify-email/{token}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "success")

        user.profile.refresh_from_db()
        self.assertIsNotNone(user.profile.email_verified_at)
        self.assertIsNone(user.profile.email_verification_token)

    def test_verify_email_expired(self):
        user = User.objects.create_user(
            username="expired_test@student.edu",
            email="expired_test@student.edu",
            password="Password123!",
        )
        token = "expired-token-123"
        user.profile.email_verification_token = token
        user.profile.email_verification_token_expires = timezone.now() - timedelta(
            hours=2
        )
        user.profile.save()

        resp = self.client.get(f"/api/auth/verify-email/{token}/")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["status"], "expired")

    def test_login_by_email(self):
        user = User.objects.create_user(
            username="login_test@student.edu",
            email="login_test@student.edu",
            password="StudentSecurePass123!",
        )
        user.profile.role = Role.STUDENT
        user.profile.save()

        payload = {
            "username": "login_test@student.edu",
            "password": "StudentSecurePass123!",
        }
        resp = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertEqual(resp.data["role"], Role.STUDENT)

        self.assertTrue(
            AuditLog.objects.filter(actor=user, action="auth.login").exists()
        )

    def test_login_by_student_id(self):
        user = User.objects.create_user(
            username="studentid_test@student.edu",
            email="studentid_test@student.edu",
            password="StudentSecurePass123!",
        )
        user.profile.role = Role.STUDENT
        user.profile.student_id = "RVS-2026-099"
        user.profile.save()

        Student.objects.create(
            profile=user.profile,
            admission_number="RVS-2026-099",
            dob=date(2008, 5, 15),
        )

        payload = {
            "username": "RVS-2026-099",  # Login by student ID / admission number
            "password": "StudentSecurePass123!",
        }
        resp = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertEqual(resp.data["role"], Role.STUDENT)

    def test_invalid_credentials_returns_generic_error(self):
        payload = {
            "username": "nonexistent@riverside.edu",
            "password": "WrongPassword123!",
        }
        resp = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_move_to_payment_service(self):
        admin_user = User.objects.create_superuser(
            username="admin_move_pay@riverside.edu",
            email="admin_move_pay@riverside.edu",
            password="AdminPassword123!",
        )
        admin_user.profile.role = Role.ADMIN
        admin_user.profile.save()

        applicant = User.objects.create_user(
            username="applicant_pay@example.com",
            email="applicant_pay@example.com",
            password="AppPassword123!",
        )
        app = AdmissionApplication.objects.create(
            applicant=applicant,
            student_first_name="David",
            student_last_name="Johnson",
            student_dob=date(2011, 2, 20),
            guardian_full_name="Peter Johnson",
            guardian_email="peter.johnson@example.com",
            guardian_phone="+2348099887766",
            class_applying_for="Grade 7",
            academic_session="2026/2027",
            status=ApplicationStatus.SUBMITTED,
        )

        updated_app = admission_service.move_to_payment(
            application=app,
            admin_user=admin_user,
            amount=150000.0,
            notes="Ready for tuition deposit",
        )

        self.assertEqual(updated_app.status, ApplicationStatus.PAYMENT_PENDING)
        self.assertTrue(
            AuditLog.objects.filter(action="admission.move_to_payment").exists()
        )

    def test_student_login_form(self):
        from accounts.forms import StudentLoginForm
        form = StudentLoginForm(data={"login_identifier": "student@example.com", "password": "Pass12345!", "remember_me": True})
        self.assertTrue(form.is_valid())

    def test_student_registration_form_validation(self):
        from accounts.forms import StudentRegistrationForm
        valid_data = {
            "first_name": "Form",
            "last_name": "Student",
            "email": "form.student@example.com",
            "phone": "+2348011223344",
            "dob": "2008-05-15",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
            "student_id": "STU-FORM-01",
            "agree_terms": True,
        }
        form = StudentRegistrationForm(data=valid_data)
        self.assertTrue(form.is_valid())

        # Test password mismatch
        mismatch_data = valid_data.copy()
        mismatch_data["confirm_password"] = "DifferentPassword123!"
        mismatch_form = StudentRegistrationForm(data=mismatch_data)
        self.assertFalse(mismatch_form.is_valid())
        self.assertIn("confirm_password", mismatch_form.errors)

        # Test weak password
        weak_data = valid_data.copy()
        weak_data["password"] = "short"
        weak_data["confirm_password"] = "short"
        weak_form = StudentRegistrationForm(data=weak_data)
        self.assertFalse(weak_form.is_valid())
        self.assertIn("password", weak_form.errors)

        # Test duplicate email
        User.objects.create_user(username="dup@example.com", email="dup@example.com", password="Pass12345!")
        dup_data = valid_data.copy()
        dup_data["email"] = "dup@example.com"
        dup_form = StudentRegistrationForm(data=dup_data)
        self.assertFalse(dup_form.is_valid())
        self.assertIn("email", dup_form.errors)

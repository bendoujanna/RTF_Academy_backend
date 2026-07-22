from django.core.management.base import BaseCommand
from users.models import UserProfile
from courses.models import Course

class Command(BaseCommand):
    help = 'Safely removes only the RTF Academy seed data without touching real accounts.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Targeting seed data for removal...")

        # 1. Delete the seeded courses (This cascades and deletes Modules, Lessons, Quizzes, Questions, etc.)
        courses_deleted, _ = Course.objects.filter(
            title__in=["English Language Essentials"]
        ).delete()

        # 2. Delete the seeded users (This cascades and deletes Enrollments, Attempts, Certificates, etc.)
        users_deleted, _ = UserProfile.objects.filter(
            email__in=["admin@rtfacademy.com", "student@rtfacademy.com"]
        ).delete()

        self.stdout.write(self.style.SUCCESS(f'Success! Deleted {courses_deleted} course(s) and {users_deleted} user(s), plus all connected data.'))
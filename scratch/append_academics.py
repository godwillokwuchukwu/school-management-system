with open(
    r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\academics\models.py",
    "a",
    encoding="utf-8",
) as f:
    f.write('''\n
class ClassSchedule(models.Model):
    """
    Timetable entry representing a specific subject scheduled for a class.
    """
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.IntegerField(choices=[
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.school_class} - {self.subject} ({self.get_day_of_week_display()} {self.start_time})"
''')

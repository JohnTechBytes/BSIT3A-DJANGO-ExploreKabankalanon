from django.db import models
from django.conf import settings


class CityInformation(models.Model):
    class InfoType(models.TextChoices):
        ATTRACTION = "attraction", "Attraction"
        FOOD = "food", "Food & Dining"
        STAY = "stay", "Stays & Accommodations"
        EVENT = "event", "Event / Festival"
        TRANSPORT = "transport", "Transport Guide"

    city = models.ForeignKey(
        "cities.City",
        on_delete=models.CASCADE,
        related_name="city_information",
    )
    title = models.CharField(max_length=255)
    info_type = models.CharField(
        max_length=20,
        choices=InfoType.choices,
        default=InfoType.ATTRACTION,
        db_index=True,
    )
    description = models.TextField()
    thumbnail_url = models.URLField(blank=True)
    photo_credit = models.CharField(
        max_length=500,
        blank=True,
        help_text=(
            "Credit line for the thumbnail, e.g. "
            "'Photo: Juan Dela Cruz / Wikimedia Commons (CC BY-SA 4.0)'."
        ),
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Only published entries are visible on the public City "
            "Information page."
        ),
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_city_information"
        verbose_name_plural = "City Information"
        ordering = ["city", "info_type", "order"]

    def __str__(self):
        return f"{self.city.name} - [{self.get_info_type_display()}] {self.title}"


class SusResponse(models.Model):
    """System Usability Scale (SUS) survey responses (1-5 scale for 10 questions)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sus_responses",
    )
    q1 = models.PositiveSmallIntegerField(help_text="I think that I would like to use this system frequently.")
    q2 = models.PositiveSmallIntegerField(help_text="I found the system unnecessarily complex.")
    q3 = models.PositiveSmallIntegerField(help_text="I thought the system was easy to use.")
    q4 = models.PositiveSmallIntegerField(help_text="I think that I would need the support of a technical person to be able to use this system.")
    q5 = models.PositiveSmallIntegerField(help_text="I found the various functions in this system were well integrated.")
    q6 = models.PositiveSmallIntegerField(help_text="I thought there was too much inconsistency in this system.")
    q7 = models.PositiveSmallIntegerField(help_text="I would imagine that most people would learn to use this system very quickly.")
    q8 = models.PositiveSmallIntegerField(help_text="I found the system very cumbersome to use.")
    q9 = models.PositiveSmallIntegerField(help_text="I felt very confident using the system.")
    q10 = models.PositiveSmallIntegerField(help_text="I needed to learn a lot of things before I could get going with this system.")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_sus_responses"

    def compute_score(self):
        """Standard SUS score calculation (0 - 100)"""
        # Odd items (1,3,5,7,9): score contribution is position - 1
        # Even items (2,4,6,8,10): score contribution is 5 - position
        odd_sum = (self.q1 - 1) + (self.q3 - 1) + (self.q5 - 1) + (self.q7 - 1) + (self.q9 - 1)
        even_sum = (5 - self.q2) + (5 - self.q4) + (5 - self.q6) + (5 - self.q8) + (5 - self.q10)
        self.score = (odd_sum + even_sum) * 2.5
        return self.score


class RecommendationRating(models.Model):
    class RatingChoices(models.TextChoices):
        RELEVANT = "relevant", "Relevant"
        PARTIAL = "partial", "Partially Relevant"
        IRRELEVANT = "irrelevant", "Irrelevant"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    query_text = models.CharField(max_length=255)
    place = models.ForeignKey(
        "places.Place",
        on_delete=models.CASCADE,
        related_name="recommendation_ratings",
    )
    rating = models.CharField(
        max_length=20,
        choices=RatingChoices.choices,
        default=RatingChoices.RELEVANT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_recommendation_ratings"


class QueryLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    raw_query = models.TextField()
    parsed_json = models.JSONField(default=dict)
    matched_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "explore_query_logs"
        ordering = ["-created_at"]

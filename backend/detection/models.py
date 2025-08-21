from django.db import models
from django.conf import settings

class DetectionResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    classification = models.CharField(max_length=50)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    engine = models.CharField(max_length=50)
    latency_ms = models.FloatField()
    preprocessed_text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.classification} ({self.confidence:.2f}) - {self.text[:50]}..."

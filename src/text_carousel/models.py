from django.db import models


class BhsaSlots(models.Model):
    """BHSA word nodes (slots)."""
    node = models.IntegerField(primary_key=True, default=0)
    text = models.TextField()

    def __str__(self) -> str:
        """Return text representation of word."""
        return str(self.text)


class BhsaNodes(models.Model):
    """BHSA nodes and some select attributes."""
    node = models.IntegerField(primary_key=True, default=0)
    otype = models.CharField(max_length=20)
    oslots = models.JSONField(default=list)
    book = models.CharField(max_length=30)
    chapter = models.IntegerField(default=1)
    verse = models.IntegerField(default=1)

    def __str__(self) -> str:
        """Return text representation of object."""
        return str(self.oslots)

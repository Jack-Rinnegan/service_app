from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client

from services.tasks import set_price, set_comment


class Service(models.Model):
    name = models.CharField(max_length=100)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):

        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    discount_percentage = models.PositiveIntegerField(
        default=0,
        validators=[
            MaxValueValidator(100)
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percentage = self.discount_percentage

    def save(self, *args, **kwargs):

        if self.discount_percentage != self.__discount_percentage:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='subscriptions')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    price = models.PositiveIntegerField(
        default=0,
    )
    comment = models.CharField(max_length=50, default='')

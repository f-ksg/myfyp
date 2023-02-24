from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
# Create your models here.

#account creation
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    accountbalance = models.DecimalField(decimal_places=2, max_digits=10)
    tutorialcompletion = models.BooleanField()
    risk_level = models.IntegerField(default=1, choices=[(1, 'Lv.1 Low'), (2, 'Lv.2 Moderate'), (3, 'Lv.3 High')])


@receiver(post_save, sender= User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, accountbalance = 30000, tutorialcompletion = False)
    # instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(user=instance)
    except Profile.DoesNotExist:
        print('Profile does not exist')
        Profile.objects.update_or_create(user=instance, accountbalance = 30000, tutorialcompletion = False)
        instance.profile.save()

#stock info

class StockInfo(models.Model):
    
    tradingName = models.CharField(max_length=100)
    stockCode = models.CharField(max_length=100)
    lastPrice = models.FloatField(null=True)
    roe = models.FloatField(null=True)
    marketcap = models.FloatField(null=True)
    totalRev = models.FloatField(null=True)
    pe = models.FloatField(null=True)
    yieldPercent = models.FloatField(null=True)
    sector = models.CharField(max_length=100)
    gtiScore = models.FloatField(null=True)
    oneYearChange = models.FloatField(null=True)


class Stocks(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10, unique=True)
    risk_level = models.IntegerField(default=0)
    rise = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Ticker: {self.ticker} Name: {self.name}"
    
    class Meta:
        unique_together = ('name', 'ticker')
    def __str__(self):
        return f"Name: {self.name} Ticker: {self.ticker}"

class StockOwned(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile', 'stock', 'purchase_price'], name='unique_stock_owned'),
            models.UniqueConstraint(fields=['profile', 'stock'], condition=Q(purchased_at=None), name='unique_stock_owned_null'),
        ]

    def __str__(self):
        return f"{self.stock.name}"

class StockSold(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stock_owned = models.ForeignKey(StockOwned, on_delete=models.CASCADE, default=0)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile', 'stock', 'sell_price'], name='unique_stock_sold'),
            models.UniqueConstraint(fields=['profile', 'stock'], condition=Q(sold_at=None), name='unique_stock_sold_null'),
        ]

    def __str__(self):
        return f"{self.profile.user.username} sold {self.quantity} shares of {self.stock.name}"


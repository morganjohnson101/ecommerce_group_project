from django.db import models
# from django.db.models import Sum
import re


# MANAGERS
class UserManager(models.Manager):
    def validator(self, postdata):
        email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(postdata['f_name'])<2:
            errors['f_name']="First name MUST be longer than 2 characters!"
        if len(postdata['l_name'])<2:
            errors['l_name']="Last name MUST be longer than 2 characters!"
        if not email_check.match(postdata['email']):
            errors['email']="Email MUST be in valid format!"
        if len(postdata['address'])<8:
            errors['address']="Address MUST be longer than 8 characters!" 
        if len(postdata['city'])<3:
            errors['city']="City MUST be longer than 3 characters!"
        if len(postdata['state'])>2:
            errors['state']="State MUST be 2 characters!"
        if len(postdata['zip_code'])>5:
            errors['zip_code']="Zip Code MUST be 5 characters!" 
        if len(postdata['pw'])<8:
            errors['pw']="Password must be at least 8 characters!"
        if postdata['pw'] != postdata['conf_pw']:
            errors['conf_pw']="Password and confirm password MUST match!"
        return errors


# MODELS
class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.IntegerField()
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Size(models.Model):
    cat = models.CharField(max_length=3)
    s1 = models.CharField(max_length=3)
    s2 = models.CharField(max_length=3)
    s3 = models.CharField(max_length=3, null=True)
    s4 = models.CharField(max_length=3, null=True)
    s5 = models.CharField(max_length=3, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Shoe(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    cat = models.CharField(max_length=10)
    desc = models.TextField(null=True)
    image = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    cc_type = models.CharField(max_length=25)
    card_number = models.IntegerField()
    exp_date = models.IntegerField()
    user = models.ForeignKey(User, related_name="cardholder", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    shoes = models.ManyToManyField(Shoe, related_name="cart")
    # do we need to create/represent a relationship between cart and order (1 cart has 1 order)?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Order(models.Model):
    order_id = models.CharField(max_length=15)
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(decimal_places=2, max_digits=6)
    payment = models.ForeignKey(Payment, related_name="payment", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

from django.db import models
# from django.db.models import Sum
import re


# MANAGERS
class UserManager(models.Manager):
    def create_validator(self, postdata):
        email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(postdata['f_n'])<2:
            errors['f_n']="First name MUST be longer than 2 characters!"
        if len(postdata['l_n'])<2:
            errors['l_n']="Last name MUST be longer than 2 characters!"
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
    objects = UserManager()


class Size(models.Model):
    cat = models.CharField(max_length=10)
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
    #cat=models.ForeignKey(Category, related_name="cat", on_delete=models.CASCADE)
    desc = models.TextField(null=True)
    image = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentManager(models.Manager):
    def create_validator(self, postdata):
        errors = {}
        if len(postdata['cc_type'])<3:
            errors['cc_type'] = "Must be more than 3 characters"
        if len(postdata['card_number'])<5:
            errors['card_number'] = "Must enter a valid card number"
        # if len(postdata['ss_code'])>=3:
        #     errors['ss_code'] = "Invalid Security Code"
        if len(postdata['exp_date'])<3:
            errors['exp_date'] = "Must enter a valid date"
        return errors


class Payment(models.Model):
    cc_type = models.CharField(max_length=25)
    card_number = models.IntegerField()
    ss_code = models.IntegerField(null=True)
    exp_date = models.DateTimeField()
    user = models.ForeignKey(User, related_name="cardholder", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PaymentManager()


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

# class Category(models.Model):
#     cat_name=models.CharField(max_length=25)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    

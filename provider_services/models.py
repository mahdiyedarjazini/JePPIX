from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid


class ServiceProvider(models.Model):
    """
    Model representing service providers in the digital platform.
    A service provider can be managed by multiple account managers.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AccountManager(models.Model):
    """
    Model extending the User model for account managers.
    Each account manager can manage multiple service providers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_manager_profile')
    service_providers = models.ManyToManyField(ServiceProvider, related_name='account_managers')
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return f"{self.user.username} (Account Manager)"
    
    def save(self, *args, **kwargs):
        """Ensure the user is in the account_manager group"""
        super().save(*args, **kwargs)
        account_manager_group, created = Group.objects.get_or_create(name='account_manager')
        self.user.groups.add(account_manager_group)


class Customer(models.Model):
    """
    Model extending the User model for customers.
    Each customer is assigned to at least one account manager.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    account_managers = models.ManyToManyField(AccountManager, related_name='customers')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return f"{self.user.username} (Customer)"
    
    def save(self, *args, **kwargs):
        """Ensure the user is in the customer group"""
        super().save(*args, **kwargs)
        customer_group, created = Group.objects.get_or_create(name='customer')
        self.user.groups.add(customer_group)


class Service(models.Model):
    """
    Model representing services (products) offered by service providers.
    """
    name = models.CharField(max_length=255)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.service_provider.name})"


class Order(models.Model):
    """
    Model representing customer orders.
    An order is created by a customer and managed by a specific account manager.
    Each order belongs to a single Job for execution.
    """
    ORDER_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    account_manager = models.ForeignKey(AccountManager, on_delete=models.CASCADE, related_name='managed_orders')
    job = models.ForeignKey('execution.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Fields to track completion time
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.customer}"
    
    def update_total_price(self):
        """Calculate and update the total price of the order"""
        self.total_price = sum(item.price * item.quantity for item in self.items.all())
        self.save()
    
    def save(self, *args, **kwargs):
        # If status changed to completed, update completed_at
        if self.pk is not None:
            old_instance = Order.objects.get(pk=self.pk)
            if old_instance.status != 'completed' and self.status == 'completed':
                self.completed_at = timezone.now()
        elif self.status == 'completed':
            self.completed_at = timezone.now()
            
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Model representing services added to an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.service.name} ({self.quantity}) - Order {self.order.id}"
    
    def save(self, *args, **kwargs):
        # Set the price of the order item to the service price if not provided
        if not self.price:
            self.price = self.service.price
            
        super().save(*args, **kwargs)
        # Update order total price
        self.order.update_total_price()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Order, Notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Order)
def create_order_notifications(sender, instance, created, **kwargs):
    """Create notifications when orders are created or updated."""
    if created:
        # Order placed notification
        Notification.objects.create(
            user=instance.user,
            title=f'Order #{instance.id} Placed Successfully',
            message=f'You placed an order with {instance.shop.name} for ₹{instance.amount}',
            notification_type='order_placed',
            icon='fas fa-shopping-cart',
            color='#28a745'
        )
    else:
        # Order status changed
        if instance.cloth_status == 'Washing':
            Notification.objects.get_or_create(
                user=instance.user,
                title=f'Order #{instance.id} - Washing Started',
                message=f'Your laundry from {instance.shop.name} is now being washed',
                defaults={
                    'notification_type': 'status_update',
                    'icon': 'fas fa-tint',
                    'color': '#17a2b8'
                }
            )
        elif instance.cloth_status == 'Drying':
            Notification.objects.get_or_create(
                user=instance.user,
                title=f'Order #{instance.id} - Drying Started',
                message=f'Your laundry from {instance.shop.name} is now being dried',
                defaults={
                    'notification_type': 'status_update',
                    'icon': 'fas fa-wind',
                    'color': '#f39c12'
                }
            )
        elif instance.cloth_status == 'Ironing':
            Notification.objects.get_or_create(
                user=instance.user,
                title=f'Order #{instance.id} - Ironing Started',
                message=f'Your laundry from {instance.shop.name} is now being ironed',
                defaults={
                    'notification_type': 'status_update',
                    'icon': 'fas fa-fire',
                    'color': '#e74c3c'
                }
            )
        elif instance.cloth_status == 'Ready':
            Notification.objects.get_or_create(
                user=instance.user,
                title=f'Order #{instance.id} Ready for Pickup',
                message=f'Your laundry from {instance.shop.name} is ready! Please collect it.',
                defaults={
                    'notification_type': 'ready_pickup',
                    'icon': 'fas fa-box-open',
                    'color': '#f39c12'
                }
            )
        elif instance.cloth_status == 'Completed':
            Notification.objects.get_or_create(
                user=instance.user,
                title=f'Order #{instance.id} Completed',
                message=f'Your laundry from {instance.shop.name} has been successfully completed and delivered.',
                defaults={
                    'notification_type': 'completed',
                    'icon': 'fas fa-check-circle',
                    'color': '#28a745'
                }
            )

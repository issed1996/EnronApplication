from django.db import models

# Create your models here.

class Employee(models.Model):
    last_name = models.CharField(max_length=40)
    first_name = models.CharField(max_length=40)
    category = models.CharField(max_length=40,default='Employee')
    mail_box = models.CharField(max_length=40)

    def __str__(self):
        return '{}, {}'.format(self.last_name,self.first_name,)


class mail_address(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    address = models.EmailField(max_length=80)

    def __str__(self):
        return self.address


class mail(models.Model):
    mail_date = models.DateTimeField(null=False)
    subject = models.CharField(max_length=200,null=True)
    sender_mail = models.ForeignKey(mail_address,null=True,on_delete=models.CASCADE,related_name='sender_mail_id')
    recipient_mail = models.ForeignKey(mail_address,null=True,on_delete=models.CASCADE,related_name='recipient_mail_id') #NULL si le mail va à l'exterieur
    isReply = models.BooleanField(default=False)
    previous_mail_date = models.DateTimeField(null=True)
    #on a une instance par couple sender/recipient
    #il peut y avoir plusieurs destinataires : une instance par destinataire 
    def __str__(self):
        return self.subject    

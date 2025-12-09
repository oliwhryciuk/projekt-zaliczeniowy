from django.db import models

#dodawanie torebek 

SIZE = models.IntegerChoices(
    'SIZE',
    'mini midi maxi'
)

COLOR = models.IntegerChoices(
    'COLOR',
    'beige white brown black red purple blue orange pink gold silver grey green yellow mixed '
)

FABRIC = models.IntegerChoices(
    'FABRIC',
    'natural_leather vegan_leather cotton nylon vinyl jute canvas'
)


class Bag(models.Model):
    
    model = models.CharField(max_length= 100, null = False,  blank = False )
    brand =  models.CharField(max_length= 50, null = False,  blank = False )
    size = models.IntegerField(choices = SIZE.choices, default= SIZE.choices[2][0])
    color = models.IntegerField(choices = COLOR.choices, default= COLOR.choices[14][0])
    fabric = models.IntegerField(choices = FABRIC.choices, default= FABRIC.choices[6][0])
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name="price in zł")
  
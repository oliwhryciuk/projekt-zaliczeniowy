from django.db import models

#dodawanie torebek 

ROZM = models.IntegerChoices(
    'ROZM',
    'mini midi maxi'
)


class Torebka(models.Model):
    
    nazwa_modelu = models.CharField(max_length= 100, null = False,  blank = False )
    marka =  models.CharField(max_length= 50, null = False,  blank = False )
    rozmiar = models.IntegerField(choices = ROZM.choices, default= ROZM.choices[2][0])
  
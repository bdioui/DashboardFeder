from django.db import models
from django.contrib.auth.models import User
from datetime import date 

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_data = models.FileField(upload_to='user_data',blank = True, null=True)
	indicateurs_data = models.FileField(upload_to='indicateurs_data', blank = True, null=True) 

	def __str__(self): 
		return self.user.username

class Dossier(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	numero_op = models.CharField(max_length=50, blank = True, null=True)
	porteur = models.CharField(max_length=100, blank = True, null=True)
	libélé = models.CharField(max_length=500, blank = True, null=True)
	descriptif = models.CharField(max_length=200000, blank = True, null=True)

	axe = models.CharField(max_length=15, blank = True, null=True) 
	os = models.CharField(max_length=15, blank = True, null=True) 
	DI = models.CharField(max_length=100, blank = True, null=True)
	OT = models.CharField(max_length=200, blank = True, null=True)

	AAP = models.CharField(max_length=100, null= True, blank=True)

	date_dépôt = models.CharField(max_length=15, blank = True, null=True) 
	date_réception = models.CharField(max_length=15, blank = True, null=True)
	date_complétude = models.CharField(max_length=15, blank = True, null=True)
	date_CRUP = models.CharField(max_length=30, blank = True, null=True) 
	date_notification = models.CharField(max_length=15, blank = True, null=True)
	date_signature = models.CharField(max_length=15, blank = True, null=True)
	debut_op = models.CharField(max_length=15, blank = True, null=True)
	fin_op = models.CharField(max_length=15, blank = True, null=True)
	début_éligibilité = models.CharField(max_length=15, blank = True, null=True)
	fin_éligibilité = models.CharField(max_length=15, blank = True, null=True) 



	montant_CT = models.FloatField(null = True, blank = True, default = 0)
	montant_UE = models.FloatField(null = True, blank = True, default = 0)
	montant_Etat = models.FloatField(null = True, blank = True, default = 0)
	montant_CD = models.FloatField(null = True, blank = True, default = 0)
	montant_Reg = models.FloatField(null = True, blank = True, default = 0)
	montant_autre_public = models.FloatField(null = True, blank = True, default = 0)
	montant_public = models.FloatField(null = True, blank = True, default = 0)
	montant_privé = models.FloatField(null = True, blank = True, default = 0)
	montant_auto = models.FloatField(null = True, blank = True, default = 0)
	DP_CT_depot = models.FloatField(null = True, blank = True, default = 0)
	DP_certif = models.FloatField(null = True, blank = True, default = 0)
	DP_payé = models.FloatField(null = True, blank = True, default = 0)


	statut_macro = models.CharField(max_length=50, default='', blank = True, null=True)
	statut_détaillé = models.CharField(max_length=50, default='', blank = True, null=True)

	type_bénéficiaire = models.CharField(max_length=50, default='', blank = True, null=True)
	
	représentant_légal = models.CharField(max_length=50, default='', blank = True, null=True)
	représentant_légal_tel = models.CharField(max_length=50, default='', blank = True, null=True)
	représentant_légal_mail = models.CharField(max_length=50, default='', blank = True, null=True)
	référent = models.CharField(max_length=50, default='', blank = True, null=True)
	référent_tel = models.CharField(max_length=50, default='', blank = True, null=True)
	référent_mail = models.CharField(max_length=50, default='', blank = True, null=True)

	instructeur = models.CharField(max_length=50, default='', blank = True, null=True)
	service = models.CharField(max_length=50, default='', blank = True, null=True)
	avis_SI = models.CharField(max_length=15, default='', blank = True, null=True)
	motivation_avis = models.CharField(max_length=400, default='', blank = True, null=True)

	note = models.CharField(max_length=500, default='Notes', blank = True, null=True)



	def __str__(self):
		return self.numero_op + ' - ' + self.porteur

class Indicateur(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	numero_op = models.CharField(max_length=200, default='', blank = True, null=True)
	indicateur = models.CharField(max_length=200, default='', blank = True, null=True)
	libellé = models.CharField(max_length=200, default='', blank = True, null=True)
	type_indicateur = models.CharField(max_length=15, default='', blank = True, null=True)
	unité = models.CharField(max_length=25, default='', blank = True, null=True)
	valeur_prev = models.FloatField(null = True, blank = True, default = 0)
	valeur_conv = models.FloatField(null = True, blank = True, default = 0)
	valeur_real = models.FloatField(null = True, blank = True, default = 0)

	def __str__(self):
		return self.indicateur + ' - ' + self.numero_op




class Enveloppe(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	Enveloppe_totale = models.FloatField(null = True, blank = True, default = 0)
	Axe_1=models.FloatField(null = True, blank = True, default = 0)
	OS_1_1=models.FloatField(null = True, blank = True, default = 0)
	OS_1_2=models.FloatField(null = True, blank = True, default = 0)
	OS_1_3=models.FloatField(null = True, blank = True, default = 0)
	OS_1_4=models.FloatField(null = True, blank = True, default = 0)
	OS_1_5=models.FloatField(null = True, blank = True, default = 0)
	OS_1_6=models.FloatField(null = True, blank = True, default = 0)
	OS_1_7=models.FloatField(null = True, blank = True, default = 0)
	OS_1_8=models.FloatField(null = True, blank = True, default = 0)
	OS_1_9=models.FloatField(null = True, blank = True, default = 0)
	OS_1_10=models.FloatField(null = True, blank = True, default = 0)
	


	Axe_2=models.FloatField(null = True, blank = True, default = 0)
	OS_2_1=models.FloatField(null = True, blank = True, default = 0)
	OS_2_2=models.FloatField(null = True, blank = True, default = 0)
	OS_2_3=models.FloatField(null = True, blank = True, default = 0)
	OS_2_4=models.FloatField(null = True, blank = True, default = 0)
	OS_2_5=models.FloatField(null = True, blank = True, default = 0)
	OS_2_6=models.FloatField(null = True, blank = True, default = 0)
	OS_2_7=models.FloatField(null = True, blank = True, default = 0)
	OS_2_8=models.FloatField(null = True, blank = True, default = 0)
	OS_2_9=models.FloatField(null = True, blank = True, default = 0)
	OS_2_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_3=models.FloatField(null = True, blank = True, default = 0)
	OS_3_1=models.FloatField(null = True, blank = True, default = 0)
	OS_3_2=models.FloatField(null = True, blank = True, default = 0)
	OS_3_3=models.FloatField(null = True, blank = True, default = 0)
	OS_3_4=models.FloatField(null = True, blank = True, default = 0)
	OS_3_5=models.FloatField(null = True, blank = True, default = 0)
	OS_3_6=models.FloatField(null = True, blank = True, default = 0)
	OS_3_7=models.FloatField(null = True, blank = True, default = 0)
	OS_3_8=models.FloatField(null = True, blank = True, default = 0)
	OS_3_9=models.FloatField(null = True, blank = True, default = 0)
	OS_3_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_4=models.FloatField(null = True, blank = True, default = 0)
	OS_4_1=models.FloatField(null = True, blank = True, default = 0)
	OS_4_2=models.FloatField(null = True, blank = True, default = 0)
	OS_4_3=models.FloatField(null = True, blank = True, default = 0)
	OS_4_4=models.FloatField(null = True, blank = True, default = 0)
	OS_4_5=models.FloatField(null = True, blank = True, default = 0)
	OS_4_6=models.FloatField(null = True, blank = True, default = 0)
	OS_4_7=models.FloatField(null = True, blank = True, default = 0)
	OS_4_8=models.FloatField(null = True, blank = True, default = 0)
	OS_4_9=models.FloatField(null = True, blank = True, default = 0)
	OS_4_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_5=models.FloatField(null = True, blank = True, default = 0)
	OS_5_1=models.FloatField(null = True, blank = True, default = 0)
	OS_5_2=models.FloatField(null = True, blank = True, default = 0)
	OS_5_3=models.FloatField(null = True, blank = True, default = 0)
	OS_5_4=models.FloatField(null = True, blank = True, default = 0)
	OS_5_5=models.FloatField(null = True, blank = True, default = 0)
	OS_5_6=models.FloatField(null = True, blank = True, default = 0)
	OS_5_7=models.FloatField(null = True, blank = True, default = 0)
	OS_5_8=models.FloatField(null = True, blank = True, default = 0)
	OS_5_9=models.FloatField(null = True, blank = True, default = 0)
	OS_5_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_6=models.FloatField(null = True, blank = True, default = 0)
	OS_6_1=models.FloatField(null = True, blank = True, default = 0)
	OS_6_2=models.FloatField(null = True, blank = True, default = 0)
	OS_6_3=models.FloatField(null = True, blank = True, default = 0)
	OS_6_4=models.FloatField(null = True, blank = True, default = 0)
	OS_6_5=models.FloatField(null = True, blank = True, default = 0)
	OS_6_6=models.FloatField(null = True, blank = True, default = 0)
	OS_6_7=models.FloatField(null = True, blank = True, default = 0)
	OS_6_8=models.FloatField(null = True, blank = True, default = 0)
	OS_6_9=models.FloatField(null = True, blank = True, default = 0)
	OS_6_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_7=models.FloatField(null = True, blank = True, default = 0)
	OS_7_1=models.FloatField(null = True, blank = True, default = 0)
	OS_7_2=models.FloatField(null = True, blank = True, default = 0)
	OS_7_3=models.FloatField(null = True, blank = True, default = 0)
	OS_7_4=models.FloatField(null = True, blank = True, default = 0)
	OS_7_5=models.FloatField(null = True, blank = True, default = 0)
	OS_7_6=models.FloatField(null = True, blank = True, default = 0)
	OS_7_7=models.FloatField(null = True, blank = True, default = 0)
	OS_7_8=models.FloatField(null = True, blank = True, default = 0)
	OS_7_9=models.FloatField(null = True, blank = True, default = 0)
	OS_7_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_8=models.FloatField(null = True, blank = True, default = 0)
	OS_8_1=models.FloatField(null = True, blank = True, default = 0)
	OS_8_2=models.FloatField(null = True, blank = True, default = 0)
	OS_8_3=models.FloatField(null = True, blank = True, default = 0)
	OS_8_4=models.FloatField(null = True, blank = True, default = 0)
	OS_8_5=models.FloatField(null = True, blank = True, default = 0)
	OS_8_6=models.FloatField(null = True, blank = True, default = 0)
	OS_8_7=models.FloatField(null = True, blank = True, default = 0)
	OS_8_8=models.FloatField(null = True, blank = True, default = 0)
	OS_8_9=models.FloatField(null = True, blank = True, default = 0)
	OS_8_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_9=models.FloatField(null = True, blank = True, default = 0)
	OS_9_1=models.FloatField(null = True, blank = True, default = 0)
	OS_9_2=models.FloatField(null = True, blank = True, default = 0)
	OS_9_3=models.FloatField(null = True, blank = True, default = 0)
	OS_9_4=models.FloatField(null = True, blank = True, default = 0)
	OS_9_5=models.FloatField(null = True, blank = True, default = 0)
	OS_9_6=models.FloatField(null = True, blank = True, default = 0)
	OS_9_7=models.FloatField(null = True, blank = True, default = 0)
	OS_9_8=models.FloatField(null = True, blank = True, default = 0)
	OS_9_9=models.FloatField(null = True, blank = True, default = 0)
	OS_9_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_10=models.FloatField(null = True, blank = True, default = 0)
	OS_10_1=models.FloatField(null = True, blank = True, default = 0)
	OS_10_2=models.FloatField(null = True, blank = True, default = 0)
	OS_10_3=models.FloatField(null = True, blank = True, default = 0)
	OS_10_4=models.FloatField(null = True, blank = True, default = 0)
	OS_10_5=models.FloatField(null = True, blank = True, default = 0)
	OS_10_6=models.FloatField(null = True, blank = True, default = 0)
	OS_10_7=models.FloatField(null = True, blank = True, default = 0)
	OS_10_8=models.FloatField(null = True, blank = True, default = 0)
	OS_10_9=models.FloatField(null = True, blank = True, default = 0)
	OS_10_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_11=models.FloatField(null = True, blank = True, default = 0)
	OS_11_1=models.FloatField(null = True, blank = True, default = 0)
	OS_11_2=models.FloatField(null = True, blank = True, default = 0)
	OS_11_3=models.FloatField(null = True, blank = True, default = 0)
	OS_11_4=models.FloatField(null = True, blank = True, default = 0)
	OS_11_5=models.FloatField(null = True, blank = True, default = 0)
	OS_11_6=models.FloatField(null = True, blank = True, default = 0)
	OS_11_7=models.FloatField(null = True, blank = True, default = 0)
	OS_11_8=models.FloatField(null = True, blank = True, default = 0)
	OS_11_9=models.FloatField(null = True, blank = True, default = 0)
	OS_11_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_12=models.FloatField(null = True, blank = True, default = 0)
	OS_12_1=models.FloatField(null = True, blank = True, default = 0)
	OS_12_2=models.FloatField(null = True, blank = True, default = 0)
	OS_12_3=models.FloatField(null = True, blank = True, default = 0)
	OS_12_4=models.FloatField(null = True, blank = True, default = 0)
	OS_12_5=models.FloatField(null = True, blank = True, default = 0)
	OS_12_6=models.FloatField(null = True, blank = True, default = 0)
	OS_12_7=models.FloatField(null = True, blank = True, default = 0)
	OS_12_8=models.FloatField(null = True, blank = True, default = 0)
	OS_12_9=models.FloatField(null = True, blank = True, default = 0)
	OS_12_10=models.FloatField(null = True, blank = True, default = 0)

	Axe_13=models.FloatField(null = True, blank = True, default = 0)
	OS_13_1=models.FloatField(null = True, blank = True, default = 0)
	OS_13_2=models.FloatField(null = True, blank = True, default = 0)
	OS_13_3=models.FloatField(null = True, blank = True, default = 0)
	OS_13_4=models.FloatField(null = True, blank = True, default = 0)
	OS_13_5=models.FloatField(null = True, blank = True, default = 0)
	OS_13_6=models.FloatField(null = True, blank = True, default = 0)
	OS_13_7=models.FloatField(null = True, blank = True, default = 0)
	OS_13_8=models.FloatField(null = True, blank = True, default = 0)
	OS_13_9=models.FloatField(null = True, blank = True, default = 0)
	OS_13_10=models.FloatField(null = True, blank = True, default = 0)

	def __str__(self):
		return 'Enveloppe FEDER de ' + self.user.username





















# Create your models here.

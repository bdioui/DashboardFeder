from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, CSV_load, Enveloppe_form, Indicateurs_load
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required 
import pandas as pd
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
import json
import csv
import datetime

from .models import Dossier, Enveloppe, Indicateur

from django.db.models import Sum, Count

from dash_board.utils import render_to_pdf
from django.template.loader import get_template





##############################################################################################################
###################################### HOME VIEW #############################################################
#####################################################################################################################


class HomeView(LoginRequiredMixin, View):
	def get(self, request,*args, **kwargs):
		try:
			user = User.objects.get(id=request.user.id)
			Dossier.objects.filter(user=user).delete()
			csv_file = user.profile.user_data
			indicateur_file = user.profile.indicateurs_data

			dfi = pd.read_csv(indicateur_file, encoding = "UTF-8", delimiter=';', decimal=',')
			dfi = dfi.round(2)


			df = pd.read_csv(csv_file, encoding = "UTF-8", delimiter=';', decimal=',')
			df = df.round(2)
			df["Début de la période prévisionnelle d'exécution"]=df["Début de la période prévisionnelle d'exécution"].str.strip()
			df["Date Dépôt"]=df["Date Dépôt"].str.strip()
			print(df["Date Dépôt"])
			df['Coût Public']= df.iloc[:,80:85].sum(axis=1, skipna=True)
			#print(df['Coût Public'])
			row_iter = df.iterrows()
			
			objs = [
			Dossier(

				user = user,

				numero_op = row['N° Dossier'],
				porteur = row['Bénéficiaire'],
				libélé = row['Libellé du dossier'],
				descriptif = row["Résumé de l'opération"],
				
				axe = row['NIV1'],
				os = row ['NIV4'],
				DI = row ["CI01 - Domaine d'intervention"],
				OT = row ["CI05 - Objectifs thématiques (FEDER et Fonds de cohésion)"],
				
				AAP = row["Référence de l'appel à projet"],
				
				date_dépôt = row["Date Dépôt"],
				date_réception = row["Accusé de réception"],
				date_complétude = row["Dossier complet"],
				date_CRUP = row["Libellé dernier Comité décisionnel"],
				date_notification = row["Notification de la décision du comité"],
				date_signature = row["Signature de l'acte attributif"],
				debut_op = row["Début de la période prévisionnelle d'exécution"],
				fin_op = row["Fin de la période prévisionnelle d'exécution"],
				début_éligibilité = row["Début d'éligibilité des dépenses"],
				fin_éligibilité = row ["Fin d'éligibilité des dépenses"],
				
				montant_CT = row['Coût total en cours'],
				montant_UE = row['UE'],
				montant_Etat = row["Etat"],
				montant_CD = row["Département"],
				montant_Reg = row["Région"],
				montant_autre_public = row["Autres publics"],
				montant_privé = row['Privé'],
				montant_auto = row['Autofinancement'],
				DP_CT_depot = row["Dépenses retenues pour le calcul de l'UE (CSF)"],
				DP_certif = row['UE déjà versé dans les CSF envoyés AC (CSF)'],
				DP_payé = row['UE payé retenu AG (PF)'],
				montant_public = row['Coût Public'],

				statut_macro = row['Statut macro'],
				statut_détaillé = row['Statut détaillé'],
				type_bénéficiaire = row['Nature juridique'],

				représentant_légal = row['Représentant légal - Info'],
				représentant_légal_tel = row['Représentant légal - Tel'],
				représentant_légal_mail = row['Représentant légal - Mail'],
				référent = row["Référent de l'opération - Info"],
				référent_tel = row["Référent de l'opération - Tel"],
				référent_mail = row["Référent de l'opération - Mail"],
				
				instructeur = row['Instructeur'],
				service = row['Service instructeur'],
				avis_SI = row['Avis Service Unique'],
				motivation_avis = row["Motivation de l'avis instructeur"],
				note = 'note'

			)

			for index, row in row_iter

			]

			Dossier.objects.bulk_create(objs)

			row_iter_indicateur = dfi.iterrows()
			
			objs = [
			Indicateur(

				user = user,
				numero_op = row['Numéro opération'],
				indicateur = row['Indicateur (code)'],
				libellé = row['Indicateur (libellé)'],
				type_indicateur = row['Type indicateur'],
				unité = row['Unité de mesure indicateur'],
				valeur_prev = row['Valeur prévisionnelle (en cours)'],
				valeur_conv = row['Valeur prévisionnelle (conventionnée)'],
				valeur_real = row["Valeur réalisée - TOTAL (dans le cas d'un indicateur H/F) ou Valeur qualitative"],


				

			)

			for index, row in row_iter_indicateur

			]

			Indicateur.objects.bulk_create(objs)


			user  = User.objects.get(id=request.user.id)
			csv_file = user.profile.user_data

			df = pd.read_csv(csv_file, delimiter=';', decimal=',')
			df = df.round(2)

			
			df_programmé = df[df['Statut macro'] == 'Programmé']
			df_retiré = df[df['Statut macro'] == 'Retiré']
			df_déposé = df[df['Statut macro'] == 'Déposé']
			df_instruction = df[df['Statut macro'] == 'En instruction']

			html=df_programmé.to_html()


			val_ue = (df_programmé['UE'].sum(skipna=True))
			val_tot = (df_programmé['Coût total en cours'].sum(skipna=True))
			val_cert = (df_programmé['UE déjà versé dans les CSF envoyés AC (CSF)'].sum(skipna=True)).round(3)
			taux_certif = ((val_cert / val_ue)*100).round(0)

			nb_programmé= df_programmé['N° Dossier'].count()
			nb_retiré = df_retiré['N° Dossier'].count()
			nb_déposé = df_déposé['N° Dossier'].count()
			nb_instruction = df_instruction['N° Dossier'].count()

			# liste des axes sélectionnées
			axes = (df['NIV1'].tolist())
			axes = list(dict.fromkeys(axes))
			#print(axes.sort())

			#TOP 10 des plus gros dossiers programmés
			df_top10 = df_programmé.nlargest(5,'UE')
			df_top10 = df_top10[['NIV1','N° Dossier', 'Libellé du dossier', 'Bénéficiaire', 'Statut détaillé', 'Coût total en cours','UE', 'UE déjà versé dans les CSF envoyés AC (CSF)' ]]
			#print(df_top10)
			#print(df_top10.iloc[1])
			liste_axe_top = df_top10['NIV1'].tolist()
			liste_num_top = df_top10['N° Dossier'].tolist()
			liste_béné_top = df_top10['Bénéficiaire'].tolist()
			liste_statut_top = df_top10['Statut détaillé'].tolist()
			liste_libélé_top = df_top10['Libellé du dossier'].tolist()
			liste_tot_top = df_top10['Coût total en cours'].tolist()
			liste_ue_top = df_top10['UE'].tolist()
			liste_cert_top = df_top10['UE déjà versé dans les CSF envoyés AC (CSF)'].tolist()

			top10 = Dossier.objects.filter(user=user).order_by('-montant_UE')[:10]
			

			

			
			#liste des OS sélectionnés
			oss = (df['NIV4'].tolist())
			oss = list(dict.fromkeys(oss))
			#print(oss.sort())
			
			
			# Somme programmée par axe
			df_axe_ue = df_programmé.groupby(['NIV1'])['UE'].sum()
			df_axe_tot = df_programmé.groupby(['NIV1'])['Coût total en cours'].sum()
			df_axe_cert = df_programmé.groupby(['NIV1'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
			# print(df_axe_tot)
			# print(df_axe_cert)

			
			# Somme programmé par OS
			df_os_ue = df_programmé.groupby(['NIV4'])['UE'].sum()
			df_os_tot = df_programmé.groupby(['NIV4'])['Coût total en cours'].sum()
			df_os_cert = df_programmé.groupby(['NIV4'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
			# print(df_os_tot)
			
			#placer la somme FEDER par axe dans une liste
			tot_ue_axe = []
			tot_ue_os = []



			tot_tot_axe = []
			tot_tot_os = []

			tot_cert_axe = []
			tot_cert_os = []
			
			for axe in axes:
				try:
					tot_ue_axe.append(df_axe_ue[axe])
					tot_tot_axe.append(df_axe_tot[axe])
					tot_cert_axe.append(df_axe_tot[axe])
				except:
					pass
			

			#placer la somme FEDER par os dans une liste
			for os in oss:
				try:
					tot_ue_os.append(df_os_ue[os])
					tot_tot_os.append(df_os_tot[os])
					tot_cert_os.append(df_os_cert[os])
				except:
					pass



			

				# print(axes)
				# print(tot_ue_axe)
				
				# print(oss)
				# print(tot_ue_os)
			
				
				
				enveloppe = Enveloppe.objects.filter(user=user)
				somme_axe = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('axe').annotate(
					Montant_UE=Sum('montant_UE'),  
					Montant_CT=Sum('montant_CT'),
					Montant_Certif=Sum('DP_certif'),
					Montant_Payé=Sum('DP_payé'),
					Nombre = Count('numero_op'),
					 ))

				somme_OS = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('os').annotate(
				Montant_UE=Sum('montant_UE'), 
				Montant_CT=Sum('montant_CT'),
				Montant_Certif=Sum('DP_certif'),
				Montant_Payé=Sum('DP_payé'),
				Nombre = Count('numero_op'),
				 ))
			
				
			
				Axe_1 = somme_axe[0]
				Axe_2 = somme_axe[1]
				Axe_3 = somme_axe[2]
				Axe_4 = somme_axe[3]
				Axe_5 = somme_axe[4]
				Axe_6 = somme_axe[5]
				Axe_12 = somme_axe[6]
				Axe_13 = somme_axe[7]

				OS_1_1 = somme_OS[0]
				OS_1_2 = somme_OS[1]
				OS_1_3 = somme_OS[2]
				OS_1_4 = somme_OS[3]
				OS_2_1 = somme_OS[4]
				OS_2_2 = somme_OS[5]
				OS_2_3 = somme_OS[6]
				OS_3_1 = somme_OS[7]
				OS_3_2 = somme_OS[8]
				OS_3_3 = somme_OS[9]
				OS_4_1 = somme_OS[10]
				OS_4_2 = somme_OS[11]
				OS_4_3 = somme_OS[12]
				OS_4_4 = somme_OS[13]
				OS_5_1 = somme_OS[14]
				OS_5_2 = somme_OS[15]
				OS_6_1 = somme_OS[16]
				OS_6_2 = somme_OS[17]
				OS_12_1 = somme_OS[18]
				OS_13_1 = somme_OS[19]

				somme_UE = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_UE')))
				print('MARKER')
				print(somme_UE)

				somme_Certif = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_certif')))
				print(somme_Certif)

				query = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='Déposé') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='Déposé')
				nombre_query = query.count()

				user = User.objects.get(id=request.user.id)
				query_difficulté = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='En instruction') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='En instruction')
				nombre_query_difficulté = query_difficulté.count()

				query_programmé_difficulté = Dossier.objects.filter(user=user, date_signature__startswith='2016',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2017',  statut_macro='Programmé') |  Dossier.objects.filter(user=user, date_signature__startswith='2018',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2019',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2020',  statut_macro='Programmé')
				nombre_query_programmé_difficulté = query_programmé_difficulté.count()

				
				context = {

				#'enveloppe':enveloppe,

				'liste_axe_top':liste_axe_top,
				'liste_num_top':liste_num_top,
				'liste_béné_top':liste_béné_top,
				'liste_statut_top':liste_statut_top,
				'liste_tot_top':liste_tot_top,
				'liste_ue_top':liste_ue_top,
				'liste_cert_top':liste_cert_top,
				'liste_libélé_top' : liste_libélé_top,


				'val_tot': val_tot,
				'val_ue' : val_ue,
				'val_cert':val_cert,
				'taux_certif': taux_certif,

				'top10':top10,

				'enveloppe':enveloppe,
				'somme_axe':somme_axe,

				'Axe_1': Axe_1,
				'Axe_2': Axe_2,
				'Axe_3': Axe_3,
				'Axe_4': Axe_4,
				'Axe_5': Axe_5,
				'Axe_6': Axe_6,
				'Axe_12': Axe_12,
				'Axe_13': Axe_13,

				'OS_1_1' : OS_1_1,
				'OS_1_2' : OS_1_2,
				'OS_1_3' : OS_1_3,
				'OS_1_4' : OS_1_4,
				'OS_2_1' : OS_2_1,
				'OS_2_2' : OS_2_2,
				'OS_2_3' : OS_2_3,
				'OS_3_1' : OS_3_1,
				'OS_3_2' : OS_3_2,
				'OS_3_3' : OS_3_3,
				'OS_4_1' : OS_4_1,
				'OS_4_2' : OS_4_2,
				'OS_4_3' :OS_4_3,
				'OS_4_4' : OS_4_4,
				'OS_5_1' : OS_5_1,
				'OS_5_2' : OS_5_2,
				'OS_6_1' : OS_6_1,
				'OS_6_2' : OS_6_2,
				'OS_12_1' : OS_12_1,
				'OS_13_1': OS_13_1,

				'somme_UE':somme_UE,
				'somme_Certif':somme_Certif,
				'query':query,
				'nombre_query':nombre_query,
				'query_difficulté':query_difficulté,
				'nombre_query_difficulté':nombre_query_difficulté,
				'query_programmé_difficulté':query_programmé_difficulté,
				'nombre_query_programmé_difficulté':nombre_query_programmé_difficulté,


			
				}

				return render(request, 'dash/home.html', context)

		except:
			user = User.objects.get(id=request.user.id)
			Dossier.objects.filter(user=user).delete()
			return render(request, 'dash/home.html')



#API pour Bar data FEDER par axe
def bar_data(request,*args, **kwargs):
	user  = User.objects.get(id=request.user.id)
	csv_file = user.profile.user_data

	df = pd.read_csv(csv_file, delimiter=';', decimal=',')
	df = df.round(2)

	df_programmé = df[df['Statut macro'] == 'Programmé']
	df_retiré = df[df['Statut macro'] == 'Retiré']
	df_déposé = df[df['Statut macro'] == 'Déposé']
	df_instruction = df[df['Statut macro'] == 'En instruction']


	val_ue = (df_programmé['UE'].sum(skipna=True))
	val_tot = (df_programmé['Coût total en cours'].sum(skipna=True))
	val_cert = (df_programmé['UE déjà versé dans les CSF envoyés AC (CSF)'].sum(skipna=True)).round(3)
	taux_certif = ((val_cert / val_ue)*100).round(0)

	# liste des axes sélectionnées
	axes = (df['NIV1'].tolist())
	axes = list(dict.fromkeys(axes))
	print(axes.sort())
	
	
	#liste des OS sélectionnés
	oss = (df['NIV4'].tolist())
	oss = list(dict.fromkeys(oss))
	print(oss.sort())
	
	
	# Somme FEDER programmée par axe
	df_axe_ue = df_programmé.groupby(['NIV1'])['UE'].sum()
	df_axe_tot = df_programmé.groupby(['NIV1'])['Coût total en cours'].sum()
	df_axe_cert = df_programmé.groupby(['NIV1'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
	

	
	# Somme FEDER programmé par OS
	df_os_ue = df_programmé.groupby(['NIV4'])['UE'].sum()
	df_os_tot = df_programmé.groupby(['NIV4'])['Coût total en cours'].sum()
	df_os_cert = df_programmé.groupby(['NIV4'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
	# print(df_os_tot)

	
	#placer la somme FEDER par axe dans une liste
	tot_ue_axe = []
	tot_ue_os = []

	tot_tot_axe = []
	tot_tot_os = []

	tot_cert_axe = []
	tot_cert_os = []
	
	for axe in axes:
		try:
			tot_ue_axe.append(df_axe_ue[axe])
			tot_tot_axe.append(df_axe_tot[axe])
			tot_cert_axe.append(df_axe_cert[axe])
		except:
			pass
	

	#placer la somme FEDER par os dans une liste
	for os in oss:
		try:
			tot_ue_os.append(df_os_ue[os])
			tot_tot_os.append(df_os_tot[os])
			tot_cert_os.append(df_os_cert[os])
		except:
			pass

	bar_data = tot_ue_axe
	bar_data_cert = tot_cert_axe
	bar_labels = axes

	data = {
		'bar_data': bar_data,
		'bar_data_cert': bar_data_cert,
		'bar_labels': bar_labels,
	}
	return JsonResponse(data)

#API pour Bar data FEDER par os
def bar_data2(request,*args, **kwargs):
	user  = User.objects.get(id=request.user.id)
	csv_file = user.profile.user_data

	df = pd.read_csv(csv_file, delimiter=';', decimal=',')
	df = df.round(2)

	df_programmé = df[df['Statut macro'] == 'Programmé']
	df_retiré = df[df['Statut macro'] == 'Retiré']
	df_déposé = df[df['Statut macro'] == 'Déposé']
	df_instruction = df[df['Statut macro'] == 'En instruction']


	val_ue = (df_programmé['UE'].sum(skipna=True))
	val_tot = (df_programmé['Coût total en cours'].sum(skipna=True))
	val_cert = (df_programmé['UE déjà versé dans les CSF envoyés AC (CSF)'].sum(skipna=True)).round(3)
	taux_certif = ((val_cert / val_ue)*100).round(0)

	# liste des axes sélectionnées
	axes = (df['NIV1'].tolist())
	axes = list(dict.fromkeys(axes))
	print(axes.sort())
	
	
	#liste des OS sélectionnés
	oss = (df['NIV4'].tolist())
	oss = list(dict.fromkeys(oss))
	print(oss.sort())
	
	
	# Somme FEDER programmée par axe
	df_axe_ue = df_programmé.groupby(['NIV1'])['UE'].sum()
	df_axe_tot = df_programmé.groupby(['NIV1'])['Coût total en cours'].sum()
	print(df_axe_tot)

	
	# Somme FEDER programmé par OS
	df_os_ue = df_programmé.groupby(['NIV4'])['UE'].sum()
	df_os_tot = df_programmé.groupby(['NIV4'])['Coût total en cours'].sum()
	df_os_cert = df_programmé.groupby(['NIV4'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
	print(df_os_tot)
	print(df_os_cert)

	
	#placer la somme FEDER par axe dans une liste
	tot_ue_axe = []
	tot_ue_os = []

	tot_tot_axe = []
	tot_tot_os = []

	tot_cert_axe = []
	tot_cert_os = []
	
	for axe in axes:
		try:
			tot_ue_axe.append(df_axe_ue[axe])
			tot_tot_axe.append(df_axe_tot[axe])
			tot_cert_axe.append(df_axe_cert[axe])
		except:
			pass
	

	#placer la somme FEDER par os dans une liste
	for os in oss:
		try:
			tot_ue_os.append(df_os_ue[os])
			tot_tot_os.append(df_os_tot[os])
			tot_cert_os.append(df_os_cert[os])
		except:
			pass


	bar_data = tot_ue_os
	bar_labels = oss
	bar_data_cert = tot_cert_os

	data = {
		'bar_data': bar_data,
		'bar_data_cert':bar_data_cert,
		'bar_labels': bar_labels,

	}
	return JsonResponse(data)



#API pour donught graph
def get_data(request,*args, **kwargs):
	user  = User.objects.get(id=request.user.id)
	csv_file = user.profile.user_data

	df = pd.read_csv(csv_file, delimiter=';', decimal=',')
	df = df.round(2)

	df_programmé = df[df['Statut macro'] == 'Programmé']
	df_retiré = df[df['Statut macro'] == 'Retiré']
	df_déposé = df[df['Statut macro'] == 'Déposé']
	df_instruction = df[df['Statut macro'] == 'En instruction']

	nb_programmé= df_programmé['N° Dossier'].count()
	nb_programmé = int(nb_programmé)

	nb_retiré = df_retiré['N° Dossier'].count()
	nb_retiré = int(nb_retiré)

	nb_déposé = df_déposé['N° Dossier'].count()
	nb_déposé = int(nb_déposé)

	nb_instruction = df_instruction['N° Dossier'].count()
	nb_instruction = int(nb_instruction)

	data = [nb_déposé, nb_instruction, nb_programmé, nb_retiré]
	labels = ['depose', 'En instruction', 'Programme', 'Retire']



	data = {
		'data': data,
		'labels': labels,

	}

	return JsonResponse(data)




# class ChartData(APIView):
# 	authentication_classes = []
# 	permission_classes = []


# 	def get(self, request, format=None):
		

# 		labels = ['Déposé','En instruction', 'Programmé', 'Retiré',]
# 		default_items = [12, 32, 23, 22]
		
# 		data = {
# 			'labels': labels,
# 			'default': default_items,
# 			}
		
# 		return Response(data)

#####################################################################################################################
###################################### FIN HOME VIEW #############################################################
#####################################################################################################################
def alerte(request):
	user = User.objects.get(id=request.user.id)
	query = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='Déposé') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='Déposé')
	nombre_query = query.count()

	context = {
	'query':query,
	'nombre_query':nombre_query,
	}
	return render(request, 'dash/alerte.html', context)

def difficulté(request):
	user = User.objects.get(id=request.user.id)
	query_difficulté = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='En instruction') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='En instruction')
	nombre_query_difficulté = query_difficulté.count()

	context = {
	'query_difficulté':query_difficulté,
	'nombre_query_difficulté':nombre_query_difficulté,
	}
	return render(request, 'dash/difficulté.html', context)

def programmé_difficulté(request):
	user = User.objects.get(id=request.user.id)
	query_programmé_difficulté = Dossier.objects.filter(user=user, date_signature__startswith='2016',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2017',  statut_macro='Programmé') |  Dossier.objects.filter(user=user, date_signature__startswith='2018',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2019',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2020',  statut_macro='Programmé')
	nombre_programmé_difficulté = query_programmé_difficulté.count()

	context = {
	'query_programmé_difficulté':query_programmé_difficulté,
	'nombre_programmé_difficulté':nombre_programmé_difficulté,
	}
	return render(request, 'dash/programmé_difficulté.html', context)

def difficultés(request):
	user = User.objects.get(id=request.user.id)

	query_programmé_difficulté = Dossier.objects.filter(user=user, date_signature__startswith='2016',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2017',  statut_macro='Programmé') |  Dossier.objects.filter(user=user, date_signature__startswith='2018',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2019',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2020',  statut_macro='Programmé')
	nombre_programmé_difficulté = query_programmé_difficulté.count()

	query_difficulté = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='En instruction') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='En instruction')
	nombre_query_difficulté = query_difficulté.count()

	query = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='Déposé') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='Déposé')
	nombre_query = query.count()

	context = {
	'query_programmé_difficulté':query_programmé_difficulté,
	'nombre_programmé_difficulté':nombre_programmé_difficulté,

	'query_difficulté':query_difficulté,
	'nombre_query_difficulté':nombre_query_difficulté,

	'query':query,
	'nombre_query':nombre_query,



	}
	return render(request, 'dash/difficultés.html', context)


class Home_Report(View):
	def get(self, request,*args, **kwargs):
		template = get_template('dash/test.html')

		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)

		
		df_programmé = df[df['Statut macro'] == 'Programmé']
		df_retiré = df[df['Statut macro'] == 'Retiré']
		df_déposé = df[df['Statut macro'] == 'Déposé']
		df_instruction = df[df['Statut macro'] == 'En instruction']

		html=df_programmé.to_html()


		val_ue = (df_programmé['UE'].sum(skipna=True))
		val_tot = (df_programmé['Coût total en cours'].sum(skipna=True))
		val_cert = (df_programmé['UE déjà versé dans les CSF envoyés AC (CSF)'].sum(skipna=True)).round(3)
		taux_certif = ((val_cert / val_ue)*100).round(0)

		nb_programmé= df_programmé['N° Dossier'].count()
		nb_retiré = df_retiré['N° Dossier'].count()
		nb_déposé = df_déposé['N° Dossier'].count()
		nb_instruction = df_instruction['N° Dossier'].count()

		# liste des axes sélectionnées
		axes = (df['NIV1'].tolist())
		axes = list(dict.fromkeys(axes))
		#print(axes.sort())

		#TOP 10 des plus gros dossiers programmés
		df_top10 = df_programmé.nlargest(5,'UE')
		df_top10 = df_top10[['NIV1','N° Dossier', 'Libellé du dossier', 'Bénéficiaire', 'Statut détaillé', 'Coût total en cours','UE', 'UE déjà versé dans les CSF envoyés AC (CSF)' ]]
		#print(df_top10)
		#print(df_top10.iloc[1])
		liste_axe_top = df_top10['NIV1'].tolist()
		liste_num_top = df_top10['N° Dossier'].tolist()
		liste_béné_top = df_top10['Bénéficiaire'].tolist()
		liste_statut_top = df_top10['Statut détaillé'].tolist()
		liste_libélé_top = df_top10['Libellé du dossier'].tolist()
		liste_tot_top = df_top10['Coût total en cours'].tolist()
		liste_ue_top = df_top10['UE'].tolist()
		liste_cert_top = df_top10['UE déjà versé dans les CSF envoyés AC (CSF)'].tolist()

		top10 = Dossier.objects.order_by('-montant_UE')[:10]
		
		
		#liste des OS sélectionnés
		oss = (df['NIV4'].tolist())
		oss = list(dict.fromkeys(oss))
		#print(oss.sort())
		
		
		# Somme programmée par axe
		df_axe_ue = df_programmé.groupby(['NIV1'])['UE'].sum()
		df_axe_tot = df_programmé.groupby(['NIV1'])['Coût total en cours'].sum()
		df_axe_cert = df_programmé.groupby(['NIV1'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
		# print(df_axe_tot)
		# print(df_axe_cert)

		
		# Somme programmé par OS
		df_os_ue = df_programmé.groupby(['NIV4'])['UE'].sum()
		df_os_tot = df_programmé.groupby(['NIV4'])['Coût total en cours'].sum()
		df_os_cert = df_programmé.groupby(['NIV4'])['UE déjà versé dans les CSF envoyés AC (CSF)'].sum()
		# print(df_os_tot)
		
		#placer la somme FEDER par axe dans une liste
		tot_ue_axe = []
		tot_ue_os = []



		tot_tot_axe = []
		tot_tot_os = []

		tot_cert_axe = []
		tot_cert_os = []
		
		for axe in axes:
			try:
				tot_ue_axe.append(df_axe_ue[axe])
				tot_tot_axe.append(df_axe_tot[axe])
				tot_cert_axe.append(df_axe_tot[axe])
			except:
				pass
		

		#placer la somme FEDER par os dans une liste
		for os in oss:
			try:
				tot_ue_os.append(df_os_ue[os])
				tot_tot_os.append(df_os_tot[os])
				tot_cert_os.append(df_os_cert[os])
			except:
				pass



		

			# print(axes)
			# print(tot_ue_axe)
			
			# print(oss)
			# print(tot_ue_os)
		
			date = datetime.date.today()
			
			enveloppe = Enveloppe.objects.filter(user=user)
			somme_axe = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('axe').annotate(
				Montant_UE=Sum('montant_UE'),  
				Montant_CT=Sum('montant_CT'),
				Montant_Certif=Sum('DP_certif'),
				Montant_Payé=Sum('DP_payé'),
				Nombre = Count('numero_op'),
				 ))

			somme_OS = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('os').annotate(
			Montant_UE=Sum('montant_UE'), 
			Montant_CT=Sum('montant_CT'),
			Montant_Certif=Sum('DP_certif'),
			Montant_Payé=Sum('DP_payé'),
			Nombre = Count('numero_op'),
			 ))
		
			
		
			Axe_1 = somme_axe[0]
			Axe_2 = somme_axe[1]
			Axe_3 = somme_axe[2]
			Axe_4 = somme_axe[3]
			Axe_5 = somme_axe[4]
			Axe_6 = somme_axe[5]
			Axe_12 = somme_axe[6]
			Axe_13 = somme_axe[7]

			OS_1_1 = somme_OS[0]
			OS_1_2 = somme_OS[1]
			OS_1_3 = somme_OS[2]
			OS_1_4 = somme_OS[3]
			OS_2_1 = somme_OS[4]
			OS_2_2 = somme_OS[5]
			OS_2_3 = somme_OS[6]
			OS_3_1 = somme_OS[7]
			OS_3_2 = somme_OS[8]
			OS_3_3 = somme_OS[9]
			OS_4_1 = somme_OS[10]
			OS_4_2 = somme_OS[11]
			OS_4_3 = somme_OS[12]
			OS_4_4 = somme_OS[13]
			OS_5_1 = somme_OS[14]
			OS_5_2 = somme_OS[15]
			OS_6_1 = somme_OS[16]
			OS_6_2 = somme_OS[17]
			OS_12_1 = somme_OS[18]
			OS_13_1 = somme_OS[19]

			somme_UE = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_UE')))
			print('MARKER')
			print(somme_UE)

			somme_Certif = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_certif')))
			print(somme_Certif)

			query = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='Déposé') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='Déposé') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='Déposé')
			nombre_query = query.count()

			user = User.objects.get(id=request.user.id)
			query_difficulté = Dossier.objects.filter(user=user, date_dépôt__startswith='2016',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2017',  statut_macro='En instruction') |  Dossier.objects.filter(user=user, date_dépôt__startswith='2018',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2019',  statut_macro='En instruction') | Dossier.objects.filter(user=user, date_dépôt__startswith='2020',  statut_macro='En instruction')
			nombre_query_difficulté = query_difficulté.count()

			query_programmé_difficulté = Dossier.objects.filter(user=user, date_signature__startswith='2016',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2017',  statut_macro='Programmé') |  Dossier.objects.filter(user=user, date_signature__startswith='2018',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2019',  statut_macro='Programmé') | Dossier.objects.filter(user=user, date_signature__startswith='2020',  statut_macro='Programmé')
			nombre_query_programmé_difficulté = query_programmé_difficulté.count()
			
			context = {

			#'enveloppe':enveloppe,

			'liste_axe_top':liste_axe_top,
			'liste_num_top':liste_num_top,
			'liste_béné_top':liste_béné_top,
			'liste_statut_top':liste_statut_top,
			'liste_tot_top':liste_tot_top,
			'liste_ue_top':liste_ue_top,
			'liste_cert_top':liste_cert_top,
			'liste_libélé_top' : liste_libélé_top,


			'val_tot': val_tot,
			'val_ue' : val_ue,
			'val_cert':val_cert,
			'taux_certif': taux_certif,

			'top10':top10,

			'enveloppe':enveloppe,
			'somme_axe':somme_axe,

			'Axe_1': Axe_1,
			'Axe_2': Axe_2,
			'Axe_3': Axe_3,
			'Axe_4': Axe_4,
			'Axe_5': Axe_5,
			'Axe_6': Axe_6,
			'Axe_12': Axe_12,
			'Axe_13': Axe_13,

			'OS_1_1' : OS_1_1,
			'OS_1_2' : OS_1_2,
			'OS_1_3' : OS_1_3,
			'OS_1_4' : OS_1_4,
			'OS_2_1' : OS_2_1,
			'OS_2_2' : OS_2_2,
			'OS_2_3' : OS_2_3,
			'OS_3_1' : OS_3_1,
			'OS_3_2' : OS_3_2,
			'OS_3_3' : OS_3_3,
			'OS_4_1' : OS_4_1,
			'OS_4_2' : OS_4_2,
			'OS_4_3' :OS_4_3,
			'OS_4_4' : OS_4_4,
			'OS_5_1' : OS_5_1,
			'OS_5_2' : OS_5_2,
			'OS_6_1' : OS_6_1,
			'OS_6_2' : OS_6_2,
			'OS_12_1' : OS_12_1,
			'OS_13_1': OS_13_1,

			'somme_UE':somme_UE,
			'somme_Certif':somme_Certif,
			'query':query,
			'nombre_query':nombre_query,
			'query_difficulté':query_difficulté,
			'nombre_query_difficulté':nombre_query_difficulté,
			'query_programmé_difficulté':query_programmé_difficulté,
			'nombre_query_programmé_difficulté':nombre_query_programmé_difficulté,
			'date':date,


		
			}
			html = template.render(context)
			pdf = render_to_pdf('dash/test.html', context)
			return pdf

		# # except:
		# 	user = User.objects.get(id=request.user.id)
		# 	Dossier.objects.filter(user=user).delete()
		# 	return render(request, 'dash/home.html')

#####################################################################################################################
###################################### DETAIL VIEW #############################################################
#####################################################################################################################

def detail_view (request, numero_op):
	try:
		user  = User.objects.get(id=request.user.id)
		numero_op = Dossier.objects.get(numero_op = numero_op, user=user)
		print(numero_op)
		context = {'numero_op': numero_op}
		return render (request, 'dash/opération.html', context)
	except:
		return render(request, 'dash/erreur.html')

#####################################################################################################################
###################################### FIN DETAIL VIEW #############################################################
#####################################################################################################################

def suivi_indicateurs(request):
	user = User.objects.get(id=request.user.id)
	somme_indicateurs = (Indicateur.objects.filter(user=user).values('indicateur', 'libellé').annotate(
			valeur_prev=Sum('valeur_prev'), 
			valeur_conv=Sum('valeur_conv'),
			valeur_real=Sum('valeur_real'),

			 ))
	context = {

	'somme_indicateurs': somme_indicateurs,

	}

	return render(request, 'dash/suivi_indicateurs.html', context)


#####################################################################################################################
###################################### PORTEURS VIEW #############################################################
#####################################################################################################################

def porteur_privé(request):
	try:
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data
		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')

		df_privé = df[df['Nature_juridique'] == 'Privé']
		df_privé = df_privé[df_privé['Statut_macro']=='Programmé']

		nb_dossiers = df_privé['N_Dossier'].count()
		val_ue = (df_privé['UE'].sum(skipna=True)).round(3)
		val_CT = (df_privé['Coût_total_en_cours'].sum(skipna=True)).round(3)
		val_certif = (df_privé['UE_déjà_versé_dans_les_CSF_envoyés_AC_CSF'].sum(skipna=True)).round(3)

		enveloppe = Enveloppe.objects.filter(user=user)

		

		
		json_records = df_privé.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers':nb_dossiers,
		'val_ue':val_ue,
		'val_CT':val_CT,
		'val_certif':val_certif,
		'enveloppe':enveloppe,


		}

		return render(request, 'dash/porteur_privé.html', context)

	except:
		return render(request, 'dash/erreur.html')


def porteur_public(request):
	try:
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data
		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')

		df_public = df[df['Nature_juridique'] == 'Public']
		df_public = df_public[df_public['Statut_macro']=='Programmé']

		nb_dossiers = df_public['N_Dossier'].count()
		val_ue = (df_public['UE'].sum(skipna=True)).round(3)
		val_CT = (df_public['Coût_total_en_cours'].sum(skipna=True)).round(3)
		val_certif = (df_public['UE_déjà_versé_dans_les_CSF_envoyés_AC_CSF'].sum(skipna=True)).round(3)


		
		json_records = df_public.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers':nb_dossiers,
		'val_ue':val_ue,
		'val_CT':val_CT,
		'val_certif':val_certif,

		}


		return render(request, 'dash/porteur_public.html', context)

	except:
		return render(request, 'dash/erreur.html')


#####################################################################################################################
###################################### FIN PORTEURS VIEW #############################################################
#####################################################################################################################



#####################################################################################################################
###################################### TABLEAU DES DIRECTEURS #############################################################
#####################################################################################################################

def directeur(request):
	try:
		user  = User.objects.get(id=request.user.id)
		somme_OS = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('os').annotate(
			Montant_UE=Sum('montant_UE'), 
			Montant_CT=Sum('montant_CT'),
			Montant_Certif=Sum('DP_certif'),
			Montant_Payé=Sum('DP_payé'),
			Nombre = Count('numero_op'),
			 ))
		print(somme_OS)

		somme_Axe = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('axe').annotate(
			Montant_UE=Sum('montant_UE'),  
			Montant_CT=Sum('montant_CT'),
			Montant_Certif=Sum('DP_certif'),
			Montant_Payé=Sum('DP_payé'),
			Nombre = Count('numero_op'),
			 ))
		print(somme_Axe)

		somme_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('DI').annotate(
			Montant_UE=Sum('montant_UE'),  
			Montant_CT=Sum('montant_CT'),
			Montant_Certif=Sum('DP_certif'),
			Montant_Payé=Sum('DP_payé'),
			Nombre = Count('numero_op'),
			 ))

		somme_UE = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_UE')))
		somme_CT = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_CT')))
		somme_Certif = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_certif')))
		somme_Payé = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_payé')))
		nombre = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Count('numero_op')))

		enveloppe = Enveloppe.objects.filter(user=user)

		print(somme_DI)

		Axe_1 = somme_Axe[0]
		Axe_2 = somme_Axe[1]
		Axe_3 = somme_Axe[2]
		Axe_4 = somme_Axe[3]
		Axe_5 = somme_Axe[4]
		Axe_6 = somme_Axe[5]
		Axe_12 = somme_Axe[6]
		Axe_13 = somme_Axe[7]

		OS_1_1 = somme_OS[0]
		OS_1_2 = somme_OS[1]
		OS_1_3 = somme_OS[2]
		OS_1_4 = somme_OS[3]
		OS_2_1 = somme_OS[4]
		OS_2_2 = somme_OS[5]
		OS_2_3 = somme_OS[6]
		OS_3_1 = somme_OS[7]
		OS_3_2 = somme_OS[8]
		OS_3_3 = somme_OS[9]
		OS_4_1 = somme_OS[10]
		OS_4_2 = somme_OS[11]
		OS_4_3 = somme_OS[12]
		OS_4_4 = somme_OS[13]
		OS_5_1 = somme_OS[14]
		OS_5_2 = somme_OS[15]
		OS_6_1 = somme_OS[16]
		OS_6_2 = somme_OS[17]
		OS_12_1 = somme_OS[18]
		OS_13_1 = somme_OS[19]
		

		context={
		'somme_OS' : somme_OS,
		'somme_Axe' : somme_Axe,
		'somme_DI': somme_DI,


		'somme_UE': somme_UE,
		'somme_CT': somme_CT,
		'somme_Certif' : somme_Certif,
		'somme_Payé' : somme_Payé,
		'nombre' : nombre,

		'enveloppe': enveloppe,

		'Axe_1': Axe_1,
		'Axe_2': Axe_2,
		'Axe_3': Axe_3,
		'Axe_4': Axe_4,
		'Axe_5': Axe_5,
		'Axe_6': Axe_6,
		'Axe_12': Axe_12,
		'Axe_13': Axe_13,


		'OS_1_1' : OS_1_1,
		'OS_1_2' : OS_1_2,
		'OS_1_3' : OS_1_3,
		'OS_1_4' : OS_1_4,
		'OS_2_1' : OS_2_1,
		'OS_2_2' : OS_2_2,
		'OS_2_3' : OS_2_3,
		'OS_3_1' : OS_3_1,
		'OS_3_2' : OS_3_2,
		'OS_3_3' : OS_3_3,
		'OS_4_1' : OS_4_1,
		'OS_4_2' : OS_4_2,
		'OS_4_3' :OS_4_3,
		'OS_4_4' : OS_4_4,
		'OS_5_1' : OS_5_1,
		'OS_5_2' : OS_5_2,
		'OS_6_1' : OS_6_1,
		'OS_6_2' : OS_6_2,
		'OS_12_1' : OS_12_1,
		'OS_13_1': OS_13_1,


		'somme_UE':somme_UE,
		'somme_Certif':somme_Certif,

		
		}
		return render(request,'dash/tableau_directeurs.html', context)

	except:
		return render(request, 'dash/erreur.html')

#####################################################################################################################
###################################### FIN TABLEAU DES DIRECTEURS #############################################################
#####################################################################################################################


#####################################################################################################################
###################################### SFC ###########################################################################
#####################################################################################################################


def données_financières(request):
	try:
		user  = User.objects.get(id=request.user.id)
		somme_Axe = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('axe').annotate(
			Montant_CT=Sum('montant_CT'),
			Montant_public = Sum('montant_public'),
			Montant_CT_déposé = Sum('DP_CT_depot'),
			Nombre = Count('numero_op'),

			 ))
		print(somme_Axe)

		somme_public = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_public')))
		somme_CT_déposé = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_CT_depot')))
		somme_CT = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_CT')))
		nombre = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Count('numero_op')))


		

		somme_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').values('DI').annotate(  
			Montant_CT=Sum('montant_CT'),
			Montant_public = Sum('montant_public'),
			Montant_CT_déposé = Sum('DP_CT_depot'),
			Nombre = Count('numero_op'),
			 ))

		somme_public_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_public')))
		somme_CT_déposé_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('DP_CT_depot')))
		somme_CT_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Sum('montant_CT')))
		nombre_DI = (Dossier.objects.filter(user=user, statut_macro='Programmé').aggregate(Count('numero_op')))


		print(somme_DI)

		context= {
		'somme_Axe':somme_Axe,
		'somme_public': somme_public,
		'somme_CT_déposé': somme_CT_déposé,
		'somme_CT': somme_CT,
		'nombre': nombre,

		'somme_DI':somme_DI,
		'somme_public_DI': somme_public_DI,
		'somme_CT_déposé_DI': somme_CT_déposé_DI,
		'somme_CT_DI': somme_CT_DI,
		'nombre_DI': nombre_DI,

		}
		

		return render(request, 'dash/données_financères.html', context)
	except:
		return render(request, 'dash/csv.html')

def ramo(request):
	return render(request, 'dash/ramo.html')


#####################################################################################################################
###################################### FIN SFC ###########################################################################
#####################################################################################################################

#####################################################################################################################
###################################### RECHERCHE ###########################################################################
#####################################################################################################################


class RechercheListView(ListView):
	model = Dossier
	template_name = 'dash/recherche.html'
	
	def get_queryset(self):
		user = self.request.user.id
		query = self.request.GET.get('q')
		return Dossier.objects.filter(user = user, numero_op__icontains = query) | Dossier.objects.filter(user = user, porteur__icontains = query)| Dossier.objects.filter(user = user, libélé__icontains = query)| Dossier.objects.filter(user = user, descriptif__icontains = query) | Dossier.objects.filter(user = user, statut_macro__icontains = query)


#####################################################################################################################
###################################### FIN RECHERCHE ###########################################################################
#####################################################################################################################






def error(request):
	return render(request, 'dash/error.html')

def login_page(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username = username, password = password)

		if user is not None :
			login(request, user)
			return redirect('dash:home')
		else :
			messages.info(request, 'username or password is incorect')

	context = {}
	return render(request, 'login.html')

def register_page(request):
	form = CreateUserForm()

	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Le compte de ' + user + 'a été créé avec succès !')
			return redirect('dash:login')

	context = {'form': form}
	return render(request, 'dash/register.html', context)




#####################################################################################################################
###################################### IMPORTATION VIEW #############################################################
#####################################################################################################################


#importation des données synergie
@login_required
def CSV_update(request):
	if request.method == 'POST':
		p_form = CSV_load(request.POST, request.FILES, instance=request.user.profile)
		if p_form.is_valid:
			p_form.save()

			#create models 
			return redirect('dash:home')
	else:
		p_form = CSV_load()

	context = {'p_form':p_form}
	return render(request, 'dash/csv.html', context)


@login_required
def indicateurs_update(request):
	if request.method == 'POST':
		i_form = Indicateurs_load(request.POST, request.FILES, instance=request.user.profile)
		if i_form.is_valid:
			i_form.save()

			#create models 
			return redirect('dash:home')
	else:
		i_form = Indicateurs_load()

	context = {'i_form':i_form}
	return render(request, 'dash/indicateurs.html', context)

#####################################################################################################################
###################################### IMPORTATION VIEW FIN #############################################################
#####################################################################################################################
 

class Enveloppe_form(CreateView):
	model = Enveloppe
	fields = [
	'Enveloppe_totale',
	'Axe_1', 'OS_1_1', 'OS_1_2', 'OS_1_3', 'OS_1_4', 'OS_1_5', 'OS_1_6', 'OS_1_7', 'OS_1_8', 'OS_1_9', 'OS_1_10', 
	'Axe_2', 'OS_2_1', 'OS_2_2', 'OS_2_3', 'OS_2_4', 'OS_2_5', 'OS_2_6', 'OS_2_7', 'OS_2_8', 'OS_2_9', 'OS_2_10',
	'Axe_3', 'OS_3_1', 'OS_3_2', 'OS_3_3', 'OS_3_4', 'OS_3_5', 'OS_3_6', 'OS_3_7', 'OS_3_8', 'OS_3_9', 'OS_3_10',
	'Axe_4', 'OS_4_1', 'OS_4_2', 'OS_4_3', 'OS_4_4', 'OS_4_5', 'OS_4_6', 'OS_4_7', 'OS_4_8', 'OS_4_9', 'OS_4_10',
	'Axe_5', 'OS_5_1', 'OS_5_2', 'OS_5_3', 'OS_5_4', 'OS_5_5', 'OS_5_6', 'OS_5_7', 'OS_5_8', 'OS_5_9', 'OS_5_10',
	'Axe_6', 'OS_6_1', 'OS_6_2', 'OS_6_3', 'OS_6_4', 'OS_6_5', 'OS_6_6', 'OS_6_7', 'OS_6_8', 'OS_6_9', 'OS_6_10',
	'Axe_7', 'OS_7_1', 'OS_7_2', 'OS_7_3', 'OS_7_4', 'OS_7_5', 'OS_7_6', 'OS_7_7', 'OS_7_8', 'OS_7_9', 'OS_7_10',
	'Axe_8', 'OS_8_1', 'OS_8_2', 'OS_8_3', 'OS_8_4', 'OS_8_5', 'OS_8_6', 'OS_8_7', 'OS_8_8', 'OS_8_9', 'OS_8_10',
	'Axe_9', 'OS_9_1', 'OS_9_2', 'OS_9_3', 'OS_9_4', 'OS_9_5', 'OS_9_6', 'OS_9_7', 'OS_9_8', 'OS_9_9', 'OS_9_10',
	'Axe_10', 'OS_10_1', 'OS_10_2', 'OS_10_3', 'OS_10_4', 'OS_10_5', 'OS_10_6', 'OS_10_7', 'OS_10_8', 'OS_10_9', 'OS_10_10',
	'Axe_11', 'OS_11_1', 'OS_11_2', 'OS_11_3', 'OS_11_4', 'OS_11_5', 'OS_11_6', 'OS_11_7', 'OS_11_8', 'OS_11_9', 'OS_11_10',
	'Axe_12', 'OS_12_1', 'OS_12_2', 'OS_12_3', 'OS_12_4', 'OS_12_5', 'OS_12_6', 'OS_12_7', 'OS_12_8', 'OS_12_9', 'OS_12_10',
	'Axe_13', 'OS_13_1', 'OS_13_2', 'OS_13_3', 'OS_13_4', 'OS_13_5', 'OS_13_6', 'OS_13_7', 'OS_13_8', 'OS_13_9', 'OS_13_10',
	
	]

	def form_valid(self, form):
		form.instance.user = self.request.user
		Enveloppe.objects.filter(user=self.request.user).delete()
		form.save()
		return redirect('dash:home')
	




#####################################################################################################################
###################################### FIN IMPORTATION VIEW #############################################################
#####################################################################################################################



#####################################################################################################################
###################################### TABLES VIEW #############################################################
#####################################################################################################################


@login_required(login_url='dash:login')
def tables(request):
	try:
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')

		df_programmé = df[df['Statut_macro'] == 'Programmé']
		df_retiré = df[df['Statut_macro'] == 'Retiré']
		df_déposé = df[df['Statut_macro'] == 'Déposé']
		df_instruction = df[df['Statut_macro'] == 'En instruction']
		df_soldé = df[df['Statut_détaillé'] == 'Solde versé']

		nb_dossiers = df['N_Dossier'].count()
		nb_programmé= df_programmé['N_Dossier'].count()
		nb_retiré = df_retiré['N_Dossier'].count()
		nb_déposé = df_déposé['N_Dossier'].count()
		nb_instruction = df_instruction['N_Dossier'].count()
		nb_soldés = df_soldé['Statut_macro'].count()

		val_ue = (df_programmé['UE'].sum(skipna=True)).round(3)
		val_ue_inst = (df_instruction['UE'].sum(skipna=True)).round(3)
		val_ue_soldé = (df_soldé['UE'].sum(skipna=True)).round(3)


		
		json_records = df.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers':nb_dossiers,
		'nb_programmé':nb_programmé,
		'nb_instruction':nb_instruction,
		'nb_déposé': nb_déposé,
		'nb_retiré':nb_retiré,
		'nb_soldés':nb_soldés,
		'val_ue':val_ue,
		'val_ue_inst':val_ue_inst,
		'val_ue_soldé':val_ue_soldé,

		}

		return render(request, 'dash/tables.html', context)

	except:
		return render(request, 'dash/erreur.html')

@login_required(login_url='dash:login')
def tables_programmé(request):
	try:

		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data



		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')

		df_programmé = df[df['Statut_macro'] == 'Programmé']

		nb_dossiers = df_programmé['Statut_macro'].count()
		val_ue = (df_programmé['UE'].sum(skipna=True))
		val_tot = (df_programmé['Coût_total_en_cours'].sum(skipna=True))
		val_cert = (df_programmé['UE_déjà_versé_dans_les_CSF_envoyés_AC_CSF'].sum(skipna=True)).round(3)
		taux_certif = ((val_cert / val_ue)*100).round(0)
		
		json_records = df_programmé.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data, 
		'nb_dossiers': nb_dossiers,
		'val_ue':val_ue,
		'val_tot':val_tot,
		'val_cert': val_cert,
		'taux_certif':taux_certif,
		}

		return render(request, 'dash/tables_programmé.html', context)
	except:
		return render(request, 'dash/erreur.html')

	


@login_required(login_url='dash:login')
def tables_déposés(request):
	try:
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')
		
		df_déposé = df[df['Statut_macro'] == 'Déposé']

		nb_dossiers = df_déposé['Statut_macro'].count()
		val_ue = (df_déposé['UE'].sum(skipna=True))
		val_tot = (df_déposé['Coût_total_en_cours'].sum(skipna=True)).round(3)
		
		json_records = df_déposé.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers': nb_dossiers,
		'val_ue':val_ue,
		'val_tot':val_tot,

		}

		return render(request, 'dash/tables_déposés.html', context)
	except:
		return render(request, 'dash/erreur.html')

@login_required(login_url='dash:login')
def tables_instruction(request):
	try:

		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')
		
		df_instruction = df[df['Statut_macro'] == 'En instruction']

		nb_dossiers = df_instruction['Statut_macro'].count()
		val_ue = (df_instruction['UE'].sum(skipna=True))
		val_tot = (df_instruction['Coût_total_en_cours'].sum(skipna=True)).round(3)

		json_records = df_instruction.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers': nb_dossiers,
		'val_ue':val_ue,
		'val_tot':val_tot,

		}

		return render(request, 'dash/tables_instruction.html', context)
	except:
		return render(request, 'dash/erreur.html')

@login_required(login_url='dash:login')
def tables_soldés(request):
	try :
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')
		
		df_soldé = df[df['Statut_détaillé'] == 'Solde versé']

		nb_dossiers = df_soldé['Statut_macro'].count()
		val_ue = (df_soldé['UE'].sum(skipna=True)).round(3)
		val_tot = (df_soldé['Coût_total_en_cours'].sum(skipna=True)).round(3)
		val_cert = (df_soldé['UE_déjà_versé_dans_les_CSF_envoyés_AC_CSF'].sum(skipna=True)).round(3)
		taux_certif = ((val_cert / val_ue)*100).round(0)
		
		json_records = df_soldé.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data, 
		'nb_dossiers': nb_dossiers,
		'val_ue':val_ue,
		'val_tot':val_tot,
		'val_cert': val_cert,
		'taux_certif':taux_certif,

		}

		return render(request, 'dash/tables_soldés.html', context)
	except:
		return render(request, 'dash/erreur.html')

@login_required(login_url='dash:login')
def tables_retirés(request):
	try:
		user  = User.objects.get(id=request.user.id)
		csv_file = user.profile.user_data

		df = pd.read_csv(csv_file, delimiter=';', decimal=',')
		df = df.round(2)
		df.columns = df.columns.str.replace('(', '')
		df.columns = df.columns.str.replace(')', '')
		df.columns = df.columns.str.replace(' ', '_')
		df.columns = df.columns.str.replace('°', '')
		
		df_retiré = df[df['Statut_macro'] == 'Retiré']
		nb_dossiers = df_retiré['Statut_macro'].count()
		val_ue = (df_retiré['UE'].sum(skipna=True))
		val_tot = (df_retiré['Coût_total_en_cours'].sum(skipna=True)).round(3)

		json_records = df_retiré.to_json(orient ='records')
		data = []
		data = json.loads(json_records)
		context = {
		'd': data,
		'nb_dossiers': nb_dossiers,
		'val_ue':val_ue,
		'val_tot':val_tot,


		}

		return render(request, 'dash/tables_retirés.html', context)
	except:
		return render(request, 'dash/erreur.html')



#####################################################################################################################
###################################### FIN TABLES VIEW #############################################################
#####################################################################################################################



#####################################################################################################################
###################################### LOGIN/LOGOUT VIEW #############################################################
#####################################################################################################################
def erreur(request):
	return render(request, 'dash/erreur.html')

def logout_page(request):
	logout(request)
	return redirect('dash:login')

@login_required(login_url='dash:login')
def forgot_password(request):
	return render(request, 'dash/forgot-password.html')

@login_required(login_url='dash:login')
def charts(request):
	return render(request, 'dash/charts.html')

@login_required(login_url='dash:login')
def cards(request):
	return render(request,'dash/cards.html')


#####################################################################################################################
###################################### FIN LOGIN/LOGOUT VIEW #############################################################
#####################################################################################################################


import arcpy
import os
from arcpy.sa import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = raw_input('ingrese carpeta de trabajo:')
carpeta = arcpy.env.workspace

#Inputs para el proceso. Shape de demanda, campo id demanda, campo volumen demanda, campo atraccion total, shape oferta.
nombre_polos = raw_input('ingrese polos:')
nombre_fincas = raw_input('ingrese fincas:')
polos_feat = os.path.join(carpeta, nombre_polos)
fincas_feat = os.path.join(carpeta, nombre_fincas)
polos_id = 'numero'
polos_vol = 'volumen'
polos_lyr = 'polos_layer'
arcpy.MakeFeatureLayer_management(polos_feat, polos_lyr)

#Listas de id polos y volumen para las iteraciones
lista_id = [row[0] for row in arcpy.da.SearchCursor(polos_feat, [polos_id])]
lista_volumen = [row[0] for row in arcpy.da.SearchCursor(polos_feat, [polos_vol])]
lista_prob = []
lista_atrac = []

#Calcular distancias desde demanda hasta oferta y los valores de atraccion
for i, j in zip(lista_id, lista_volumen):
    donde = '{0} = {1}'.format(polos_id, i)
    campo_dist = 'dist_{0}'.format(i)
    campo_atrac = 'atrac_{0}'.format(i)    
    arcpy.SelectLayerByAttribute_management(polos_lyr,"NEW_SELECTION",donde)
    arcpy.Near_analysis(fincas_feat, polos_lyr)
    arcpy.AddField_management(fincas_feat, campo_dist, "FLOAT")
    arcpy.CalculateField_management(fincas_feat,campo_dist, '!NEAR_DIST!', "PYTHON")
    arcpy.DeleteField_management(fincas_feat, "NEAR_DIST")
    arcpy.AddField_management(fincas_feat, campo_atrac, "FLOAT")
    donde_atraccion = '{0} / (!{1}! ** 2)'.format(j, campo_dist)
    arcpy.CalculateField_management(fincas_feat, campo_atrac, donde_atraccion, "PYTHON")
    lista_atrac.append(campo_atrac)

# Calcular la atraccion total
arcpy.AddField_management(fincas_feat, 'tot', "FLOAT")
lista_atrac.append('tot')
with arcpy.da.UpdateCursor(fincas_feat, lista_atrac) as cursor:
    for row in cursor:
        total = sum(row[:-1])
        row[-1] = total
        cursor.updateRow(row)
del cursor
# Calcular probabilidades
for i, j in zip(lista_id, lista_atrac[:-1]):
    campo_prob = 'prob_{0}'.format(i)
    donde_prob = '!{0}! / !tot!'.format(j)
    arcpy.AddField_management(fincas_feat, campo_prob, "FLOAT")
    arcpy.CalculateField_management(fincas_feat,campo_prob, donde_prob, "PYTHON")
    lista_prob.append(campo_prob)
 
#Definicion de las cuencas.

arcpy.AddField_management(fincas_feat, 'maxValue', 'FLOAT') 
arcpy.AddField_management(fincas_feat, 'maxName', 'TEXT')

n = len(lista_prob)
lista_cursor = lista_prob[:]
lista_cursor.extend(['maxValue', 'maxName'])

with arcpy.da.UpdateCursor(fincas_feat, lista_cursor) as cursor:
    for row in cursor:
        maxVal = max(row[:n])
        maxFld = lista_cursor[row.index(maxVal)]
        row[-2] = maxVal
        row[-1] = maxFld
        cursor.updateRow(row)
del cursor
                                    

# -*- coding: utf-8 -*-
"""
Created on Mon May 13 23:10:18 2019

@author: ANUDEEP AKKANA
"""


from gurobipy import*
import os
import xlrd

book = xlrd.open_workbook(os.path.join("pickup and delivery.xlsx"))



Node=[]
Demand={}           #Demand in Thousands
Distance={}         #Distance in kms
VehicleNum=[]       #Vehicle number




sh = book.sheet_by_name("Demand")
i = 1
while True:
    try:
        sp = sh.cell_value(i,0)
        Node.append(sp)
        Demand[sp]=sh.cell_value(i,1)
        i = i + 1   
    except IndexError:
        break
    
sh = book.sheet_by_name("VehicleNum")

i = 1
while True:
    try:
        sp = sh.cell_value(i,0)
        VehicleNum.append(sp)
        i = i + 1   
    except IndexError:
        break
cost={}
sh = book.sheet_by_name("Cost")
i = 1
for P in Node:
    j = 1
    for Q in Node:
        cost[P,Q] = sh.cell_value(i,j)
        j += 1
    i += 1
sh = book.sheet_by_name("Distance")
i = 1
for P in Node:
    j = 1
    for Q in Node:
        Distance[P,Q] = sh.cell_value(i,j)
        j += 1
    i += 1 
Aij = {}
sh = book.sheet_by_name("Aij")
i = 1
for P in Node:
    j = 1
    for Q in Node:
        Aij[P,Q] = sh.cell_value(i,j)
        j += 1
    i += 1
    
numberOfVehicle=2

K=numberOfVehicle

m=Model("Pick_up_and_Delivery")


m.modelSense=GRB.MINIMIZE
Q = 20              #vehicle capacity
xijk=m.addVars(Node,Node,VehicleNum,vtype=GRB.BINARY,name='X_ijk')
fij=m.addVars(Node,Node,vtype=GRB.INTEGER,name='f_ijk')
#Uik=m.addVars(Node,VehicleNum,vtype=GRB.CONTINUOUS,name='Uik')


m.setObjective(sum((cost[i,j]*xijk[i,j,k] for i in Node for j in Node for k in VehicleNum if  Aij[i,j] == 1)))

for i in Node :
    if i!='Depot':
        m.addConstr(sum(xijk[i,j,k] for j in Node for k in VehicleNum if  Aij[i,j] == 1)==1)  
          
for i in Node:
    for k in VehicleNum:
        m.addConstr(sum(xijk[i,j,k] for j in Node if  Aij[i,j] == 1)-sum(xijk[j,i,k] for j in Node if  Aij[i,j] == 1)==0)
      
for i in Node:
    if i!= 'Depot':
        m.addConstr(sum(fij[j,i] for j in Node if  Aij[i,j] == 1)-sum(fij[i,j] for j in Node if  Aij[i,j] == 1) == Demand[i] ) 
for i in Node:
    for j in Node:
        m.addConstr(fij[i,j]>=0) 
for i in Node:
    for j in Node:
        if Aij[i,j] == 1:
            m.addConstr((Q*(sum(xijk[i,j,k] for k in VehicleNum)))>=fij[i,j])

for i in Node:
    for j in Node:
        if(i!='Depot'):
            if(j!='Depot'):
                m.addConstr(sum(xijk[i,j,k] for k in VehicleNum)<=4)
                                 

                               
m.write('Pickupanddelivery.lp')

m.optimize()
                            
for v in m.getVars():
    if v.x > 0.01:
        print(v.varName, v.x)
print('Objective:',m.objVal)
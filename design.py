from cmath import pi
from re import X
from tkinter import Y
import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd
import math

# UTM32 Coordinates of the Potential Drilling Site and Reservoir Target
res_target_easting = 694043 #input("Please Enter Reservoir Target Easting: ")
res_target_northing = 5313126 #input("Please Enter Reservoir Target Northing: ")
res_target_lat = 47.94204 #input("Please Enter Reservoir Target Latitude: ")
res_target_long = 11.59845 #input("Please Enter Reservoir Target Longitude: ")

pds_easting = 694548 #input("Please Enter Potential Drilling Site Easting: ")
pds_northing = 5313173 #input("Please Enter Potential Drilling Site Northing: ")
pds_lat = 47.94231 #input("Please Enter Potential Drill Site Latitude: ")
pds_long = 11.60522 #input("Please Enter Potential Drill Site Longitude: ")

def calc_bearing(pointA, pointB): # Calculates the Azimuth of the Reservoir Target w.r.t Potential Drilling Site
    deg2rad = math.pi / 180
    latA = pointA[0] * deg2rad 
    latB = pointB[0] * deg2rad 
    lonA = pointA[1] * deg2rad 
    lonB = pointB[1] * deg2rad 

    delta_ratio = math.log(math.tan(latB/ 2 + math.pi / 4) / math.tan(latA/ 2 + math.pi / 4))
    delta_lon = abs(lonA - lonB)

    delta_lon %= math.pi
    bearing = math.atan2(delta_lon, delta_ratio)/deg2rad
    return bearing

g_point1 = (pds_lat, pds_long)
g_point2 = (res_target_lat, res_target_long)

print("Azimuth of the Reservoir Target w.r.t Potential Drilling Site is", calc_bearing(g_point1, g_point2), "degrees")

# script for returning elevation from lat, long, based on open elevation data which in turn is based on SRTM
def get_elevation(lat, long):
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    r = requests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    xyz = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
    return xyz

elevation = get_elevation(pds_lat, pds_long)
tvdinm = elevation + 3250 #input("Please Enter True Vertical Depth: ")
tvdinft = tvdinm*3
print("The True Vertical Depth is", tvdinm, "metres and", tvdinft, "in feet.")

kopinm = 500 #input("Please Enter Kick off Point: ")
kopinft = kopinm*3
print("The Kick off Point is", kopinft, "feet.")

var1 = (res_target_easting - pds_easting)*(res_target_easting - pds_easting) + (res_target_northing - pds_northing)*(res_target_northing - pds_northing)
hdist = math.sqrt(var1)
print("The Horizontal Distance between the Potential Drilling Site and the Reservoir Target is", hdist, "feet.")

# Target Bearing Beta
var2 = (res_target_easting - pds_easting)/(res_target_northing - pds_northing)
beta = math.atan(var2)
print("The Target Bearing is", beta, "degrees.")

br = 1.5 #input("Please Input the Build Rate: ")
R = 18000/(pi*br)

# Max Angle of Inclination 
var3 = tvdinft - kopinft
var4 = hdist - R
a = math.atan(var4/var3)
var5 = R*(math.cos(a))
b = math.asin(var5/var3)
alpha = a + b 
print("Max Angle of Inclination", alpha, "degrees.")

#Coordinates of the End of Build Section
tvdateob = kopinft + R*(math.sin(alpha))
var6 = 1-(math.cos(alpha))
hdistateob = R*var6
mdateob = kopinft + 100*(alpha/br)
print("The Coordinates of EOB are", tvdateob, ",", hdistateob, "and the measured depth at EOB is", mdateob, "feet.")

mdattarget = mdateob + (tvdinft - tvdateob)/math.cos(alpha)
print("The Measured depth at Target is ", mdattarget, "feet.")

print("The Well Path is Loading, Please wait for a few moments....")


# Adjusted code for smoother 3D plot with more points for smooth transition
num_points = 100  # Increase number of points for smoother curve
build_section = np.linspace(0, alpha, num_points//2)  # More points for smooth build-up
hold_section = np.ones(num_points//2) * alpha  # Hold angle at max inclination

# Creating more points for smooth curvature transition
X = np.concatenate((kopinft + R * np.sin(build_section), np.linspace(tvdateob, tvdinft, num_points//2)))
Y = np.concatenate((R * (1 - np.cos(build_section)), np.linspace(hdistateob, hdist, num_points//2)))
Z = np.zeros_like(X)  # For 3D plot, keeping Z-axis constant here

# 3D Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(X, Y, Z, c='r', marker='o')  # Plot the well path

ax.set_xlabel('Depth in ft.')
ax.set_ylabel('Distance from Potential Drilling Site in ft.')
ax.set_zlabel('Azimuth')

plt.show()

# Adjusted 2D Plot
fig, ax = plt.subplots()

ax.plot(X, Y, c='r', marker='o')  # 2D plot of the well path
ax.set_xlabel('Depth in ft.')
ax.set_ylabel('Distance from Potential Drilling Site in ft.')

plt.show()

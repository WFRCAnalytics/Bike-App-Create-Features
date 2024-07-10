'''

create-bike-features.py
Josh Reynolds - jreynolds@wfrc.org
2024-07-08

This script pulls down the most recent copies of the utah roads and 
trails & pathways datasets (hosted by UGRC), merges and formats them, 
and determines its best bike feature as well as which side of the 
road the feature is on. The final products are 1) existing and 
2) planned line layers for the wfrc-bike-app.

'''

import arcpy
from arcpy import env
import os
import numpy as np
from arcgis import GIS
from arcgis.features import GeoAccessor
from arcgis.features import GeoSeriesAccessor
import pandas as pd
import numbers

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "90%"


def determine_direction_from_angle(angle):
     
    if isinstance(angle, numbers.Number):
        
        if angle < 337.5 and angle > 292.5:
            direction = 'NW'
        elif angle == 337.5:
            direction = 'NNW'
        elif (angle >= 0 and angle < 22.5) or (angle > 337.5 and angle <= 360):
            direction = 'N'
        elif angle == 22.5:
            direction = 'NNE'
        elif angle < 67.5 and angle > 22.5:
            direction = 'NE'
        elif angle == 67.5:
            direction = 'ENE'
        elif angle < 112.5 and angle > 67.5:
            direction = 'E'
        elif angle == 112.5:
            direction = 'ESE'
        elif angle < 157.5 and angle > 112.5:
            direction = 'SE'
        elif angle == 157.5:
            direction = 'SSE'
        elif angle < 202.5 and angle > 157.5:
            direction = 'S'
        elif angle == 202.5:
            direction = 'SSW'
        elif angle < 247.5 and angle > 202.5:
            direction = 'SW'
        elif angle == 247.5:
            direction = 'WSW'
        elif angle < 292.5 and angle > 247.5:
            direction = 'W'
        elif angle == 292.5:
            direction = 'WNW'
    else:
        direction = 'NA'
    
    return direction    

def determine_primary_bike_feature_and_side(row):


    # lookup table for bike facility and rankings
    bike_lookup = {
    '1A':3, # 1A Cycle track, at-grade, protected with parking
    '1B':2, # 1B Cycle track, protected with barrier
    '1C':1, # 1C Cycle track, raised and curb separated (may be multiuse with peds)
    '1D':3, # 1D Cycle track, bi-directional
    '1E':3, # 1E Cycle track, center-running 
    '2A':4, # 2A Buffered bike lane
    '2B':5, # 2B Bike lane
    '2C':4, # 2C Bi-directional buffered bike lane
    '3A':6, # 3A Shoulder bikeway
    '3B':7, # 3B Marked shared roadway
    '3C':8, # 3C Signed shared roadway
    '1': 1, # 1 Cycle track, unspecified 
    '2':5, # 2 Bike lane, unspecified 
    '3':8, # 3 Other bike route, unspecified
    'PP':1, # Parallel Bike Path, Paved
    'PU':9, # Parallel Bike Path, Unpaved
    'UN':10, # Unknown Category,
    'TrPw':1 # Trail or Pathway
    }

    #-----------------------------------
    # Existing Bike Facilities
    #-----------------------------------

    # if there are bike features on both sides
    if row['BIKE_L'] in bike_lookup.keys() and row['BIKE_R'] in bike_lookup.keys(): 
        # get the rank for each facility
        bl_rank = bike_lookup[row['BIKE_L']]
        br_rank = bike_lookup[row['BIKE_R']]

        # if bike_left's facility is better than bike_right's or they tie
        if (bl_rank < br_rank) or (bl_rank == br_rank):
            primary_feature = row['BIKE_L']
            secondary_feature = row['BIKE_R']

            if row['CompassA'] >= 90:
                primary_feature_degrees = row['CompassA'] - 90
            elif row['CompassA'] < 90:
                primary_feature_degrees = row['CompassA'] + 270
            else:
                 primary_feature_degrees = 'NA'

            if primary_feature_degrees =='NA':
                 secondary_feature_degrees = 'NA'
            elif primary_feature_degrees <= 180:
                    secondary_feature_degrees = primary_feature_degrees + 180
            elif primary_feature_degrees > 180:
                    secondary_feature_degrees = primary_feature_degrees - 180

        # if bike_right's facility is better than bike_left's
        if br_rank < bl_rank:
            primary_feature = row['BIKE_R']
            secondary_feature = row['BIKE_L']

            if row['CompassA'] <= 270:
                primary_feature_degrees = row['CompassA'] + 90
            elif row['CompassA'] > 270:
                primary_feature_degrees = row['CompassA'] - 270
            else:
                 primary_feature_degrees = 'NA'

            if primary_feature_degrees =='NA':
                 secondary_feature_degrees = 'NA'
            elif primary_feature_degrees <= 180:
                    secondary_feature_degrees = primary_feature_degrees + 180
            elif primary_feature_degrees > 180:
                    secondary_feature_degrees = primary_feature_degrees - 180

    # if bike right does not have a facility
    elif row['BIKE_L'] in bike_lookup.keys() and row['BIKE_R'] not in bike_lookup.keys(): 

        primary_feature = row['BIKE_L']
        secondary_feature  = "NA"
        secondary_feature_degrees ='NA'

        if row['CompassA'] <= 270:
            primary_feature_degrees = row['CompassA'] + 90
        elif row['CompassA'] > 270:
            primary_feature_degrees = row['CompassA'] - 270
        else:
            primary_feature_degrees = 'NA'
    
    # if bike left does not have a facility
    elif row['BIKE_R'] in bike_lookup.keys() and row['BIKE_L'] not in bike_lookup.keys(): 
        
        primary_feature = row['BIKE_R']
        secondary_feature  = "NA"
        secondary_feature_degrees ='NA'

        if row['CompassA'] <= 270:
            primary_feature_degrees = row['CompassA'] + 90
        elif row['CompassA'] > 270:
            primary_feature_degrees = row['CompassA'] - 270
        else:
            primary_feature_degrees = 'NA'

    else:
         primary_feature = 'NA'
         secondary_feature = 'NA'
         primary_feature_degrees = 'NA'
         secondary_feature_degrees = 'NA'

    row['Facility1'] = primary_feature
    row['Facility2'] = secondary_feature
    row['Facility1_Side'] = determine_direction_from_angle(primary_feature_degrees)
    row['Facility2_Side'] = determine_direction_from_angle(secondary_feature_degrees)


    #-----------------------------------
    # Planned Bike Facilities
    #-----------------------------------

    # are facilities planned for both sides?
    if row['BIKE_PLN_L'] in bike_lookup.keys() and row['BIKE_PLN_R'] in bike_lookup.keys(): 
        
        bl_rank = bike_lookup[row['BIKE_PLN_L']]
        br_rank = bike_lookup[row['BIKE_PLN_R']]

        # if bike_left's facility is better than bike_right's or they tie
        if (bl_rank < br_rank) or (bl_rank == br_rank):
            planned_primary_feature = row['BIKE_PLN_L']
            planned_secondary_feature = row['BIKE_PLN_R']

            if row['CompassA'] >= 90:
                planned_primary_feature_degrees = row['CompassA'] - 90
            elif row['CompassA'] < 90:
                planned_primary_feature_degrees = row['CompassA'] + 270
            else:
                planned_primary_feature_degrees = 'NA'

            
            if planned_primary_feature_degrees =='NA':
                 planned_secondary_feature_degrees = 'NA'
            elif planned_primary_feature_degrees <= 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
            elif planned_primary_feature_degrees > 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

        # if bike_right's facility is better than bike_left's
        if br_rank < bl_rank:
            planned_primary_feature = row['BIKE_PLN_R']
            planned_secondary_feature = row['BIKE_PLN_L']

            if row['CompassA'] <= 270:
                planned_primary_feature_degrees = row['CompassA'] + 90
            elif row['CompassA'] > 270:
                planned_primary_feature_degrees = row['CompassA'] - 270
            else:
                planned_primary_feature_degrees = 'NA'

            if planned_primary_feature_degrees =='NA':
                 planned_secondary_feature_degrees = 'NA'
            elif planned_primary_feature_degrees <= 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
            elif planned_primary_feature_degrees > 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

    # if a new facility is only planned for left
    elif row['BIKE_PLN_L'] in bike_lookup.keys() and row['BIKE_PLN_R'] not in bike_lookup.keys(): 
        
        bl_rank = bike_lookup[row['BIKE_PLN_L']]
        
        # is there an existing facility on bike right?
        if row['BIKE_R'] in bike_lookup.keys():

            br_rank = bike_lookup[row['BIKE_R']]

            # if bike_left's facility is better than bike_right's or they tie
            if (bl_rank < br_rank) or (bl_rank == br_rank):
                planned_primary_feature = row['BIKE_PLN_L']
                planned_secondary_feature = row['BIKE_R']

                if row['CompassA'] >= 90:
                    planned_primary_feature_degrees = row['CompassA'] - 90
                elif row['CompassA'] < 90:
                    planned_primary_feature_degrees = row['CompassA'] + 270
                else:
                    planned_primary_feature_degrees = 'NA'

                
                if planned_primary_feature_degrees =='NA':
                    planned_secondary_feature_degrees = 'NA'
                elif planned_primary_feature_degrees <= 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                elif planned_primary_feature_degrees > 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

            # if bike_right's facility is better than bike_left's
            if br_rank < bl_rank:
                planned_primary_feature = row['BIKE_R']
                planned_secondary_feature = row['BIKE_PLN_L']

                if row['CompassA'] <= 270:
                    planned_primary_feature_degrees = row['CompassA'] + 90
                elif row['CompassA'] > 270:
                    planned_primary_feature_degrees = row['CompassA'] - 270
                else:
                    planned_primary_feature_degrees = 'NA'

                if planned_primary_feature_degrees =='NA':
                    planned_secondary_feature_degrees = 'NA'
                elif planned_primary_feature_degrees <= 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                elif planned_primary_feature_degrees > 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

        else:
            planned_primary_feature = row['BIKE_PLN_L']
            if row['CompassA'] <= 270:
                planned_primary_feature_degrees = row['CompassA'] + 90
            if row['CompassA'] > 270:
                planned_primary_feature_degrees = row['CompassA'] - 270
            else:
                planned_primary_feature_degrees = 'NA'

            planned_secondary_feature = 'NA'
            planned_secondary_feature_degrees = 'NA'
          
    # if a new facility is only planned for right
    elif row['BIKE_PLN_R'] in bike_lookup.keys() and row['BIKE_PLN_L'] not in bike_lookup.keys(): 
        
        br_rank = bike_lookup[row['BIKE_PLN_R']]
        
        # is there an existing facility on bike left?
        if row['BIKE_L'] in bike_lookup.keys():

            bl_rank = bike_lookup[row['BIKE_L']]

            # if bike_left's facility is better than bike_right's or they tie
            if (bl_rank < br_rank) or (bl_rank == br_rank):
                planned_primary_feature = row['BIKE_L']
                planned_secondary_feature = row['BIKE_PLN_R']

                if row['CompassA'] >= 90:
                    planned_primary_feature_degrees = row['CompassA'] - 90
                if row['CompassA'] < 90:
                    planned_primary_feature_degrees = row['CompassA'] + 270

                if planned_primary_feature_degrees =='NA':
                    planned_secondary_feature_degrees = 'NA'
                elif planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                elif planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

            # if bike_right's facility is better than bike_left's
            if br_rank < bl_rank:
                planned_primary_feature = row['BIKE_PLN_R']
                planned_secondary_feature = row['BIKE_L']

                if row['CompassA'] <= 270:
                    planned_primary_feature_degrees = row['CompassA'] + 90
                elif row['CompassA'] > 270:
                    planned_primary_feature_degrees = row['CompassA'] - 270
                else:
                    planned_primary_feature_degrees = 'NA'

                if planned_primary_feature_degrees =='NA':
                    planned_secondary_feature_degrees = 'NA'
                elif planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                elif planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180
        else:
            planned_primary_feature = row['BIKE_PLN_R']
            if row['CompassA'] <= 270:
                planned_primary_feature_degrees = row['CompassA'] + 90
            elif row['CompassA'] > 270:
                planned_primary_feature_degrees = row['CompassA'] - 270
            else:
                planned_primary_feature_degrees = 'NA'
            
            planned_secondary_feature = 'NA'
            planned_secondary_feature_degrees = 'NA'
    else:
         planned_primary_feature = 'NA'
         planned_secondary_feature = 'NA'
         planned_primary_feature_degrees = 'NA'
         planned_secondary_feature_degrees = 'NA'

    row['PlannedFacility1'] = planned_primary_feature
    row['PlannedFacility2'] = planned_secondary_feature
    row['PlannedFacility1_Side'] = determine_direction_from_angle(planned_primary_feature_degrees)
    row['PlannedFacility2_Side'] = determine_direction_from_angle(planned_secondary_feature_degrees)
         
    return row

def main():
    print('begin script!')
    # create output directories    
    if not os.path.exists('Outputs'):
        os.makedirs('Outputs')
        
    print('creating output directories...')
    outputs = ['.\\Outputs', "scratch.gdb", 'wfrc_bike_map_features.gdb', 'wfrc_bike_map_planned_features.gdb']
    gdb = os.path.join(outputs[0], outputs[1])
    gdb2 = os.path.join(outputs[0], outputs[2])
    gdb3 = os.path.join(outputs[0], outputs[3])

    if not arcpy.Exists(gdb):
        arcpy.CreateFileGDB_management(outputs[0], outputs[1])

    if not arcpy.Exists(gdb2):
        arcpy.CreateFileGDB_management(outputs[0], outputs[2])

    if not arcpy.Exists(gdb3):
        arcpy.CreateFileGDB_management(outputs[0], outputs[3])


    # store paths to datasets
    roads = 'https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/UtahRoads/FeatureServer/0'
    trails = 'https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/TrailsAndPathways/FeatureServer/0'
    counties = r'.\Inputs\WFRC_MPO_AOG_Counties.shp'
    cities = r'.\Inputs\Cities.shp'

    # pull down data layers from AGOL with predefined filter
    print('retrieving data layers...')
    roads_lyr = arcpy.MakeFeatureLayer_management(roads, 'roads_lyr', where_clause=""" (((BIKE_L IS NOT NULL AND BIKE_L NOT IN ('', ' ')) OR (BIKE_R IS NOT NULL AND BIKE_R NOT IN ('', ' '))) OR ((BIKE_PLN_L IS NOT NULL AND BIKE_PLN_L NOT IN ('', ' ')) OR (BIKE_PLN_R IS NOT NULL AND BIKE_PLN_R NOT IN ('', ' ')))) """)
    trails_lyr = arcpy.MakeFeatureLayer_management(trails, 'trails_lyr', where_clause=""" DesignatedUses NOT IN ('Pedestrian') And 
                                                                                        CartoCode NOT IN ('1 - Hiking Only', '7 - Steps') """)

    # filter the layers by the counties of interest
    arcpy.management.SelectLayerByLocation(roads_lyr, 'INTERSECT',  counties)
    arcpy.management.SelectLayerByLocation(trails_lyr, 'INTERSECT',  counties)

    # merge both roads and trails and add unique id
    print('merging roads and trails...')
    bike_features = arcpy.management.Merge([trails_lyr,roads_lyr], output=os.path.join(gdb, 'bike_features'), add_source='ADD_SOURCE_INFO')
    arcpy.management.AddField(bike_features, 'UID', "LONG")
    arcpy.management.CalculateField(bike_features, "UID", '!OBJECTID!', "PYTHON3")
    bike_features_df = pd.DataFrame.spatial.from_featureclass(bike_features[0])

    # spatial join for cities attribute
    target_features = bike_features 
    join_features = cities
    output_features = os.path.join(gdb, "bf_cities_sj")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(target_features)
    fieldmappings.addTable(join_features)
    bf_cities_sj = arcpy.SpatialJoin_analysis(target_features, join_features, output_features,'JOIN_ONE_TO_ONE', "KEEP_ALL", fieldmappings, match_option="HAVE_THEIR_CENTER_IN")
    bf_cities_sj_df = pd.DataFrame.spatial.from_featureclass(bf_cities_sj[0])[['UID','CITY']].copy()

    # add directionality to line features
    print('computing directional mean...')
    bf_dm = arcpy.stats.DirectionalMean(bike_features, os.path.join(gdb, "bike_features_directional_mean"), "DIRECTION", "uid")
    bf_dm_df = pd.DataFrame.spatial.from_featureclass(bf_dm[0])[['UID', 'CompassA']].copy()

    # data formatting
    bf_all = bike_features_df.merge(bf_dm_df, on='UID', how='left').merge(bf_cities_sj_df, on='UID', how='left')
    bf_all = bf_all[['UID', 'Status','CartoCode', 'FULLNAME', 'PrimaryName',  'BIKE_L','BIKE_R','BIKE_PLN_L','BIKE_PLN_R', 'MERGE_SRC', 'CompassA', 'CITY', 'County','GlobalID', 'SHAPE']]
    bf_all.loc[(bf_all['MERGE_SRC'] == 'trails_lyr') & (bf_all['Status'].isin(['Future', 'Proposed', 'PROPOSED'])==False), 'BIKE_L'] = 'TrPw'
    bf_all.loc[(bf_all['MERGE_SRC'] == 'trails_lyr') & (bf_all['Status'].isin(['Future', 'Proposed', 'PROPOSED'])==False), 'BIKE_R'] = 'TrPw'

    # planned trails
    bf_all.loc[(bf_all['MERGE_SRC'] == 'trails_lyr') & (bf_all['Status'].isin(['Future', 'Proposed', 'PROPOSED'])==True), 'BIKE_PLN_L'] = 'TrPw'
    bf_all.loc[(bf_all['MERGE_SRC'] == 'trails_lyr') & (bf_all['Status'].isin(['Future', 'Proposed', 'PROPOSED'])==True), 'BIKE_PLN_R'] = 'TrPw'

    # create source field
    bf_all.loc[bf_all['MERGE_SRC'].isin(['roads_lyr']) == True, 'SOURCE'] = 'Utah Roads'
    bf_all.loc[bf_all['MERGE_SRC'].isin(['trails_lyr']) == True, 'SOURCE'] = 'Trails Pathways'
    
    # transfer name field
    bf_all.loc[bf_all['MERGE_SRC'].isin(['roads_lyr']) == True, 'NAME'] = bf_all['FULLNAME']
    bf_all.loc[bf_all['MERGE_SRC'].isin(['trails_lyr']) == True, 'NAME'] = bf_all['PrimaryName']

    # determine the bike feature order and side
    print('determining primary bike feature and side...')
    bf_all_processed = bf_all.apply(determine_primary_bike_feature_and_side, axis=1)

    # data formatting, split existing and planned features
    bf_all_processed.rename({'CartoCode':'CARTOCODE', 'County':'COUNTY', 'GlobalID':'SOURCE_ID'},axis=1, inplace=True)
    bf_all_processed['NOTES'] = np.nan
    planned_bf = bf_all_processed[(bf_all_processed['PlannedFacility1'] != 'NA') & (bf_all_processed['PlannedFacility2'] != 'NA')].copy()
    planned_bf = planned_bf[['UID', 'CITY', 'COUNTY', 'NAME', 'PlannedFacility1','PlannedFacility2', 'PlannedFacility1_Side', 'PlannedFacility2_Side', 'NOTES', 'CARTOCODE', 'SOURCE', 'SOURCE_ID', 'SHAPE']].copy()
    existing_bf = bf_all_processed[(bf_all_processed['Facility1'] != 'NA') & (bf_all_processed['Facility2'] != 'NA')].copy()
    existing_bf = existing_bf[['UID', 'CITY', 'COUNTY', 'NAME', 'Facility1','Facility2', 'Facility1_Side', 'Facility2_Side', 'NOTES', 'CARTOCODE', 'SOURCE', 'SOURCE_ID', 'SHAPE']].copy()

    # export as geodatabase feature class
    print('exporting data layers...')
    planned_bf.spatial.to_featureclass(location=os.path.join(gdb3, 'planned_bike_features'), sanitize_columns=False)
    existing_bf.spatial.to_featureclass(location=os.path.join(gdb2, 'bike_features'), sanitize_columns=False)
    print('end script!')

if __name__ == "__main__":
    main()


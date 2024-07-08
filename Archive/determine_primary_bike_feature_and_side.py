def determine_primary_bike_feature_and_side(_degrees, _bike_left=None, _bike_right=None, _planned_bike_left=None, _planned_bike_right=None):


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
    if _bike_left in bike_lookup.keys() and _bike_right in bike_lookup.keys(): 
        # get the rank for each facility
        bl_rank = bike_lookup[_bike_left]
        br_rank = bike_lookup[_bike_right]

        # if bike_left's facility is better than bike_right's or they tie
        if (bl_rank < br_rank) or (bl_rank == br_rank):
            primary_feature = _bike_left
            secondary_feature = _bike_right

            if _degrees >= 90:
                primary_feature_degrees = _degrees - 90
            if _degrees < 90:
                primary_feature_degrees = _degrees + 270

            if primary_feature_degrees <= 180:
                    secondary_feature_degrees = primary_feature_degrees + 180
            if primary_feature_degrees > 180:
                    secondary_feature_degrees = primary_feature_degrees - 180

        # if bike_right's facility is better than bike_left's
        if br_rank < bl_rank:
            primary_feature = _bike_right
            secondary_feature = _bike_left

            if _degrees <= 270:
                primary_feature_degrees = _degrees + 90
            if _degrees > 270:
                primary_feature_degrees = _degrees - 270

            if primary_feature_degrees <= 180:
                    secondary_feature_degrees = primary_feature_degrees + 180
            if primary_feature_degrees > 180:
                    secondary_feature_degrees = primary_feature_degrees - 180

    # if bike right does not have a facility
    elif _bike_left in bike_lookup.keys() and _bike_right not in bike_lookup.keys(): 

        primary_feature = _bike_left
        secondary_feature  = "NA"
        secondary_feature_degrees ='NA'

        if _degrees <= 270:
            primary_feature_degrees = _degrees + 90
        if _degrees > 270:
            primary_feature_degrees = _degrees - 270
    
    # if bike left does not have a facility
    elif _bike_right in bike_lookup.keys() and _bike_left not in bike_lookup.keys(): 
        
        primary_feature = _bike_right
        secondary_feature  = "NA"
        secondary_feature_degrees ='NA'

        if _degrees <= 270:
            primary_feature_degrees = _degrees + 90
        if _degrees > 270:
            primary_feature_degrees = _degrees - 270

    else:
         primary_feature = 'NA'
         secondary_feature = 'NA'
         primary_feature_degrees = 'NA'
         secondary_feature_degrees = 'NA'  


    #-----------------------------------
    # Planned Bike Facilities
    #-----------------------------------

    # are facilities planned for both sides?
    if _planned_bike_left in bike_lookup.keys() and _planned_bike_right in bike_lookup.keys(): 
        
        bl_rank = bike_lookup[_planned_bike_left]
        br_rank = bike_lookup[_planned_bike_right]

        # if bike_left's facility is better than bike_right's or they tie
        if (bl_rank < br_rank) or (bl_rank == br_rank):
            planned_primary_feature = _planned_bike_left
            planned_secondary_feature = _planned_bike_right

            if _degrees >= 90:
                planned_primary_feature_degrees = _degrees - 90
            if _degrees < 90:
                planned_primary_feature_degrees = _degrees + 270

            if planned_primary_feature_degrees <= 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
            if planned_primary_feature_degrees > 180:
                planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

        # if bike_right's facility is better than bike_left's
        if br_rank < bl_rank:
            planned_primary_feature = _planned_bike_right
            planned_secondary_feature = _planned_bike_left

            if _degrees <= 270:
                planned_primary_feature_degrees = _degrees + 90
            if _degrees > 270:
                planned_primary_feature_degrees = _degrees - 270

            if planned_primary_feature_degrees <= 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
            if planned_primary_feature_degrees > 180:
                    planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

    # if a new facility is only planned for left
    elif _planned_bike_left in bike_lookup.keys() and _planned_bike_right not in bike_lookup.keys(): 
        
        bl_rank = bike_lookup[_planned_bike_left]
        
        # is there an existing facility on bike right?
        if _bike_right in bike_lookup.keys():

            br_rank = bike_lookup[_bike_right]

            # if bike_left's facility is better than bike_right's or they tie
            if (bl_rank < br_rank) or (bl_rank == br_rank):
                planned_primary_feature = _planned_bike_left
                planned_secondary_feature = _bike_right

                if _degrees >= 90:
                    planned_primary_feature_degrees = _degrees - 90
                if _degrees < 90:
                    planned_primary_feature_degrees = _degrees + 270

                if planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                if planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

            # if bike_right's facility is better than bike_left's
            if br_rank < bl_rank:
                planned_primary_feature = _bike_right
                planned_secondary_feature = _planned_bike_left

                if _degrees <= 270:
                    planned_primary_feature_degrees = _degrees + 90
                if _degrees > 270:
                    planned_primary_feature_degrees = _degrees - 270

                if planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                if planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180
        else:
            planned_primary_feature = _planned_bike_left
            if _degrees <= 270:
                    planned_primary_feature_degrees = _degrees + 90
            if _degrees > 270:
                    planned_primary_feature_degrees = _degrees - 270
          
    # if a new facility is only planned for right
    elif _planned_bike_right in bike_lookup.keys() and _planned_bike_left not in bike_lookup.keys(): 
        
        br_rank = bike_lookup[_planned_bike_right]
        
        # is there an existing facility on bike left?
        if _bike_left in bike_lookup.keys():

            bl_rank = bike_lookup[_bike_left]

            # if bike_left's facility is better than bike_right's or they tie
            if (bl_rank < br_rank) or (bl_rank == br_rank):
                planned_primary_feature = _bike_left
                planned_secondary_feature = _planned_bike_right

                if _degrees >= 90:
                    planned_primary_feature_degrees = _degrees - 90
                if _degrees < 90:
                    planned_primary_feature_degrees = _degrees + 270

                if planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                if planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180

            # if bike_right's facility is better than bike_left's
            if br_rank < bl_rank:
                planned_primary_feature = _planned_bike_right
                planned_secondary_feature = _bike_left

                if _degrees <= 270:
                    planned_primary_feature_degrees = _degrees + 90
                if _degrees > 270:
                    planned_primary_feature_degrees = _degrees - 270

                if planned_primary_feature_degrees <= 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees + 180
                if planned_primary_feature_degrees > 180:
                        planned_secondary_feature_degrees = planned_primary_feature_degrees - 180
        else:
            planned_primary_feature = _planned_bike_right
            if _degrees <= 270:
                    planned_primary_feature_degrees = _degrees + 90
            if _degrees > 270:
                    planned_primary_feature_degrees = _degrees - 270
    else:
         planned_primary_feature = 'NA'
         planned_secondary_feature = 'NA'
         planned_primary_feature_degrees = 'NA'
         planned_secondary_feature_degrees = 'NA'
         

    return (primary_feature, secondary_feature, primary_feature_degrees, secondary_feature_degrees, planned_primary_feature, planned_secondary_feature, planned_primary_feature_degrees, planned_secondary_feature_degrees)

result = determine_primary_bike_feature_and_side(_degrees=0, _bike_right='2C', _planned_bike_left='3C')
print(f"The primary bike feature is {result[0]} and is on the {determine_direction(result[2])} side")
print(f"The secondary bike feature is {result[1]} and is on the {determine_direction(result[3])} side")
print(f"The planned primary bike feature is {result[4]} and is on the {determine_direction(result[6])} side")
print(f"The planned secondary bike feature is {result[5]} and is on the {determine_direction(result[7])} side")

## Bike-App-Create-Features

*Requires Arcpy, ArcGIS Python API*

This script pulls down the most recent copies of the utah roads and 
trails & pathways datasets (hosted by UGRC), merges and formats them, 
and determines its best bike feature as well as which side of the 
road the feature is on. The final products are 1) existing and 
2) planned line layers for the wfrc-bike-app.

### Schema:
- 'UID' - unique identifier
- 'COUNTY' - name of county
- 'CITY' - name of city
- 'NAME' - name of the street or trail
- 'Facility1 (PlannedFacility1)'  - primary bike facility type
- 'Facility2 (PlannedFacility2)' - secondary bike facility type
- 'Facility1_Side (PlannedFacility1_Side)' - cardinal direction of the primary bike facility
- 'Facility2_Side (PlannedFacility2_Side)' - cardinal direction of the secondary bike facility
- 'STATUS' - existing or planned
- 'NOTES' - notes field for displaying additional info or capturing comments
- 'CARTOCODE' - cartographic code
- 'SOURCE' - roads or trails,
- 'SOURCE_ID' - id for joining back to global id of source data

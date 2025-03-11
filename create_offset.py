# First off, make sure your line segs have unique IDs.

#     1.Buffer "FLAT" in each direction of the line, add a new field of the same name to each and give them a direction ("L","R").
#     2.Merge the buffers together.
#     3.Buffer the original line again, this time "FULL".
#     4.Convert the FULL buffer to lines (PolygonToLine: "IGNORE_NEIGHBORS"), then convert its vertices to points (FeatureVerticesToPoints: "BOTH_ENDS").
#     5.Buffer each point by a very small width (e.g. 0.1 m).
#     6.Split the lines by vertex (SplitLine).
#     7.Select by location to select all lines that intersect with the point buffers.
#     8.Delete these lines.
#     9.Dissolve ("SINGLE_PART") on the segment unique ID.
#     10.Spatial Join ("SHARE_A_LINE_SEGMENT_WITH") the new lines to the merged "LEFT" and "RIGHT" buffers to attribute them with direction.

# Voila! Offset lines without ArcObjects.
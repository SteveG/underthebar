#!/usr/bin/env python3
"""Garmin Translate

Provides the methods for translating a hevy routine json file into a garmin csv file (prior to using fitcsvtool to create .fit)

Currently this is a 'hidden' feature. It is enabled by adding a file "garmin_translations.json" to the users routines folder.

"""


import json
import os
import csv
import time
from pathlib import Path


# This stuff is all copied from an example csv file, I'll copy these rows and adjust elements within them.
first_eight_lines = [
  ["Type","Local Number","Message","Field 1","Value 1","Units 1","Field 2","Value 2","Units 2","Field 3","Value 3","Units 3","Field 4","Value 4","Units 4","Field 5","Value 5","Units 5","Field 6","Value 6","Units 6","Field 7","Value 7","Units 7","Field 8","Value 8","Units 8","Field 9","Value 9","Units 9","Field 10","Value 10","Units 10","Field 11","Value 11","Units 11","Field 12","Value 12","Units 12",""  ],
  ["Definition","0","file_id","type","1","","manufacturer","1","","product","1","","time_created","1","","serial_number","1","","","","","","","","","","","","","","","","","","","","","","",""  ],
  ["Data","0","file_id","type","5","","manufacturer","1","","garmin_product","65534","","time_created","1105967882","","serial_number","1108273834","","","","","","","","","","","","","","","","","","","","","","",""  ],
  ["Definition","0","file_creator","hardware_version","1","","software_version","1","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""  ],
  ["Data","0","file_creator","hardware_version","0","","software_version","0","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""  ],
  ["Definition","0","workout","wkt_name","19","","unknown","1","","unknown","1","","unknown","1","","unknown","1","","unknown","1","","unknown","1","","sport","1","","sub_sport","1","","capabilities","1","","num_valid_steps","1","","message_index","1","",""  ],
  ["Data","0","workout","wkt_name","Exercise Templates","","unknown","0","","unknown","1","","unknown","0","","unknown","0","","unknown","0","","unknown","0","","sport","10","","sub_sport","20","","capabilities","32","","num_valid_steps","13","","message_index","0","",""  ],
  ["Definition","0","workout_step","message_index","1","","intensity","1","","target_type","1","","target_value","1","","secondary_target_type","1","","secondary_target_value","1","","duration_type","1","","duration_value","1","","exercise_category","1","","exercise_name","1","","exercise_weight","1","","weight_display_unit","1","",""  ]
]

sample_rest_line =   ["Data",0,"workout_step","message_index",0,"","intensity",1,"","target_type",2,"","target_value",0,"","secondary_target_type",2,"","secondary_target_value",0,"","duration_type",0,"","duration_time",60,"","","","","","","","","","","","","",""  ]
sample_reps_only =   ["Data",0,"workout_step","message_index",1,"","intensity",0,"","target_type",2,"","target_value",0,"","secondary_target_value",0,"","duration_type",29,"","duration_reps",10,"","exercise_category",37,"","exercise_name",32,"","","","","","","","","","",""  ]
sample_reps_weight = ["Data",0,"workout_step","message_index",2,"","intensity",0,"","target_type",2,"","target_value",0,"","secondary_target_value",0,"","duration_type",29,"","duration_reps",10,"","exercise_category",0,"","exercise_name",1,"","exercise_weight",100,"kg","weight_display_unit",1,"","","","",""  ]
sample_duration =    ["Data",0,"workout_step","message_index",8,"","intensity",0,"","target_type",2,"","target_value",0,"","secondary_target_value",0,"","duration_type",0,"","duration_time",60,"","exercise_category",19,"","exercise_name",43,"","","","","","","","","","",""  ]

names_line =   ["Definition",0,"exercise_title","exercise_name",1,"","exercise_category",1,"","wkt_step_name",28,"","message_index",1,"","","","","","","","","","","","","","","","","","","","","","","","","",""  ]
sample_names_line =   ["Data",0,"exercise_title","exercise_name",1,"","exercise_category",0,"","wkt_step_name","Barbell Bench Press","","message_index",1,"","","","","","","","","","","","","","","","","","","","","","","","","",""  ]



#
# Scripted translation of a hevy routine in json to a garmin csv file to pass into fitcsvtool to make a .fit file
# the_file = path and name of your hevy routine in json format
# the_target = path and name of destination csv file
# the_translations = path and name the garmin_translations.json file or similar
#
def do_translation(the_file, the_target, the_translations):
	
	print("starting do_translation with file: ", the_file)
	
	with open(the_translations, 'r') as file:
		translation_data = json.load(file)
		
	with open(the_file, 'r') as file:
		routine_data = json.load(file)
		
	workout_exercises = {}
	workout_steps = []
	workout_exercise_names = []
	workout_step_count = 0
	
	
	
	for exercise in routine_data["exercises"]:
		if exercise["title"] in translation_data.keys():
			print("FOUND", exercise["title"]," >>> ", translation_data[exercise["title"]]["wkt_step_name"])
		else:
			print("CREATE", exercise["title"])
			translation_data[exercise["title"]] = {"exercise_name":0, "exercise_category":65534, "wkt_step_name":exercise["title"]}
			
		workout_exercises[exercise["title"]] = 1
		for exercise_set in exercise["sets"]:
			# CASES FOR SETS
			# Weight Reps
			if exercise_set["reps"] != None and exercise_set["weight_kg"] != None and exercise_set["distance_meters"] == None and exercise_set["duration_seconds"] == None:
				#print (workout_step_count, " - set", "weight/reps")
				new_line = sample_reps_weight.copy()
				new_line[4] = workout_step_count
				new_line[22] = exercise_set["reps"] # reps
				new_line[25] = translation_data[exercise["title"]]["exercise_category"] # exercise_category
				new_line[28] = translation_data[exercise["title"]]["exercise_name"] # exercise_name
				new_line[31] = exercise_set["weight_kg"] # weight
				workout_steps.append(new_line)
				
				workout_step_count +=1 
			# Reps Only
			elif exercise_set["reps"] != None and exercise_set["weight_kg"] == None and exercise_set["distance_meters"] == None and exercise_set["duration_seconds"] == None:
				#print (workout_step_count, " - set", "reps only")
				new_line = sample_reps_only.copy()
				new_line[4] = workout_step_count
				new_line[22] = exercise_set["reps"] # reps
				new_line[25] = translation_data[exercise["title"]]["exercise_category"] # exercise_category
				new_line[28] = translation_data[exercise["title"]]["exercise_name"] # exercise_name
				workout_steps.append(new_line)
				
				workout_step_count +=1 
			# Duration only
			elif exercise_set["reps"] == None and exercise_set["weight_kg"] == None and exercise_set["distance_meters"] == None and exercise_set["duration_seconds"] != None:
				#print (workout_step_count, " - set", "duration only")
				new_line = sample_duration.copy()
				new_line[4] = workout_step_count
				new_line[22] = exercise_set["duration_seconds"] # duration
				new_line[25] = translation_data[exercise["title"]]["exercise_category"] # exercise_category
				new_line[28] = translation_data[exercise["title"]]["exercise_name"] # exercise_name
				workout_steps.append(new_line)
				
				workout_step_count +=1 
				
			# These hevy types I haven't done yet
			# Weight Duration
			# Distance Duration
			# Weight Distance
			
			
			# THEN DO THE REST TIMER
			#print(workout_step_count, " - rest ", exercise["rest_seconds"])
			if exercise["rest_seconds"] != 0:
				new_line = sample_rest_line.copy()
				new_line[4] = workout_step_count
				new_line[25] = exercise["rest_seconds"]
				workout_steps.append(new_line)
				
				workout_step_count +=1 
            
	exercise_count = 0
	for exercise in workout_exercises.keys():
		new_line = sample_names_line.copy()
		new_line[7] = translation_data[exercise]["exercise_category"] # exercise_category
		new_line[4] = translation_data[exercise]["exercise_name"] # exercise_name
		new_line[10] = exercise # exercise_name
		new_line[13] = exercise_count
		workout_exercise_names.append(new_line)
		
		exercise_count +=1
	
	first_eight_lines[2][13] = int(time.time())
	first_eight_lines[6][4] = routine_data["title"]
	first_eight_lines[6][34] = workout_step_count
            

	# Create the output, first the header lines, then the workout steps, then the exercise definitions
	with open(the_target, 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		
		for rout_line in first_eight_lines:
			spamwriter.writerow(rout_line)
		
		for rout_line in workout_steps:
			spamwriter.writerow(rout_line)
			
		spamwriter.writerow(names_line)
		
		for rout_line in workout_exercise_names:
			spamwriter.writerow(rout_line)
			

if __name__ == "__main__":


	print("starting Garmin translate")
	#do_translation("garmin_test.json", "garmin_output.csv")


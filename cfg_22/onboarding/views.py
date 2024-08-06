from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
from tempfile import NamedTemporaryFile
import math

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
cfg_db = client['cfg_22']
onboarding = cfg_db['onboarding']
measures = cfg_db['measures']

@csrf_exempt
@require_http_methods(["POST"])
def save_data(request):
    try:
        data = request.POST
        topview = request.FILES.get('top_view')

        range_val = data.get('range')
        place = data.get('place')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        height = float(data.get('height'))

        # Save images to MongoDB
        topview_id = save_image(topview)

        current_datetime = datetime.now()

        yield_per_m2 = 1.5

        color_ranges = [
            ([100, 50, 50], [140, 255, 255]),  # Blue color range (for lakes)
            ([10, 50, 50], [25, 255, 255]),    # Brown color range (for land)
            ([35, 50, 50], [85, 255, 255]),    # Green color range (for vegetation)
            ([60, 40, 60], [80, 60, 90])
        ]

        # Save the top_view file temporarily
        with NamedTemporaryFile(delete=False) as temp_file:
            for chunk in topview.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name  # Path to the temporary file

        # Process the image using the temporary file path
        res = calc_size(temp_file_path, height, color_ranges, yield_per_m2)
        print(res)

        # Remove the temporary file after processing
        os.remove(temp_file_path)

        # Prepare the document to insert
        doc = {
            'topview': topview_id,
            'range': range_val,
            'place': place,
            'latitude': math.floor(latitude),
            'longitude': math.floor(longitude),
            'height': height,
            'current_datetime': current_datetime,
            'area': res[0]
        }
        print(doc)

        # Insert the measures into the database
        measures.insert_one({'area': res[0], 'biomass': res[1]})

        # Check for existing records with the same floored latitude and longitude
        existing_record = onboarding.find_one({'longitude': math.floor(longitude), 'latitude': math.floor(latitude)})
        print(existing_record)
        if existing_record:
            new_area = res[0]
            if new_area < existing_record['area']:
                change_amount = existing_record['area'] - new_area
                print("change_amount***************************************",change_amount)
                return JsonResponse({'success': True, 'message': 'Lantana decreased.', 'change': change_amount})
            else:
                print("&&&&&&&&&&&&&&&&&&&&&")
                return JsonResponse({'success': True, 'message': 'Lantana increased.'})

        # Insert the new record if no existing record was found
        onboarding.insert_one(doc)
        print("now redirecting")
        return JsonResponse({'success': True, 'message': 'Data saved successfully.'})
    except Exception as e:
        return HttpResponse('Error saving data: ' + str(e))

def save_image(image):
    try:
        # Generate a random filename for the image
        filename = str(random.randint(1000, 9999)) + '.' + image.name.split('.')[-1]
        # Save the image to MongoDB
        image_id = cfg_db['onboarding_images'].insert_one({'image': image.read(), 'filename': filename}).inserted_id
        return image_id
    except Exception as e:
        print(e)

def remove_colors(image_path, color_ranges):
    img = cv2.imread(image_path)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = np.zeros(img_hsv.shape[:2], dtype=np.uint8)

    for (lower_bound, upper_bound) in color_ranges:
        lower_bound = np.array(lower_bound, dtype=np.uint8)
        upper_bound = np.array(upper_bound, dtype=np.uint8)
        color_mask = cv2.inRange(img_hsv, lower_bound, upper_bound)
        mask = cv2.bitwise_or(mask, color_mask)

    result = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))

    result_path = 'filtered_image.jpg'
    cv2.imwrite(result_path, result)
    return result_path

def get_number_of_pixels(image_path):
    with Image.open(image_path) as img:
        img_gray = img.convert('L')
        img_array = np.array(img_gray)
        number_of_pixels = np.sum(img_array > 0)
        return float(number_of_pixels)  # Use float for double precision

def calculate_area(number_of_pixels, pixel_size_meters):
    return number_of_pixels * (float(pixel_size_meters) ** 2)

def calculate_biomass(area_meters, yield_per_m2):
    return area_meters * float(yield_per_m2)

def convert_kg_to_metric_tons(biomass_kg):
    """Convert biomass from kilograms to metric tons."""
    return biomass_kg / 1000.0

def calc_size(image_path, pixel_size_meters, color_ranges, yield_per_m2):
    filtered_image_path = remove_colors(image_path, color_ranges)
    
    number_of_pixels = get_number_of_pixels(filtered_image_path)
    
    area_meters = calculate_area(number_of_pixels, pixel_size_meters)
    
    biomass_kg = calculate_biomass(area_meters, yield_per_m2)
    biomass_metric_tons = convert_kg_to_metric_tons(biomass_kg)
    
    print(f"The number of pixels in the filtered image is {number_of_pixels:.2f}.")
    print(f"The area is {area_meters:.2f} square meters.")
    print(f"The estimated biomass is {biomass_kg:.2f} kg.")
    print(f"The estimated biomass is {biomass_metric_tons:.2f} metric tons.")

    return [area_meters, biomass_kg]

def index(request):
    return render(request, 'onboarding/index.html')

def identify(request):
    return render(request, 'onboarding/identify.html')

def revenue(request):
    return render(request, 'cost_analysis/revenue.html')
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import os
from PIL import Image
import cv2
import numpy as np

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

    result_path = 'filtered_image3.jpg'
    cv2.imwrite(result_path, result)
    return result_path

def get_number_of_pixels(image_path):
    with Image.open(image_path) as img:
        img_gray = img.convert('L') 
        img_array = np.array(img_gray)
        number_of_pixels = np.sum(img_array > 0)
        return number_of_pixels

def calculate_area(number_of_pixels, pixel_size_meters):
    return number_of_pixels * (pixel_size_meters ** 2)

def calculate_biomass(area_meters, yield_per_m2):
    return area_meters * yield_per_m2

def convert_kg_to_metric_tons(biomass_kg):
    return biomass_kg / 1000

def process_image(image_path, pixel_size_meters, color_ranges, yield_per_m2):
    filtered_image_path = remove_colors(image_path, color_ranges)
    number_of_pixels = get_number_of_pixels(filtered_image_path)
    area_meters = calculate_area(number_of_pixels, pixel_size_meters)
    biomass_kg = calculate_biomass(area_meters, yield_per_m2)
    biomass_metric_tons = convert_kg_to_metric_tons(biomass_kg)
    return area_meters, biomass_kg, biomass_metric_tons

# Function to handle uploaded zip file
def handle_zip_file(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall('extracted_images')

# Process each image and classify them
def classify_images(image_dir, pixel_size_meters, color_ranges, yield_per_m2, threshold):
    images_data = []
    for img_name in os.listdir(image_dir):
        img_path = os.path.join(image_dir, img_name)
        area_meters, biomass_kg, biomass_metric_tons = process_image(img_path, pixel_size_meters, color_ranges, yield_per_m2)
        classification = 'elephant' if biomass_metric_tons < threshold else 'biomass'
        images_data.append({
            'image': img_name,
            'area_m^2': area_meters,
            'biomass_kg': biomass_kg,
            'biomass_metric_tons': biomass_metric_tons,
            'classification': classification
        })
    return pd.DataFrame(images_data)

# Streamlit app
st.title('Lantana Biomass Classification and Visualization')

# File upload
uploaded_zip = st.file_uploader("Upload a zip file containing images", type="zip")

if uploaded_zip:
    handle_zip_file(uploaded_zip)
    
    # Parameters
    pixel_size_meters = 1
    yield_per_m2 = 1.5
    color_ranges = [
        ([100, 50, 50], [140, 255, 255]),
        ([10, 50, 50], [25, 255, 255]),
        ([35, 50, 50], [85, 255, 255]),
        ([60, 40, 60], [80, 60, 90])
    ]
    threshold = 0.5  # Metric tons threshold for classification
    
    # Process images and classify
    df = classify_images('extracted_images', pixel_size_meters, color_ranges, yield_per_m2, threshold)
    
    # Display classification results
    st.write('## Classification Results')
    st.write(df)

    # Display images classified as 'elephant'
    st.write('## Images classified as "elephant"')
    for idx, row in df[df['classification'] == 'elephant'].iterrows():
        st.write(f"Image: {row['image']}, Biomass: {row['biomass_metric_tons']} metric tons")
        img_path = os.path.join('extracted_images', row['image'])
        st.image(img_path, caption=row['image'], use_column_width=True)
    
    # Display pie chart for fixed biomass values
    st.write('## Biomass vs Elephant Classification Distribution')
    labels = ['Biomass (60%)', 'Elephant (40%)']
    sizes = [60, 40]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.set_title('Biomass vs Elephant Classification Distribution')
    st.pyplot(fig)

    # Display histogram of biomass (kg) vs area
    st.write('## Histogram: Biomass (kg) vs Area (m^2)')
    fig, ax = plt.subplots()
    ax.hist(df['biomass_kg'], bins=10, edgecolor='black', alpha=0.7, label='Biomass (kg)')
    ax.set_xlabel('Biomass (kg)')
    ax.set_ylabel('Frequency')
    ax.set_title('Histogram: Biomass (kg) vs Area (m^2)')
    st.pyplot(fig)

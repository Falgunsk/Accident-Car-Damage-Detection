import base64
from collections import Counter
from io import BytesIO

import mysql.connector
import pandas as pd
from PIL import Image
from tqdm import tqdm
from ultralytics import YOLO

import config


def get_db_connection():
    return mysql.connector.connect(**config.credentials)

class YOLOModel:
    def __init__(self, model_path = r"..\\Accident-Car-Damage-Detection\\flask\\model weights\\weights\\best.pt", image_path = None):
        """Initialize the YOLO model with the given path."""
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        self.db_connection = get_db_connection()
        self.image_path = image_path
        self.max_counts = {
            'Bonnet': 1,
            'Bumper': 1,
            'Dickey': 1,
            'Door': 4,
            'Fender': 4,
            'Light': 4,
            'Windshield': 2
        }

    def predict(self):
        """Make predictions on a single image path with progress tracking."""
        # Wrap the single image processing in tqdm for progress indication
        with tqdm(total=1, desc="Processing image") as pbar:
            self.output = self.model(self.image_path)
            pbar.update(1)
        return self.output

    def get_detected_objects(self):
        """Extract detected objects and their counts."""
        results = self.output[0]  # Get the first (and only) result
        detected_classes = [self.class_names[int(cls)] for cls in results.boxes.cls]
        detected_counts = Counter(detected_classes)
        
        # Ensure detected counts do not exceed the maximum allowed counts
        for part, max_count in self.max_counts.items():
            if detected_counts[part] > max_count:
                detected_counts[part] = max_count
        
        return detected_counts
    
    def plot_image(self, save_path=None):
        """Plot detections on the image, ensuring counts do not exceed max counts."""
        # Load the original image
        original_image = Image.open(self.image_path)

        # Plot detections on the image
        results = self.output[0]  # Get the first (and only) result
        
        # Filter boxes to ensure they do not exceed max counts
        filtered_boxes = []
        counts = Counter()
        for box in results.boxes:
            class_name = self.class_names[int(box.cls)]
            if counts[class_name] < self.max_counts.get(class_name, float('inf')):
                filtered_boxes.append(box)
                counts[class_name] += 1
        
        results.boxes = filtered_boxes
        
        # Saving the output image if a `save_path` is provided and then opening that saved image. 
        # If no `save_path` is provided, it simply displays the output image.
        
        if save_path:
            out_image_path = results.save(save_path)
            out_image = Image.open(out_image_path)
        else:
            out_image = results.show()
        
        # Convert images to byte arrays for web display with base64
        original_image_bytes = self.image_to_bytes(original_image)
        out_image_bytes = self.image_to_bytes(out_image)

        return base64.b64encode(original_image_bytes).decode("utf-8"), base64.b64encode(out_image_bytes).decode("utf-8")

    def image_to_bytes(self, image):
        """Convert a PIL image to bytes. with base64 encoding."""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return buffered.getvalue()

    def predict_price(self, car_brand = None, car_model = None):
        """Predict the price of the detected objects."""
        # Get detected objects and their counts
        
        detected_counts = self.get_detected_objects()
        
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM car_data WHERE brand = %s AND model = %s", (car_brand, car_model))
            car_data = cursor.fetchall()
            car_data = pd.DataFrame(car_data, columns=['id', 'brand', 'model', 'part', 'price'])
            
            # Calculate the price of each detected object
            # also show the quantity of each object detected
            estimated_prices = pd.DataFrame(columns=['Part', 'Quantity', 'Rate', 'Total'])
            
            rows = []
            for part, count in detected_counts.items():
                part_data = car_data[car_data['part'] == part]
                if len(part_data) > 0:
                    rate = part_data['price'].values[0]
                    total = rate * count
                else:
                    rate = 0
                    total = 0

                rows.append({'Part': part, 'Quantity': count, 'Rate': rate, 'Total': total})
                
            estimated_prices = pd.concat([estimated_prices, pd.DataFrame(rows)], ignore_index=True)
                    
            # Convert the Total column to float
            estimated_prices['Total'] = estimated_prices['Total'].astype(float)
                
            # Calculate the total price of all detected objects
            total_price = estimated_prices['Total'].sum()
            
            # Show all the detected objects and their prices in a tabular format
            cursor.close()
         
            return estimated_prices, total_price
        
    
    def __del__(self):
        """Close the database connection when the object is deleted."""
        self.db_connection.close()
        

# Example usage
# if __name__ == "__main__":
#     # Initialize the model
#     img_path = "path-to-image.jpg"
#     model = YOLOModel(image_path=img_path)
    
#     # Make predictions on the image
#     model.predict()
    
#     # Get detected objects and their counts
#     detected_objects = model.get_detected_objects()
#     print("Detected Objects:", detected_objects)
    
#     # Plot the detections on the image
#     model.plot_image(save_path="output.png")
    
#     # Predict the price of the detected objects
#     estimated_prices, total_price = model.predict_price(car_brand = "Toyota", car_model = "Corolla")
#     print("Detected Prices:")
#     print(estimated_prices)
#     print("Total Price:", total_price)
    
#     # Delete the model object to close the database connection


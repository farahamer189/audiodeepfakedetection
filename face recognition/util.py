import os
import cv2
from deepface import DeepFace


def recognize(img, db_path):
    try:
        # Save the current frame temporarily for DeepFace to process
        temp_img_path = "temp_login.jpg"
        cv2.imwrite(temp_img_path, img)

        # Use DeepFace to find a match
        result = DeepFace.find(img_path=temp_img_path, db_path=db_path, model_name='Facenet')

        # Handle DataFrame results
        if isinstance(result, list):
            result = result[0]  # Access the first DataFrame if it's returned as a list

        if not result.empty:  # Ensure the DataFrame has results
            matched_path = result.iloc[0]['identity']  # Get the first match's file path
            return os.path.basename(matched_path).split('.')[0]  # Extract the username

        return 'unknown_person'  # No matches found
    except Exception as e:
        print(f"Error during recognition: {e}")
        return 'unknown_person'

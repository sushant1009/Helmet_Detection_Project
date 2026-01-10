from src.Helmet_Detection import logger
from dataclasses import dataclass
from pathlib import Path
import urllib.request as request
from src.Helmet_Detection.utils.common import read_yaml, create_directory,get_size
from src.Helmet_Detection.constants import *
from src.Helmet_Detection.entity.config_entity import DataTransformationConfig
import json
import shutil
import random
import os



class DataTransformation:
    def __init__(self, config : DataTransformationConfig):
        self.config = config
        self.class_map = {
        "helmet": 0,
        "head": 1
    }
       
    def convert_to_yolo(self,json_file, txt_file):
        with open(json_file, "r") as f:
            data = json.load(f)

        img_w = data["size"]["width"]
        img_h = data["size"]["height"]

        yolo_lines = []
        for obj in data["objects"]:
            cls = obj["classTitle"]
            if cls not in self.class_map:
                continue

            # Get bounding box
            x_min, y_min = obj["points"]["exterior"][0]
            x_max, y_max = obj["points"]["exterior"][1]

            # Convert to YOLO format (normalized)
            x_center = ((x_min + x_max) / 2) / img_w
            y_center = ((y_min + y_max) / 2) / img_h
            width = (x_max - x_min) / img_w
            height = (y_max - y_min) / img_h

            yolo_lines.append(f"{self.class_map[cls]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        with open(txt_file, "w") as f:
            f.write("\n".join(yolo_lines))
            
    def convert_all(self):
        input_folder = self.config.ann_path  
        output_folder = self.config.labels_path
        os.makedirs(output_folder, exist_ok=True)
        for filename in os.listdir(input_folder):
            if filename.endswith(".json"):
                json_path = os.path.join(input_folder, filename)
                txt_filename = filename.replace(".json", ".txt")
                txt_path = os.path.join(output_folder, txt_filename)
                self.convert_to_yolo(json_path, txt_path)

        print("Conversion completed. YOLO labels are saved in:", output_folder)
    
    def rename_files(self):
        labels_folder = self.config.labels_path

        for filename in os.listdir(labels_folder):
            if filename.endswith(".png.txt"):
                new_name = filename.replace(".png.txt", ".txt")
                os.rename(
                    os.path.join(labels_folder, filename),
                    os.path.join(labels_folder, new_name)
                )

        print("Renaming completed. Labels are now in YOLO format (img.txt).")
    
    def move_files(self,file_list, split):
        for img_file in file_list:
            # Image
            src_img = os.path.join(self.config.img_path, img_file)
            dst_img = os.path.join(self.config.image_data_path, split, img_file)
            shutil.copy(src_img, dst_img)

            
            label_file = os.path.splitext(img_file)[0] + ".txt"
            src_label = os.path.join(self.config.labels_path, label_file)
            dst_label = os.path.join(self.config.label_data_path, split, label_file)

            if os.path.exists(src_label):  # Some images may not have labels
                shutil.copy(src_label, dst_label)
    
    def train_test_val_split(self):

        # Split ratios
        train_ratio = self.config.train_split
        val_ratio = self.config.val_split
        test_ratio = self.config.test_split

        # Ensure output directories exist
        for split in ["train", "val", "test"]:
            os.makedirs(os.path.join(self.config.image_data_path, split), exist_ok=True)
            os.makedirs(os.path.join(self.config.label_data_path, split), exist_ok=True)

        # Get all image files
        images_dir = os.path.join(self.config.img_path)
        labels_dir = os.path.join(self.config.labels_path)

        image_files = [f for f in os.listdir(images_dir) if f.endswith((".jpg", ".png", ".jpeg"))]
        random.shuffle(image_files)

        # Split indexes
        n_total = len(image_files)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        train_files = image_files[:n_train]
        val_files = image_files[n_train:n_train + n_val]
        test_files = image_files[n_train + n_val:]
        
        self.move_files(train_files, "train")
        self.move_files(val_files, "val")

        self.move_files(test_files, "test")

        print(f"Dataset split complete!")
        print(f"Train: {len(train_files)} | Val: {len(val_files)} | Test: {len(test_files)}")

       
        

        
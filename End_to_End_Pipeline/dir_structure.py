import os

def create_dirs(base_dir="Helmet_Detection_Project"):
    # Define the directory structure
    dirs = [
        f"{base_dir}/data/raw",
        f"{base_dir}/data/processed",
        f"{base_dir}/data/datasets/train/images",
        f"{base_dir}/data/datasets/train/labels",
        f"{base_dir}/data/datasets/val/images",
        f"{base_dir}/data/datasets/val/labels",
        f"{base_dir}/data/datasets/test/images",
        f"{base_dir}/data/datasets/test/labels",
        f"{base_dir}/configs",
        f"{base_dir}/notebooks",
        f"{base_dir}/src",
        f"{base_dir}/models",
        f"{base_dir}/logs/tensorboard",
        f"{base_dir}/logs/wandb",
        f"{base_dir}/tests",
    ]

    # Create each directory if not exists
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created: {d}")

    # Create some starter files
    files = {
        f"{base_dir}/README.md": "# Final Year Project\n\nProject documentation goes here.",
        f"{base_dir}/requirements.txt": "# Add Python dependencies here\nultralytics\nmatplotlib\npandas\nopencv-python\n",
        f"{base_dir}/configs/dataset.yaml": "# Example YOLO dataset config\ntrain: ../data/datasets/train/images\nval: ../data/datasets/val/images\ntest: ../data/datasets/test/images\n\nnc: 3\nnames: ['class1', 'class2', 'class3']\n",
        f"{base_dir}/.gitignore": "*.pyc\n__pycache__/\nmodels/\nlogs/\n",
    }

    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)
        print(f"Created file: {path}")

if __name__ == "__main__":
    create_dirs()

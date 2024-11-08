from PIL import Image
import os

# 원본 이미지 경로 및 저장 경로 설정
input_dir = "/home/hj/gaussian-splatting/dataset/Church/images_o"
output_dir = "/home/hj/gaussian-splatting/dataset/Church/images"
os.makedirs(output_dir, exist_ok=True)

# 각 이미지에 대해 크기를 절반으로 줄이기
for img_file in os.listdir(input_dir):
    img_path = os.path.join(input_dir, img_file)
    img = Image.open(img_path)
    
    # 원본 크기의 절반 계산
    new_size = (img.width // 2, img.height // 2)
    img_resized = img.resize(new_size, Image.LANCZOS)  # 고품질 리사이징

    # 리사이즈된 이미지 저장
    img_resized.save(os.path.join(output_dir, img_file))

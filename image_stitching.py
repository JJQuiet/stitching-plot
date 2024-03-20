from PIL import Image
import os

def concatenate_vertically(image_list):
    width = max(image.width for image in image_list)
    height = sum(image.height for image in image_list)
    concatenated_image = Image.new('RGB', (width, height))
    y_offset = 0
    for image in image_list[::-1]:
        concatenated_image.paste(image, (0, y_offset))
        y_offset += image.height
    return concatenated_image

def concatenate_horizontally(image_list):
    width = sum(image.width for image in image_list)
    height = max(image.height for image in image_list)
    concatenated_image = Image.new('RGB', (width, height))
    x_offset = 0
    for image in image_list:
        concatenated_image.paste(image, (x_offset, 0))
        x_offset += image.width
    return concatenated_image

def process_folders(parent_folder):
    subfolders = [os.path.join(parent_folder, o) for o in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder,o))]
    print('subfolder length:',len(subfolders))
    intermediate_vertical_folder = os.path.join('./', 'intermediate_vertical')
    intermediate_horizontal_folder = os.path.join('./', 'intermediate_horizontal')
    intermediate_files = []  # 存储中间文件的路径
    for folder_idx, folder in enumerate(subfolders):
        images = [Image.open(os.path.join(folder, img)) for img in os.listdir(folder) if img.endswith(('png', 'jpg', 'jpeg'))]
        if images:
            vertical_image = concatenate_vertically(images)
            intermediate_path = os.path.join(intermediate_vertical_folder, f'intermediate_{folder_idx}.tif')
            # vertical_image.save(intermediate_path)
            vertical_image.save(intermediate_path, format='TIFF')
            intermediate_files.append(intermediate_path)

    # 逐步合并中间结果，以减少内存占用
    batch_size = 10  # 根据内存容量调整
    is_last_horizontal_concatenate = False
    while len(intermediate_files) > 1:
        print('intermediate_files:       ',intermediate_files)
        if len(intermediate_files) < batch_size:
            is_last_horizontal_concatenate = True
        batched_intermediate_files = [intermediate_files[i:i + batch_size] for i in range(0, len(intermediate_files), batch_size)]
        print('bat:     ',batched_intermediate_files)
        intermediate_files = []  # 清空，准备存储这一轮合并的结果
        for batch_idx, batch in enumerate(batched_intermediate_files):
            images = [Image.open(img_file) for img_file in batch]
            horizontal_image = concatenate_horizontally(images)
            # intermediate_path = f'final_intermediate_{batch_idx}.jpg'
            intermediate_path = os.path.join(intermediate_horizontal_folder, f'final_intermediate_{batch_idx}.tif')
            horizontal_image.save(intermediate_path)
            intermediate_files.append(intermediate_path)
            print('batch:      ',batch,batch_idx)
            # for img_file in batch:  # 删除已经合并过的中间文件
                # os.remove(img_file)

    # 最后的中间文件即为最终结果，重命名为最终文件名
    if intermediate_files:  # 检查是否有最终的中间文件
        os.rename(intermediate_files[0], 'final_result.tif')

parent_folder = 'D:/Work/寿县/GIS使用java17/寿县地图baidumaps/baidumaps/tiles_hybird/15'  # 替换为你的文件夹路径
process_folders(parent_folder)

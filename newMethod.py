import SimpleITK as sitk
import vtkmodules.all as vtk
import pyvista as pv
import numpy as np
import tempfile
import os
import time

# 这些东西都读进内存就完了，犯不着一次次调用,大概要花1s
reader = sitk.ImageSeriesReader()
dicom_series = reader.GetGDCMSeriesFileNames("dicomFolder")
reader.SetFileNames(dicom_series)

# 执行读取操作
dicom_image = reader.Execute()
spacing = dicom_image.GetSpacing()
size = dicom_image.GetSize()
print(spacing)
print(size)

def world_coordinate_to_stl(pos_input):
    def convert_ras_to_lps(ras_point):
        x, y, z = ras_point
        lps_point = [x, z, size[2] - y]
        return lps_point

    def generate_array_with_sphere(shape, sphere_radius, sphere_center):
        # 定义圆柱的半径
        cylinder_radius = 1
        cylinder_length = 15  # 圆柱体长度的一半
        # 创建空间大小和掩码
        mask = np.zeros((shape[2], shape[1], shape[0]), dtype=bool)

        # 生成球的掩码
        z, y, x = np.ogrid[:shape[2], :shape[1], :shape[0]]
        sphere_mask = (x - sphere_center[0]) ** 2 + (y - sphere_center[1]) ** 2 + (
                z - sphere_center[2]) ** 2 <= sphere_radius ** 2
        mask |= sphere_mask

        # 生成沿着x、y、z方向的圆柱体掩码，考虑长度限制
        cylinder_mask_x = ((y - sphere_center[1]) ** 2 + (z - sphere_center[2]) ** 2 <= cylinder_radius ** 2) & (
                abs(x - sphere_center[0]) <= cylinder_length)
        cylinder_mask_y = ((x - sphere_center[0]) ** 2 + (z - sphere_center[2]) ** 2 <= cylinder_radius ** 2) & (
                abs(y - sphere_center[1]) <= cylinder_length)
        cylinder_mask_z = ((x - sphere_center[0]) ** 2 + (y - sphere_center[1]) ** 2 <= cylinder_radius ** 2) & (
                abs(z - sphere_center[2]) <= cylinder_length)
        mask |= cylinder_mask_x | cylinder_mask_y | cylinder_mask_z

        return mask

    def polydata_to_buffer(polydata):
        temp_file = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)

        writer = vtk.vtkSTLWriter()
        writer.SetInputData(polydata)
        writer.SetFileTypeToBinary()

        writer.SetFileName(temp_file.name)
        writer.Write()

        return temp_file.name

    # 指定数组形状、球的半径和球心的位置
    array_shape = size
    sphere_center = convert_ras_to_lps(pos_input)

    # 生成包含球的 NumPy 数组
    # 拆小包围框，并修改原点位置。
    sphere_array = generate_array_with_sphere(array_shape, 3, sphere_center)
    result4 = sphere_array[
              int(sphere_center[2]) - 25:int(sphere_center[2] + 25),
              int(sphere_center[1]) - 25:int(sphere_center[1]) + 25,
              int(sphere_center[0]) - 25:int(sphere_center[0]) + 25
              ]
    world_coordinate = dicom_image.TransformIndexToPhysicalPoint(
        (int(sphere_center[0]) - 25, int(sphere_center[1]) - 25, int(sphere_center[2]) - 25))

    origin = world_coordinate
    label = 1
    mesh1 = pv.wrap(result4)
    mesh1.origin = origin
    mesh1.spacing = spacing
    clipped = mesh1.threshold([label - 0.5, label + 0.5])
    clipped = clipped.clip_scalar(
        value=label - 0.5, invert=False
    )

    surf = clipped.extract_surface()
    surf = surf.smooth(80)
    surf = surf.triangulate()

    surf1 = surf.decimate(0.9)

    return polydata_to_buffer(surf1)


if __name__ == '__main__':
    # ---------------------------------------------------------------------------------------
    pos = [267, 174, 297]

    start = time.time()
    poltbuffer = world_coordinate_to_stl(pos)

    finish = time.time()

    elapsedTime = finish - start
    print(elapsedTime, " sec")

    # ---------------------------------------------------------------------------------------

    # 将STL文件内容写入到指定文件
    with open('lung_100.stl', 'wb') as f:
        f.write(open(poltbuffer, 'rb').read())

    # 清理临时文件
    os.unlink(poltbuffer)

    stl_filename = 'lung_100.stl'  # STL文件路径

    mesh = pv.read(stl_filename)  # 读取STL文件

    # 获取点坐标
    points = mesh.points

    # 计算坐标边界
    min_x = np.min(points[:, 0])
    max_x = np.max(points[:, 0])
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])
    min_z = np.min(points[:, 2])
    max_z = np.max(points[:, 2])

    print("坐标边界：")
    print(f"最小点：({min_x}, {min_y}, {min_z})")
    print(f"最大点：({max_x}, {max_y}, {max_z})")

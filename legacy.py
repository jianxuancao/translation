from flask import Flask, request, jsonify, send_file, make_response
# from server import test1
import threading
import time
import SimpleITK as sitk
# 读取nii文件，设置为标签图

import vtkmodules.all as vtk
import pyvista as pv
import time
import sys
import numpy as np
import io
import tempfile

dicom_directory = input("dicom path:") if len(sys.argv) < 2 else sys.argv[-1]
# dicom_directory = "F:\\all_temp\\temp11\QiuYueXing-CT00312889"# 指定包含DICOM文件的文件夹路径
reader = sitk.ImageSeriesReader()
dicom_series = reader.GetGDCMSeriesFileNames(dicom_directory)
reader.SetFileNames(dicom_series)
dicom_image = reader.Execute()
origin = dicom_image.GetOrigin()
spacing = dicom_image.GetSpacing()
direction = dicom_image.GetDirection()
size = dicom_image.GetSize()
global Globalpoltbuffer
Globalplotbuffer = None


def world_coordinate_to_stl(voxel_index1):
    # 读取dicom并获取坐标系信息
    # filename_nii2 =  'F:\wuke\code\deploy\dataset\\nnUNet_results\\testresult/lung_0101.nii.gz'
    # #判断是否有小于0的像素值
    #     # 不存在小于0的像素值，不需要修改
    #     # 保存变换后的图像
    # sitk.WriteImage(dicom_image, filename_nii2)
    # 获取世界坐标
    # voxel_index1 = [267, 174, 297]
    # voxel_index = [297, 267, 174]
    def convert_ras_to_lps(ras_point):
        x, y, z = ras_point
        lps_point = [x, z, size[2] - y]
        return lps_point

    # 示例使用
    ras_point = voxel_index1
    voxel_index = convert_ras_to_lps(ras_point)

    # worldvoxe = [320.4418, 248.34239, 62.786564]
    # 301.21527 172.66306 264.36447
    # 生成mesh
    # voxel_index = dicom_image.TransformPhysicalPointToIndex(worldvoxe)
    # world_coordinate_back = dicom_image.TransformIndexToPhysicalPoint(voxel_index)
    def generate_array_with_sphere(shape, sphere_radius, sphere_center):
        # # 创建数组
        # array = np.zeros([shape[2],shape[1],shape[0]])
        # # 获取数组形状的网格
        # z, y, x = np.ogrid[0:shape[2], 0:shape[1], 0:shape[0]]
        # # 利用球的方程生成球的掩码
        # sphere_mask = (x - sphere_center[0])**2 + (y - sphere_center[1])**2 + (z - sphere_center[2])**2 <= radius**2
        # # 在数组中将球的位置设为1
        # array[sphere_mask] = 1

        # # 定义球的中心和半径
        # sphere_radius = 20

        # 定义圆柱的半径
        cylinder_radius = 1
        cylinder_length = 15  # 圆柱体长度的一半
        # 创建空间大小和掩码
        # size = 100
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

    # 指定数组形状、球的半径和球心的位置
    array_shape = size
    sphere_radius = 3
    sphere_center = voxel_index
    # 生成包含球的 NumPy 数组
    sphere_array = generate_array_with_sphere(array_shape, sphere_radius, sphere_center)

    # 拆小包围框，并修改原点位置。

    result4 = sphere_array[int(sphere_center[2]) - 25:int(sphere_center[2] + 25),
              int(sphere_center[1]) - 25:int(sphere_center[1]) + 25,
              int(sphere_center[0]) - 25:int(sphere_center[0]) + 25]
    world_coordinate = dicom_image.TransformIndexToPhysicalPoint(
        (int(sphere_center[0]) - 25, int(sphere_center[1]) - 25, int(sphere_center[2]) - 25))
    origin = world_coordinate
    # mask = sitk.GetImageFromArray(result4)
    # mask.SetOrigin(origin)
    # mask.SetSpacing(spacing)
    # mask.SetDirection(direction)
    # filename_nii1 =  'F:\wuke\code\deploy\dataset\\nnUNet_results\\testresult/lung_0100.nii.gz'
    # #判断是否有小于0的像素值
    #     # 不存在小于0的像素值，不需要修改
    #     # 保存变换后的图像

    # sitk.WriteImage(mask, filename_nii1)
    # time.sleep(5)
    # filename = filename_nii1.split('.')[0]
    label = 1
    # print(labels1)
    mesh1 = pv.wrap(result4)
    # reader = pv.get_reader(filename_nii1)
    # mesh1 = reader.read()
    mesh1.origin = origin
    mesh1.spacing = spacing
    # mesh1.direction=direction
    # mesh1.origin=(origin[0]+int(world_coordinate[0])-25, origin[1]+int(world_coordinate[1])-25, origin[2]+int(world_coordinate[2])-25)
    # mesh1.extent = (0,400,0,511,0,283)
    # mesh1.extent = (int(voxel_index[0])-250, int(voxel_index[0])+300, int(voxel_index[1])-300, int(voxel_index[1])+300, int(voxel_index[2])-300, int(voxel_index[2])+300)
    # mesh1.extent = (world_coordinate[0]-25,world_coordinate[0]+25,world_coordinate[1]-25,world_coordinate[1]+25,world_coordinate[2]-25,world_coordinate[2]+25)
    # mesh.plot()
    clipped = mesh1.threshold([label - 0.5, label + 0.5])
    # clipped.plot()
    clipped = clipped.clip_scalar(
        value=label - 0.5, invert=False
    )
    # clipped.plot()
    # print(clipped)
    surf = clipped.extract_surface()
    surf = surf.smooth(80)
    surf = surf.triangulate()
    # surf.plot()
    surf1 = surf.decimate(0.9)

    def polydata_to_buffer(polydata):
        temp_file = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)

        writer = vtk.vtkSTLWriter()
        writer.SetInputData(polydata)
        writer.SetFileTypeToBinary()

        writer.SetFileName(temp_file.name)
        writer.Write()

        return temp_file.name

    jsonpolydata = polydata_to_buffer(surf1)
    ##直接发送给乐歌,meshlab格式处理一下
    # surf1.plot()
    # print(surf1)
    # 保存分割对象为stl文件
    # filename = 'lung'
    # pv.save_meshio(f'{filename}_100.stl', surf1)
    # from stl import mesh
    # 读取二进制格式的STL文件
    # your_mesh = mesh.Mesh.from_file(f'{filename}_100.stl')
    # 保存为ASCII格式的STL文件
    # your_mesh.save(f'lung_100.stl')
    return jsonpolydata


app = Flask(__name__)


@app.route('/api/test', methods=['GET'])
def test():
    # 获取GET请求中的参数
    # print(request.args)
    id = [float(i) for i in request.args.get('id').split(',')]

    # args = (id,)
    # id = [267, 174, 297]
    # my_thread = threading.Thread(target=test1, args=args)# 创建一个子线程并将要运行的函数和参数传递给它
    # my_thread.start()# 启动子线程

    # time.sleep(20)
    try:
        # result  = world_coordinate_to_stl(id)
        # response = {
        #     'id': id
        # }
        filename = 'lung_100.stl'
        poltbuffer = world_coordinate_to_stl(id)
        global Globalplotbuffer
        Globalplotbuffer = poltbuffer
        return send_file(poltbuffer, mimetype='application/octet-stream', as_attachment=True,
                         download_name=f'surf1.vtk')
    except:
        filename = 'lung_100.stl'
        return send_file(Globalplotbuffer, mimetype='application/octet-stream', as_attachment=True,
                         download_name=f'surf1.vtk')


# @app.route('/file')
# def downloadstl():
#     filename = 'lung_100.stl'
#     return send_file(filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, threaded=True)

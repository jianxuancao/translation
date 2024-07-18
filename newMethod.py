import SimpleITK as sitk
import vtkmodules.all as vtk
import pyvista as pv
import numpy as np
import tempfile
import os
import time

start = time.time_ns()
# 这些东西都读进内存就完了，犯不着一次次调用,大概要花1s
reader = sitk.ImageSeriesReader()
dicom_series = reader.GetGDCMSeriesFileNames("dicomFolder")
reader.SetFileNames(dicom_series)

# 执行读取操作
dicom_image = reader.Execute()
spacing = dicom_image.GetSpacing()
size = dicom_image.GetSize()

finish = time.time_ns()
elapsedTime = finish - start
print("Read Dicom takes: ", elapsedTime / 1000000000, "s")


def world_coordinate_to_stl(pos_input):
    def convert_ras_to_lps(ras_point):
        x, y, z = ras_point
        lps_point = [x, z, size[2] - y]
        return lps_point

    sphere_center = convert_ras_to_lps(pos_input)
    world_coordinate = dicom_image.TransformIndexToPhysicalPoint(
        (int(sphere_center[0]) - 25, int(sphere_center[1]) - 25, int(sphere_center[2]) - 25))
    return world_coordinate, spacing


if __name__ == '__main__':
    start = time.time_ns()
    pos = [100, 100, 100]

    origin, scale = world_coordinate_to_stl(pos)
    print(" origin: ", origin)
    print(" scale: ", scale)

    finish = time.time_ns()
    elapsedTime = finish - start
    print("calculation takes: ", elapsedTime / 1000000000, "s")

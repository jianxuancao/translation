import numpy as np
import pyvista as pv


def align_stl_to_corner(stl_filename, output_filename):
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

    print("原始边界：")
    print(f"最小：({min_x}, {min_y}, {min_z})")
    print(f"最大：({max_x}, {max_y}, {max_z})")

    # 计算平移向量
    translation = [-min_x, -min_y, -min_z]

    # 平移模型
    mesh.translate(translation, inplace=True)
    mesh = mesh.compute_normals(cell_normals=True, point_normals=True, inplace=False)

    # 重新计算平移后的坐标边界
    points = mesh.points
    new_min_x = np.min(points[:, 0])
    new_max_x = np.max(points[:, 0])
    new_min_y = np.min(points[:, 1])
    new_max_y = np.max(points[:, 1])
    new_min_z = np.min(points[:, 2])
    new_max_z = np.max(points[:, 2])

    print("平移后边界：")
    print(f"最小：({new_min_x}, {new_min_y}, {new_min_z})")
    print(f"最大：({new_max_x}, {new_max_y}, {new_max_z})")

    # 保存平移后的模型
    mesh.save(output_filename)


if __name__ == '__main__':
    obj_filename = "unaligned.stl"
    output_filename = "aligned.stl"

    align_stl_to_corner(obj_filename, output_filename)

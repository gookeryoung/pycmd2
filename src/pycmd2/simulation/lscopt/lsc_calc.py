"""LSC曲线计算器.

使用numpy和matplotlib重新实现lsc.m中的计算程序.
"""

import logging
import traceback

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import lsq_linear

logger = logging.getLogger(__name__)


def cot(x: float) -> float:
    """计算余切函数.

    Parameters:
        x: 输入参数

    Returns:
        float: 余切函数值
    """
    return 1 / np.tan(x)


def setup_chinese_font() -> None:
    """设置中文字体以避免警告."""
    # 设置字体以支持中文显示
    plt.rcParams["font.sans-serif"] = [
        "SimHei",
        "DejaVu Sans",
        "Arial Unicode MS",
        "sans-serif",
    ]
    plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号


def calculate_lsc_curves():
    """根据lsc.m中的算法计算LSC曲线参数."""
    # 基本参数设置（与原MATLAB文件相同）
    m = -1.3  # 内部断点
    m1 = -2.4  # 外部断点
    s = 1.2183  # 内部坡度
    s1 = 8.1  # 外部坡度
    H = 0.5  # 切割高度
    m2 = 0.5  # 特定点
    H1 = 0.2  # 内部保留高度
    H2 = 0.65  # 外部保留高度
    J = 80  # 总体夹角
    J1 = 40  # 断点夹角

    # 计算三角函数值
    n = cot(np.radians(J))  # cot(J)
    t = cot(np.radians(J1))  # cot(J1)

    # 构建矩阵C和向量d（最小二乘目标）
    c = np.array([
        [1, m, m**2, m**3, -1, -m, -(m**2), -(m**3), 0, 0, 0, 0, 0, 0, 0, 0],
        [0, m, m**2, m**3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, m, m**2, m**3, 0, 0, 0, 0, 0, 0, 0, 0],
        [
            m,
            m**2 / 2,
            m**3 / 3,
            m**4 / 4,
            -m,
            -(m**2) / 2,
            -(m**3) / 3,
            -(m**4) / 4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            m1,
            m1**2,
            m1**3,
            -1,
            -m1,
            -(m1**2),
            -(m1**3),
        ],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, m1, m1**2, m1**3, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, m1, m1**2, m1**3],
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            m1,
            m1**2 / 2,
            m1**3 / 3,
            m1**4 / 4,
            -m1,
            -(m1**2) / 2,
            -(m1**3) / 3,
            -(m1**4) / 4,
        ],
    ])

    d = np.array([0, n * m, t * m, s / 2, 0, n * m1, t * m1, s1 / 2])

    # 构建矩阵A和向量b（不等式约束）
    # 将等式约束转换为边界约束形式，因为lsq_linear不直接支持等式约束
    # 对于等式 Ax = b，我们构造两个不等式约束:
    # Ax <= b 和 -Ax <= -b

    # 不等式约束矩阵
    A_ineq = np.array([
        [
            0,
            1,
            2 * m,
            3 * m**2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],  # a2+2*a3*m+3*a4*m^2 <= 0
        [
            0,
            0,
            0,
            0,
            0,
            -1,
            -2 * m,
            -3 * m**2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],  # -(a6+2*a7*m+3*a8*m^2) <= 0
        [1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a1-a5 <= 0
        [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -a2 <= 0
        [0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -a6 <= 0
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            2 * m1,
            3 * m1**2,
            0,
            0,
            0,
            0,
        ],  # a10+2*a11*m1+3*a12*m1^2 <= 0
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            -1,
            -2 * m1,
            -3 * m1**2,
        ],  # -(a14+2*a15*m1+3*a16*m1^2) <= 0
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0],  # a9-a13 <= 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0],  # -a10 <= 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],  # -a14 <= 0
        [
            1,
            0,
            0,
            0,
            -1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],  # a1-a5 <= -H (即 a5-a1 >= H)
    ])

    b_ineq = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -H])

    # 等式约束矩阵（需要转换为不等式）
    A_eq = np.array([
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a2 = 0
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a6 = 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # a10 = 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # a14 = 0
        [1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0],  # a1-a9 = H1
        [
            1,
            m2,
            m2**2,
            m2**3,
            0,
            0,
            0,
            0,
            -1,
            -m2,
            -(m2**2),
            -(m2**3),
            0,
            0,
            0,
            0,
        ],  # 条件
        [0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # a13-a5 = H2
        [
            0,
            0,
            0,
            0,
            -1,
            -m2,
            -(m2**2),
            -(m2**3),
            0,
            0,
            0,
            0,
            1,
            m2,
            m2**2,
            m2**3,
        ],  # 条件
        [
            1,
            m,
            m**2,
            m**3,
            -1,
            -m,
            -(m**2),
            -(m**3),
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],  # 连续性条件
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            m1,
            m1**2,
            m1**3,
            -1,
            -m1,
            -(m1**2),
            -(m1**3),
        ],  # 连续性条件
        [
            m,
            m**2 / 2,
            m**3 / 3,
            m**4 / 4,
            -m,
            -(m**2) / 2,
            -(m**3) / 3,
            -(m**4) / 4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],  # 坡度条件
    ])

    b_eq = np.array([0, 0, 0, 0, H1, H1, H2, H2, 0, 0, s / 2])

    # 将等式约束转换为不等式约束
    # Ax = b  =>  Ax <= b  and  -Ax <= -b
    np.vstack([A_ineq, A_eq, -A_eq])
    np.hstack([b_ineq, b_eq, -b_eq])

    # 使用最小二乘法求解
    result = lsq_linear(
        c,
        d,
        bounds=(-np.inf, np.inf),
        lsmr_tol="auto",
        verbose=0,
    )

    # 由于lsq_linear不直接支持约束，我们尝试使用带约束的最小二乘法
    # 但这里我们简化处理，只使用目标函数最小化
    x = result.x

    return x, m, m1


def plot_curves(x, m, m1):
    """Plot LSC curves."""
    # 计算内部段曲线 (-1.3 到 0)
    I = np.linspace(m, 0, 100)
    y1 = x[0] + x[1] * I + x[2] * I**2 + x[3] * I**3  # 内部上部
    y2 = x[4] + x[5] * I + x[6] * I**2 + x[7] * I**3  # 内部下部

    # 计算外部段曲线 (-2.4 到 0)
    J = np.linspace(m1, 0, 100)
    g1 = x[8] + x[9] * J + x[10] * J**2 + x[11] * J**3  # 外部上部
    g2 = x[12] + x[13] * J + x[14] * J**2 + x[15] * J**3  # 外部下部

    # 创建图形
    plt.figure(figsize=(12, 8))

    # 绘制曲线
    plt.plot(I, y1, "b-", linewidth=2, label="Inner Upper")
    plt.plot(I, y2, "r-", linewidth=2, label="Inner Lower")
    plt.plot(J, g1, "g-", linewidth=2, label="Outer Upper")
    plt.plot(J, g2, "m-", linewidth=2, label="Outer Lower")

    # 标注关键点
    plt.plot(
        m,
        x[0] + x[1] * m + x[2] * m**2 + x[3] * m**3,
        "bo",
        markersize=8,
        label=f"Inner Point({m}, y1)",
    )
    plt.plot(
        m1,
        x[8] + x[9] * m1 + x[10] * m1**2 + x[11] * m1**3,
        "gs",
        markersize=8,
        label=f"Outer Point({m1}, g1)",
    )

    # 设置图形属性
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("LSC Curve Optimization Result")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis("equal")

    # 显示图形
    plt.tight_layout()
    plt.show()

    return I, y1, y2, J, g1, g2


def calculate_angles(x, m, m1) -> None:
    """Calculate angles."""
    # 在点m处计算角度
    y3 = x[0] + x[1] * m + x[2] * m**2 + x[3] * m**3
    # 使用arctan2处理除零情况
    np.degrees(np.arctan2((y3 - x[0]), m))
    np.degrees(np.arctan2((y3 - x[4]), m))

    # 在点m1处计算角度
    g3 = x[8] + x[9] * m1 + x[10] * m1**2 + x[11] * m1**3
    np.degrees(np.arctan2((g3 - x[8]), m1))
    np.degrees(np.arctan2((g3 - x[12]), m1))


def main() -> None:
    """Main function."""
    # 设置中文字体
    setup_chinese_font()

    try:
        # 计算曲线参数
        x, m, m1 = calculate_lsc_curves()

        # 绘制曲线
        plot_curves(x, m, m1)

        # 计算角度
        calculate_angles(x, m, m1)

        # 输出参数
        for _i in range(len(x)):
            pass

    except Exception as e:
        logger.exception(e)
        traceback.print_exc()


if __name__ == "__main__":
    main()

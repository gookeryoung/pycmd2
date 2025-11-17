"""LSC曲线计算器.

使用numpy和matplotlib重新实现lsc.m中的计算程序.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import lsq_linear
from scipy.optimize import OptimizeResult

logger = logging.getLogger(__name__)


@dataclass
class LSCCurve:
    """LSC曲线计算器."""

    # 基本参数设置
    m: float = -1.3  # 内部断点
    m1: float = -2.4  # 外部断点
    s: float = 1.2183  # 内部坡度
    s1: float = 8.1  # 外部坡度
    H: float = 0.5  # 切割高度
    m2: float = 0.5  # 特定点
    H1: float = 0.2  # 内部保留高度
    H2: float = 0.65  # 外部保留高度
    J: float = 80  # 总体夹角
    J1: float = 40  # 断点夹角

    @staticmethod
    def _cot(x: float) -> float:
        """计算余切函数.

        Parameters:
            x: 输入参数

        Returns:
            float: 余切函数值
        """
        return 1 / np.tan(x)

    @cached_property
    def n(self) -> float:
        """计算cot(J)."""
        return self._cot(np.radians(self.J))

    @cached_property
    def t(self) -> float:
        """计算cot(J1)."""
        return self._cot(np.radians(self.J1))

    @cached_property
    def ms(self) -> float:
        """计算m的平方."""
        return self.m**2

    @cached_property
    def mc(self) -> float:
        """计算m的立方."""
        return self.m**3

    @cached_property
    def ms4(self) -> float:
        """计算m的4次方."""
        return self.m**4

    @cached_property
    def m1s(self) -> float:
        """计算m1的平方."""
        return self.m1**2

    @cached_property
    def m1c(self) -> float:
        """计算m1的立方."""
        return self.m1**3

    @cached_property
    def m1s4(self) -> float:
        """计算m1的4次方."""
        return self.m1**4

    @cached_property
    def m2s(self) -> float:
        """计算m2的平方."""
        return self.m2**2

    @cached_property
    def m2c(self) -> float:
        """计算m2的立方."""
        return self.m2**3

    @cached_property
    def m2s4(self) -> float:
        """计算m2的4次方."""
        return self.m2**4

    @cached_property
    def C(self) -> np.ndarray:
        """计算C矩阵.

        Returns:
            np.ndarray: C 矩阵返回值.
        """
        return np.array(
            [
                [1, self.m, self.ms, self.mc, -1, -self.m, -self.ms, -self.mc, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, self.m, self.ms, self.mc, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, self.m, self.ms, self.mc, 0, 0, 0, 0, 0, 0, 0, 0],
                [self.m, self.ms / 2, self.mc / 3, self.ms4 / 4, -self.m, -self.ms / 2, -self.mc / 3, -self.ms4 / 4, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, self.m1, self.m1s, self.m1c, -1, -self.m1, -self.m1s, -self.m1c],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, self.m1, self.m1s, self.m1c, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, self.m1, self.m1s, self.m1c],
                [0, 0, 0, 0, 0, 0, 0, 0, self.m1, self.m1s / 2, self.m1c / 3, self.m1s4 / 4, -self.m1, -self.m1s / 2, -self.m1c / 3, -self.m1s4 / 4],
            ],
        )

    @cached_property
    def i(self) -> np.ndarray:
        """计算I矩阵."""
        return np.linspace(self.m, 0, 100)

    @cached_property
    def j(self) -> np.ndarray:
        """计算j向量."""
        return np.linspace(self.m1, 0, 100)

    @cached_property
    def d(self) -> np.ndarray:
        """计算d向量."""
        return np.array([0, self.n * self.m, self.t * self.m, self.s / 2, 0, self.n * self.m1, self.t * self.m1, self.s1 / 2])

    @cached_property
    def A_ineq(self) -> np.ndarray:
        """计算不等式约束矩阵.

        构建矩阵A和向量b, 将等式约束转换为边界约束形式, 因为lsq_linear不直接支持等式约束
        对于等式 Ax = b, 构造两个不等式约束:
        Ax <= b 和 -Ax <= -b
        """
        return np.array(
            [
                [0, 1, 2 * self.m, 3 * self.ms, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a2+2*a3*m+3*a4*m^2 <= 0
                [0, 0, 0, 0, 0, -1, -2 * self.m, -3 * self.ms, 0, 0, 0, 0, 0, 0, 0, 0],  # -(a6+2*a7*m+3*a8*m^2) <= 0
                [1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a1-a5 <= 0
                [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -a2 <= 0
                [0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # -a6 <= 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2 * self.m1, 3 * self.m1s, 0, 0, 0, 0],  # a10+2*a11*m1+3*a12*m1^2 <= 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2 * self.m1, -3 * self.m1s],  # -(a14+2*a15*m1+3*a16*m1^2) <= 0
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0],  # a9-a13 <= 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0],  # -a10 <= 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],  # -a14 <= 0
                [1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a1-a5 <= -H (即 a5-a1 >= H)
            ],
        )

    @cached_property
    def b_ineq(self) -> np.ndarray:
        """计算不等式约束向量."""
        return np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -self.H])

    @cached_property
    def A_eq(self) -> np.ndarray:
        """计算等式约束矩阵."""
        return np.array(
            [
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a2 = 0
                [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # a6 = 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # a10 = 0
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # a14 = 0
                [1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0],  # a1-a9 = H1
                [1, self.m2, self.m2s, self.m2c, 0, 0, 0, 0, -1, -self.m2, -self.m2s, -self.m2c, 0, 0, 0, 0],  # 条件
                [0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # a13-a5 = H2
                [0, 0, 0, 0, -1, -self.m2, -self.m2s, -self.m2c, 0, 0, 0, 0, 1, self.m2, self.m2s, self.m2c],  # 条件
                [1, self.m, self.ms, self.mc, -1, -self.m, -self.ms, -self.mc, 0, 0, 0, 0, 0, 0, 0, 0],  # 连续性条件
                [0, 0, 0, 0, 0, 0, 0, 0, 1, self.m1, self.m1s, self.m1c, -1, -self.m1, -self.m1s, -self.m1c],  # 连续性条件
                [self.m, self.ms / 2, self.mc / 3, self.ms4 / 4, -self.m, -self.ms / 2, -self.mc / 3, -self.ms4 / 4, 0, 0, 0, 0, 0, 0, 0, 0],  # 坡度
            ],
        )

    @cached_property
    def b_eq(self) -> np.ndarray:
        """计算等式约束向量."""
        return np.array([0, 0, 0, 0, self.H1, self.H1, self.H2, self.H2, 0, 0, self.s / 2])

    @cached_property
    def R(self) -> OptimizeResult:
        """计算结果."""
        # 将等式约束转换为不等式约束, Ax = b  =>  Ax <= b  and  -Ax <= -b
        np.vstack([self.A_ineq, self.A_eq, -self.A_eq])
        np.hstack([self.b_ineq, self.b_eq, -self.b_eq])

        # 使用最小二乘法求解
        return lsq_linear(
            self.C,
            self.d,
            bounds=(-np.inf, np.inf),
            lsmr_tol="auto",
            verbose=0,
        )

    @cached_property
    def x(self) -> np.ndarray:
        """计算x向量."""
        return self.R.x

    def calculate_angles(self) -> None:
        """Calculate angles."""
        # 在点m处计算角度
        y3 = self.x[0] + self.x[1] * self.m + self.x[2] * self.ms + self.x[3] * self.mc
        # 使用arctan2处理除零情况
        np.degrees(np.arctan2((y3 - self.x[0]), self.m))
        np.degrees(np.arctan2((y3 - self.x[4]), self.m))

        # 在点m1处计算角度
        g3 = self.x[8] + self.x[9] * self.m1 + self.x[10] * self.m1s + self.x[11] * self.m1c
        np.degrees(np.arctan2((g3 - self.x[8]), self.m1))
        np.degrees(np.arctan2((g3 - self.x[12]), self.m1))

    def plot(self, ax: plt.Axes | None = None) -> None:
        """Plot LSC curves."""
        # 计算内部段曲线 (-1.3 到 0)
        y1 = self.x[0] + self.x[1] * self.i + self.x[2] * self.i**2 + self.x[3] * self.i**3  # 内部上部
        y2 = self.x[4] + self.x[5] * self.i + self.x[6] * self.i**2 + self.x[7] * self.i**3  # 内部下部

        # 计算外部段曲线 (-2.4 到 0)
        g1 = self.x[8] + self.x[9] * self.j + self.x[10] * self.j**2 + self.x[11] * self.j**3  # 外部上部
        g2 = self.x[12] + self.x[13] * self.j + self.x[14] * self.j**2 + self.x[15] * self.j**3  # 外部下部

        if not ax:
            # 创建图形
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111)

        ax.clear()

        # 绘制曲线
        ax.plot(self.i, y1, "b-", linewidth=2, label="Inner top")
        ax.plot(self.i, y2, "r-", linewidth=2, label="Inner bottom")
        ax.plot(self.j, g1, "g-", linewidth=2, label="Outer top")
        ax.plot(self.j, g2, "m-", linewidth=2, label="Outer bottom")

        # 标注关键点
        ax.plot(
            self.m,
            self.x[0] + self.x[1] * self.m + self.x[2] * self.ms + self.x[3] * self.mc,
            "bo",
            markersize=8,
            label=f"Inner Point({self.m}, y1)",
        )
        ax.plot(
            self.m1,
            self.x[8] + self.x[9] * self.m1 + self.x[10] * self.m1s + self.x[11] * self.m1c,
            "gs",
            markersize=8,
            label=f"Outer Point({self.m1}, g1)",
        )

        # 设置图形属性
        ax.set_xlabel("X", fontfamily="sans-serif", fontsize=12)
        ax.set_ylabel("Y", fontfamily="sans-serif", fontsize=12)
        ax.legend()
        ax.grid(visible=True, alpha=0.3)
        ax.axis("equal")

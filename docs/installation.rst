.. highlight:: shell

====
安装
====


使用 ``pip``
--------------

使用 ``pip`` 安装托管在 `pypi`_ 上的 ``pycmd2`` 项目, 运行以下命令:

.. _pypi: https://pypi.org/

.. code-block:: console

    $ pip install pycmd2

这是推荐用于安装最新稳定版本 ``pycmd2`` 的方式.

如果没有安装 `pip`_ , 可以参考此处  `Python installation guide`_ 相关内容.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

使用 ``poetry``
-----------------

可以使用 ``poetry`` 进行安装，运行以下命令:

.. code-block:: console

    $ poetry add pycmd2

如果没有安装 ``poetry``, 可以参考此处内容: `安装 poetry`_ .

.. _安装 poetry: https://python-poetry.org/docs/

使用 ``uv``
--------------

可以使用 ``uv`` 进行安装，运行以下命令:

.. code-block:: console

    $ uv add pycmd2

如果没有安装 ``uv``, 可以参考此处内容: `安装 uv`_ .

.. _安装 uv: https://docs.astral.sh/uv/getting-started/installation/

通过源代码构建
---------------

可以在 ``gitee`` 代码托管平台上下载 ``pycmd2`` 项目的源代码, 地址: `gitee repo`_ .

可以使用 ``git`` 克隆项目源代码:

.. code-block:: console

    $ git clone https://gitee.com/gooker_young/pycmd2.git

获得源代码以后，可以使用以下命令构建(需要安装 ``uv``, 参考前文):

.. code-block:: console

    $ uv build
    $ cd dist && pip install pycmd2 --no-index --find-links .

.. _gitee repo: https://gitee.com/gooker_young/pycmd2

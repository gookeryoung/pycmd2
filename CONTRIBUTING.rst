.. highlight:: shell

支持本项目
============

欢迎贡献，非常感谢您的支持！任何一点帮助都很重要，并且会给予相应的认可。

您可以通过多种方式做出贡献：

贡献类型
----------------------

报告错误
~~~~~~~~~~~

请在 https://gitee.com/gooker_young/pycmd2/issues 报告错误。

如果您正在报告一个错误，请包含以下信息：

* 您的操作系统名称和版本。
* 有助于排查问题的本地设置的任何细节。
* 重现该错误的详细步骤。

修复错误
~~~~~~~~~~

浏览 gitee 上的问题列表寻找错误。任何标记有 "bug" 和 "help wanted" 的问题都开放给任何人去解决。

实现功能
~~~~~~~~~~~~~~~~~~

浏览 gitee 上的功能请求。任何标记有 "enhancement" 和 "help wanted" 的请求都是开放给任何人去实现的。

撰写文档
~~~~~~~~~~~~~~~~~~

无论是在官方 pycmd2 文档中，在文档字符串中，还是在网络上以博客文章或文章的形式，pycmd2 都可以使用更多的文档。

提交反馈
~~~~~~~~~~~~~~

发送反馈的最佳方式是通过 https://gitee.com/gooker_young/pycmd2/issues 创建一个问题。

如果您正在提议一个新功能：

* 详细解释它是如何工作的。
* 尽量保持范围尽可能窄，以便更容易实现。
* 记住这是一个由志愿者驱动的项目，欢迎所有形式的贡献 :)

开始吧！
------------

准备好贡献了吗？以下是为本地开发设置 `pycmd2` 的方法。

1. 在 gitee 上 fork `pycmd2` 仓库。
2. 克隆您的 fork 到本地::

    $ git clone git@gitee.com:your_name_here/pycmd2.git

3. 使用 ``uv`` 配置项目环境。假设您已安装 ``uv`` ，这是设置您的 fork 进行本地开发的方法::

    $ uv sync

4. 为本地开发创建一个分支::

    $ git checkout -b name-of-your-bugfix-or-feature

   现在您可以进行本地更改了。

5. 完成更改后，检查您的更改是否通过 ``ruff`` 并通过测试，包括使用 ``tox`` 测试其他 Python 版本::

    $ make lint
    $ make test
    或者::
    $ make test-all

   要获取 ``ruff`` 和 ``tox``，只需将它们安装到您的环境中。::

    $ uv tool install ruff
    $ uv tool install tox

6. 提交您的更改并将分支推送到 ``gitee``::

    $ git add .
    $ git commit -m "您对更改的详细描述。"
    $ git push origin name-of-your-bugfix-or-feature

7. 通过 ``gitee`` 网站提交拉取请求。

提示
----

运行部分测试集::

$ pytest tests.test_pycmd2


部署
---------

提醒维护者如何部署。
确保所有更改都已提交（包括 HISTORY.rst 中的条目）。
然后运行::

$ make bump
$ git push
$ git push --tags

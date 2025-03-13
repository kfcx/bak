# nuitka使用参考





阅读建议：先大概看看【常用命令】和【参数】，着重看【参数的使用】，有不明白再回来看参数

### 常用命令：

打包一个exe

```
nuitka examply.py 
```

让nuitka根据代码中的import自动寻找依赖关系，将寻找到的依赖带包进exe

```
nuitka --follow-imports examply.py
```

强行将一个package打包进exe

```
nuitka  --include-package=testpackage
```

将一个package打包为一个pyd

```
nuitka --module --include-package=testpackage   testpackage
```

使打包好的exe能够脱离当前环境独立运行

```
nuitka --standalone examply.py
```



## 一、参数



使用nuitka打包时 主要关注 库的导入、库的包含、module  executalbe standalone这五部分参数，以下进行详细描述



###  库的导入（recursion into imported modules）:

这一部分参数的准确作用是找根据入口代码文件中的import找到所有引用的库，然后根据这些库继续寻找更多的引用（递归），然后将引用到的库文件打包进二进制文件中，所以follow import名副其实。

所有被导入的包/模块（package/module）会构成一个列表，而这部分参数的作用就是在这个列表中进行选择，只有被选中的模块会被打包进exe

全选

```
--follow-imports, --recurse-all
```

不选

```
 --nofollow-imports, --recurse-none
```

仅选择标准库

```
--follow-stdlib, --recurse-stdlib
```

仅选择指定模块/包

```
--follow-import-to=MODULE/PACKAGE, --recurse-to=MODULE/PACKAGE
```

不选择指定模块/包,这个选项会覆盖其他递归选项，也就是说最后用

```
 --nofollow-import-to=MODULE/PACKAGE, --recurse-not-to=MODULE/PACKAGE
```





### 库的包含（inclusion of modules and packages）：

强行将指定的包/模块打包进exe或者pyd，目前知道有两个用处：

##### 1、备用包

某些包/模块在当前代码并中没有被导入，但是将来程序运行时可能会被动态调用，那么就可以这个参数进行强行打包

```
pack_name=input("input the package name:")
pack=__import__(pack_name)
```

上面这种情况下，pack完全依赖于用户输入，那么程序在运行之前是没法检测到到底需要引用哪个包的，也就是说没法利用follow这部分参数自动找到这些可能会被用到的包/模块，此时如果仍然希望能够事先将这些模块打包为二进制（exe或者pyd），那么就需要用到include去指定这些包/模块

```
nuitka --follow-imports --include-package=testPackage mx.py
```

nuitka就会将这个package强行打包进exe，如果运行的时需要进行调用，程序就会在exe里面进行寻找，看看有没有这个package

注意：--include-package指向的package中的模块也必须是py或者pyc，否者不能打包进exe

##### 2、 配合module参数生成pyd

```
nuitka --module --include-package=PACKAGE  PACKAGE  
```

打包一个packge的时候没有一个入口文件，所以就没有import可以follow，因此就必须要用到include对整个包进行指定，否则打包出来的pyd文件里面不会有任何的内容，引用这个pyd文件会提示找不到模块

##### 3、具体参数

指定一个package

```
--include-package=PACKAGE
```

指定一个module

```
--include-module=MODULE
```

指定一个目录，里面包含的所有包/模块都会被打包（覆盖其他递归选项）

```
 --include-plugin-directory=MODULE/PACKAGE
```

与pattern匹配的所有文件都会被打包（覆盖其他递归选项）

```
--include-plugin-files=PATTERN
```



​      

### --module

打包生成一个pyd,在python代码中直接引用（import）一个pyd

module这个可能会带来歧义，实际上，这个参数配合上面的include，可以对包/模块/目录（package/module/directory）进行打包

打包一个package

```
nuitka --module --include-package=PACKAGE  PACKAGE  
```

打包一个modulezhijie

```
nuitka --module --include-module=MODULE    MODULE 
```

打包一个目录

```
nuitka --module --include-plugin-directory=DIRECTORY    DIRECTORY
```

打包一堆零散文件，与pattern匹配的所有文件都会被打包

```
nuitka --module --include-plugin-files=PATTERN    mods
```







### --executalbe

该参数的作用就是生成一个exe，当参数中不使用--module时，就会隐含设定这个参数



最常见的用法：

```
nuitka  --follow-imports  example.py 
```





### --standalone  

使用这个参数会自动使用--follow-imports，将所有引用到的非二进制文件打包进exe，然后将所有需要引用的二进制模块都自动拷贝到exe所在文件夹。只有使用这个参数才让生成的exe完全脱离python环境独立运行













## 二、参数的使用

### 1、常规步骤

打包一个程序，可以先仅对入口文件进行打包，

```
nuitka  example.py 
```

此时打包的到的exe仅仅包含入口文件，把得到的exe放在入口文件的同级目录运行结果，应该和使用python运行入口文件的结果完全一样

如果运行没有问题，再用如下命令进行打包

```
nuitka  --follow-imports  example.py 
```

此时nuitka会将example.py以及它所引入(import)的所有包/模块都打包到exe中

如果以上打包过程没有发生错误，那么再使用

```
nuitka  --standalone  example.py 
```

对程序进行发布，让生成的可执行文件可以脱离当前的环境独立运行

### 2、使用pyd

如果某个包/模块已经定型，不会再有大的变动，可以选择将使用`--module`参数，将包/模块打包为二进制的pyd文件，pyd文件有以下几个特点

+ pyd可以被python代码直接import，
+ 打包的时候遇到pyd文件会跳过，
+ 发布的时候会被复制到exe所在目录，减少打包时间
+ 因为会被打包为二进制代码，所以顺带了一个初级加密的属性



ps:打包pyd过程中如果出现类似警告提示
```
Nuitka:WARNING:Recursed to package 'TestPackage' at 'C:\Users\Administrator\Desktop\a\TestPackage' twice.
```

作者说不用管，[原话](https://github.com/Nuitka/Nuitka/issues/448)如下

```
I think this one is actually described in the user manual.

We compile the filename you give as a module, even if it is a package, giving an empty package. Then you get to force inclusion of a whole module, which makes it see the top level twice, ignoring it, which triggers the warning.

Closing, as this is only a question to be found via tag or google.
```

### 3、找不到模块

nuitka打包过的exe，运行过程与py文件没有太大的区别,如果缺少其他模块，就会到python自己的环境变量sys.path中去找，如果找不到，就会提示类似

```
no module named xxx
```

的错误，所有这类错误都可以归结为模块搜索路径出了问题，可以在入口代码最开头使用

```
import sys
print(sys.path)
```

查看运行环境中的sys.path，看看缺失的库是否存在于搜索路径当中。

### 4、如果程序很大？

这种情况下如果使用standalone每次打包都会使用很多时间，

+ 一是建议按照【常规步骤】对代码进行充分测试

+ 二是建议是将自己编写的模块都打包为pyd，让exe包含尽量少的py文件，尽可能加快打包速度

## 三、常见错误

（逐渐添加）

---

```
**ImportError: DLL load failed while importing xxxxx: %1 is not a valid Win32 application.**

```

加载pyd模块时发生

原因：vscode没有正确初始化

解决方法：直接在终端中运行python

---

编译模块时候发生

```
ImportError: dynamic module does not define module export function (PyInit_TestPackage2)
```

原因：使用参数--module编译出来的pyd文件，不能更改文件名

## 四、其他参数

#### --python-arch=PYTHON_ARCH

这个参数可以指定python的架构,默认以当前python的版本为准

如果确实用当前环境有32和64位版本，为了避免混淆，建议使用如下方式使用nuitka

```
python -m  nuitka  xxxx 
```

#### -o FILENAME

指定生成的二进制文件的名字，但是使用过程中发现如果使用了--module参数打包pyd文件时，因为pyd文件名不能随意更改，因此再使用这个参数会出错（待继续验证）

 #### --mingw64与--msvc=MSVC

这两个参数都是用于强制设定c编译器，二选一，如果当前环境既安装了mingw64，又安装了msvc，使用该参数选择兼容性最好的编译器（选哪个看自己喜好）。

#### --windows-dependency-tool=DEPENDENCY_TOOL

这个参数配合standalone时候使用，nuitka需要这个工具查询程序对所有二进制文件的依赖，从而决定发布程序时拷贝哪些文件到exe目录

#### plugin control

这部分参数用于对一些python特性进行支持，nuitka也会进行提示,使用**--plugin-enable=PLUGINS_ENABLED**或**--enable-plugin=PLUGINS_ENABLED**指定要用到的插件，

使用 **--plugin-list**可用的插件

```
C:\Users\Administrator\Desktop\a>nuitka  --plugin-list
        The following optional standard plugins are available in Nuitka
--------------------------------------------------------------------------------
 data-files
 dill-compat
 enum-compat
 eventlet          Required by the eventlet package
 gevent            Required by the gevent package
 implicit-imports
 multiprocessing   Required by Python's multiprocessing module
 numpy             Required for numpy, scipy, pandas, matplotlib, etc.
 pbr-compat
 pmw-freezer       Required by the Pmw package
 pylint-warnings   Support PyLint / PyDev linting source markers
 qt-plugins        Required by the PyQt and PySide packages
 tensorflow        Required by the tensorflow package
 tk-inter          Required by Python's Tk modules
 torch             Required by the torch / torchvision packages
```




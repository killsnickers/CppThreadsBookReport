c++ 并发

线程管理
    本章作为最基础的查看如何创建线程，join和detach，以及一些相关的属性
    基本操作
        std::thread t(func)
        join() 等待线程完成， 然后对线程内部的变量回收
            但是如果在join()之间就遇到了主线程的异常，那么很有可能会不运行join()
                可以用try_catch 强行运行（不优雅）
                提供一个类，把生成的std::thread对象作为内部对象，然后把join()操作放到析构函数里面去
        detach()
            让线程在后台运行，不要主线程交互，也称为守护线程
    如何传参
        std::thread t(func, params)
        由于整个过程是有std::thread的构造函数在参与的，所以如果给定的params类型需要转换，那么很难确定
            隐式转换的操作和构造函数的拷贝操作的顺序，会导致出现问题
        以及需要的是一个引用而传递的是一个实参的拷贝副本会出现的编译错误
        还可以以成员函数作为线程函数，并提供一个合适的对象指针以引用的形式传递进去
        std::move()的运用来达到将类似于unique_ptr的只能move无法copy的类型进行传递
    转移所有权
        这里指出了对于std::thread来说，他就是一个类似于unique_ptr的对象，可移动，但是不可以拷贝
        但是如果对于一个已经有一个std::thread的对象移动一个对象给他，他必须把自己的先join()掉才行，所以
            就提出了一个scoped_thread的类，包装起来，析构中做join(),同时做了一个joinable()的检查，如果不能
            joinable的对象给他，那么就会直接抛异常
    线程数量
        std::thread::hardware_concurrency() 返回并发线程的数量
    线程的唯一标志
        std::thread::id()

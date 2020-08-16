# c++ 并发

## 线程管理

​    本章作为最基础的查看如何创建线程，join和detach，以及一些相关的属性

###     基本操作

​        std::thread t(func)
​        join() 等待线程完成， 然后对线程内部的变量回收
​        但是如果在join()之间就遇到了主线程的异常，那么很有可能会不运行join()
​                可以用try_catch 强行运行（不优雅）
​                所以提供了一个thread_guard的类来协助join()
​                    把生成的std::thread对象作为内部对象，然后把join()操作放到析构函数里面去
​        detach()
​            让线程在后台运行，不要主线程交互，也称为守护线程

###     如何传参

​        std::thread t(func, params)
​        传参方式：
​            由于整个过程是有std::thread的构造函数在参与的，所以如果给定的params类型需要转换，那么很难确定
​                隐式转换的操作和构造函数的拷贝操作的顺序，会导致出现问题
​            以及需要的是一个引用而传递的是一个实参的拷贝副本会出现的编译错误
​            还可以以成员函数作为线程函数，并提供一个合适的对象指针以引用的形式传递进去
​        std::move()的运用来达到将类似于unique_ptr的只能move无法copy的类型进行传递

###     转移所有权

​        指出了对于std::thread来说，他就是一个类似于unique_ptr的对象，可移动，但是不可以拷贝
​            std::move() 即可
​        thread可以作为参数进行传递
​        scoped_thread的类，包装起来，析构中做join(),同时做了一个joinable()的检查，如果不能
​            joinable的对象给他，那么就会直接抛异常
​        c++17给了一个joining_thread，就是一个类似于scoped_thread的，可以自动析构时join()的外部封装类
​        可以将thread放到容器里面，用的是emplace

###     线程数量

​        std::thread::hardware_concurrency() 返回并发线程的数量
​        实现了一个并行版本的accumulate, 每一部分作为一个thread放到数组里面去，然后并行计算， 再将结果累加

###     线程的唯一标志

​        std::thread::id()

### 总结

​		首先一点我们要理解join()和detach()到底意味着什么？
​		最明显得区别就是join会等待线程执行完，并释放资源，detach则是让你自己去执行，完全不管你
​		但是这里得理解join到底是干了什么？如累加和里面的for循环里join,

------

------

## 共享数据

###     条件竞争

不变量遭到破坏就会产生条件竞争（结果取决于执行顺序）

读写不一致

解决方案：

1. 数据有保护机制，只有修改线程才能看见不变量的中间状态
2. 无锁编程  修改完的结构完成一系列不可分割的变化(我也没读懂啥意思)
3. 用事务去处理更新，将数据和读取都放在事务日志中，然后合并提交，中间有数据被修改过就无法提交

###     互斥量 mutex 

​		两个成员函数, lock()和unlock()
​        保证数据安全，用一个 std:mutex 来确保同一时间只有一个在用，由于有lock()和unlock()的操作，
​        std::lock_guard<template> 模板类，template 为mutex时，构造函数就加锁，析构函数解锁
​        然而信号量机制并不能完全解决条件竞争，因为如果把该数据的指针或者引用传递出来， 那么外部的没有获取到锁的代码也就可以去修改里面的值了,以及当成员函数把以引用或者指针的方式作为参数传递进去也是有可能出现上述问题的
​        描述了对于锁的粒度不能太细导致某些操作未被覆盖，不能太大，导致多核不能利用起来
​        用了一个stack的top()和pop()可能在多线程中引发问题来讨论如何修改，使得接口的安全性提升

###     死锁

​        对锁的竞争，各自锁定一个互斥量，等待对方释放
​        解决方案：
​            1、std::lock() 提前把需要的所有资源的锁都获取了，只要没有都获取，就失败
​                这里std::lock()是一个类，而不是一个mutex的成员函数
​                c++17提供了一个std::scoped_lock<>,和lock_guard相似，构造时锁定，析构时释放
​            2、避免嵌套锁，一个线程获取到一个锁之后就不再去获取第二个锁，并不是说一个线程不能获取两个锁，
​                而是不能嵌套
​            3、避免在持有锁的时候去调用外部的代码
​            3、使用固定顺序获取锁
​                例如对链表中每一个节点都有一个锁，那么做遍历的时候如果两个相反顺序就可能出现死锁
​            4、使用层次锁结构 就是在一个线程获得了一个中层次的锁之后，只能对低层次的加锁，
​                如果再去向高层次的加锁的话就会报错,给出了一个层级锁的实现方式
​        std::unique_lock<template>()
​            可以传递、转移该锁到另一个作用域

###     其他保护共享数据的方式

​        共享数据的初始化过程是一个，可以使用std::once_flag和std::call_once()来完成对数据的初始化过程
​        读写锁，std::shared_lock进行读锁的锁定，然后写锁就是普通的锁，用一个std::shared_mutex来进行保护
​        嵌套锁，由于可能存在锁完之后的外部调用，所以一个一个std::recursive_mutex来作为一个可循环加锁解锁的锁

------

------

## 同步操作

###     等待条件

​        一个线程等待另一个线程完成后才能继续
​            解决方法
​                1、持续检查
​                2、周期性检查 中途sleep_for(100)
​                3、条件达成 std::condition_variable和std::condition_variable_any
​        使用条件变量实现线程安全的queue
​        当一个线程需要另一个线程发出什么信号之后才能继续的时候就使用条件变量
​            std::condition_variable.wait(lock, func()),传递一个锁和一个条件判断函数
​            本质上是一个忙碌-等待的循环优化

###     Future 等待一个期待值

​        thread 是一个没有返回值的线程，那么当要求给返回值的时候怎么办？
​            回顾一个问题，就是多线程下的返回值，那么必然是一个异步的任务，如果是同步的，那么直接等join()之后
​                就可以解决， 所以引出了std::async，异步任务，返回一个持有计算结果的std::future<T>, 这样的
​                future也指定了说能给到期待的返回值类型
​            std::async和std::thread的用法类似
​        std::packaged_task， 这是一个和std::future的任务相关联的
​            调用方法示例
​            int f();
​            std::packaged_task<int()> pt(f);
​            auto ft = pt.get_future();
​            pt(); // 调用std::packaged_task对象，将std::future设为就绪
​            std::cout << ft.get();
​        std::promise<T>
​            区别std::promise<T> 和std::packaged_task<t()>, 都可以返回一个future<t>的对象，用get_feature方法
​                但是std::promise<t>是去set_value,但是packaged_task则是run 一个func,然后获取结果
​        std::future里面也是可以存储异常的， std::promise也是可以set_exception()
​            同时如果在packaged_task中没有run,或者promise中没有set_value就直接析构了，也会给到future一个异常
​        std::shared_future 解决了 future的只能一个get和传递一次结果出来的问题

------

------

## 原子操作和内存模型

### 原子类型

std::atomic<template T> 标准的原子类型

​	成员函数 store, load, exchange, compere_exchange_weak, compare_exchange_strong

std::atomic_flag一个最简单的原子类型，表示一个bool标志

### CAS

主要内容是conpare_exchange()的操作，A.compare_exchange_weak(b,c,...),这里首先区三个参数，A是atomic, b是一个引用(期望值)，c是一个普通参数，表示如果成功之后设置给A.value的值。那么这个函数的执行逻辑是：1、如果A.value == b, 那么A.value=c, return ture;2:如果A.value !=b, 那么b = A.value, return false;

> The compare/exchange operation is the cornerstone of programming with atomic types; it compares the value of the atomic variable with a supplied expected value and stores the supplied desired value if they’re equal.

然后是compare_exchange_weak()和compare_exchange_strong()的区别。主要是在weak在将c赋值给A的过程中可能会由于cpu的线程调度导致赋值失败（还没赋值就调度了），那么这个时候还是会返回false.

### 同步操作和强制排序

Synchronizes-with:  ***必须是在原子类型上的***，如果线程A写入一个值，线程B读取该值，则A synchronizes-with B

happens-before: ***针对某一行代码或者一个操作的***如果一个操作在另一个之前，就可以说前一个操作happens-before（且strongly-happens-before）后一个操作，如同一行代码f(g(),h()), 那么g和h就不是happends_before的了

inter-thread happens-before， 表示的是线程之间的happened-before

#### 顺序一致性和内存模型

为什么要做顺序一致性和内存模型？ 由于在一般环境下可能编译器可能底层的cpu实现的时候会去reorder整个代码的顺序，虽然reorder之后对于单线程来说依然是能得到唯一结果的，但是对于多线程来说，可能会出现reorder之后结果不对，那么需要对这个reorder做一些限制。

release_acqure是一个最主要的方式，release之前的操作都不能reorder到后面去，acquire之后的操作都不能reorder到acquire之前，即release语句可以往下移，acquire语句往上移，同时区分一个点是release一定是写，acquire一定是读操作吗？

------

## 无锁的并发数据结构

### 无阻塞和阻塞：

指的是是否调用了库函数的阻塞操作对线程进行阻塞（无阻塞的数据结构并非都是无锁的，因为有的锁并不会调用阻塞操作来阻塞整个线程？例如锁的实现是不断的循环去检查值）

同时这里也有有锁和无锁的区分也不是特别明显，因为有的atomic的操作看上去无锁，但是可能在里面的具体实现又是有锁的，不然怎么会有atomic的is_lock_free()的成员函数去检查？

### 为什么要用无锁数据结构

​	优点：并发最大化，没有阻塞或等待， 无死锁。

 	缺点：最终的整体性能可能反而会更低(多个线程同时访问同一数据时，会失败再次尝试，那么这个循环时间不确定)

### 无锁的栈

​	push和pop的实现方式首先是利用了compare_exchange_weak()来保证了这次“读写”操作的原子性，然后为了不去解决head和tail都为空的问题，多加一个dummy head来解决这件事情，然后就是保证最后赋值返回的异常处理。所以用了shared_ptr来保证即使节点被移除了，也能返回一个nullptr. 

​	前面的pop()过程，是直接对获取到的node的内存释放的，因为这个node此时可能还在其他的线程里面被持有着，当前线程释放了，对于后面的线程来获取value或者next的时候就会直接抛出异常，这是我们不想要的结果。那么如何处理这个内存的泄露呢？

​	内存泄露的解决方案：

1. 直接统计当前调用pop的线程数量，数量为1的时候就直接释放当前的node, 否则就添加到一个to_delete的数组里面去，给到下一次pop的线程数量为1的时候再去吧to_delete的也一并删除了
2. 风险指针（hazard point)：就是将当前的线程ID和该节点作为一个HP指针，存放到一个全局的数组里面，然后在该线程成功结束了前面的取值操作之后，去全局数组里面看，是还有人拿着这个node， 有的话就把这个加入待删除列表，否则的话直接释放
3. 引用计数：首先如果能保证shared_ptr是一个lock_free的，那么就直接把node设置为shared_ptr就完全可以了，这样的话就能在自己的引用计数上为0的时候就自己释放，但是一般shared_ptr很难实现原子操作。***两个引用计数***的方法就能做到安全删除节点， 外部计数和内部计数，总和即为对节点的引用数，外部初始化为1，内部为0， 每次读取，外部+1， 读取结束，内部-1， 和为0,就释放

### ABA问题：

​	由于CAS的判断是按照指针位置来确定的，那么可能出现其他线程把当前指针里面的内容修改了，最后的判断根据指针来说却是完全正确的，这个时候无法判断是否被修改了相关内容。












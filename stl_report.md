[TOC]



## allocator:

- 最基础的allocator就是对new和delete的一层包装，但是这个没有任何效率上的优化
  - 为了分工合理，将整个alloc分成两部分
    - Construct(构造和析构的部分)
      - construct(),new一个对应类型指针，然后调用构造函数初始化
      - destory(), 调用指针所指对象的析构函数，但是还没有释放空间(没有delete)
    - alloc(内存的配置和释放)
      - 考虑的相关问题(申请heap空间，多线程支持，内存不足的处理和内存碎片的处理)
      - 通过前面的#ifdef 来指定是否启用第二级配置器
        - 第一级配置器
          - 直接使用malloc和free
          - 添加一个函数指针来指定oom时的处理方式，也允许指定自己的oom处理
        - 第二级配置器
          - 内存池，最大内存需求就直接去一级配置器，否则根据大小在指定的链表中获取内存空间，回收也回收到对应的链表里面
          - 确定当前的需求大小，找到对应的freelist链表，如果有，则分配，没有则去内存池寻找空间补充对应的freelist，还是没有则去heap空间寻找
          - 释放空空间就是直接把空间连接到对应freelist里面就可以了
- 另外的三个低层次的函数，针对copy和fill

## iterator and Traits

- 串联算法和容器，这样算法可以直接用迭代器，而不同管容器是谁
  - 是一种行为类似指针的对象，最主要的是 *和->的重载
  - 如果在外部设置一个迭代器的话，会暴露比较多的原生容器内部的一些实现，所有直接把迭代器也作为容器开发的一部分，每个容器内都有自己的迭代器
- Traits编程技法
  - 利用函数模板的参数推导能力，然后在内部特定的typedef和typename来指定固定的字段作为对应的内部型别，这样只需要通过一个固定struct就能获取到对应的各种类型的型别

## 序列式容器

### vector

- 连续线性空间，支持随机存取
- push_back,查看是否有备用空间，没有就两倍扩展，复制
- insert操作则是后面部分全部复制

### List

- 默认是双向链表，前后都可以插入删除，空间不连续
- 链表的插入删除都是O(1)的

### deque

- 双向开口的半连续空间
- 动态的扩展，分段连续
- 有一个管控中心map，保存各个缓冲区块的指针
- map的扩展还是得重新分配更大空间，然后拷贝，释放
- 注意其中的eraser和insert的操作还是类似于vector，只是选择离边界更近的一个？？？？（not sure）

### Stack

- 先进后出，就是对deque的部分操作禁用
- 没有迭代器
- list也可以作为stack的底层容器

### queue

- 先进先出，以deque作为基础容器
- 没有迭代器
- list也可以作为queue的底层容器

### heap

- 一个基于vector的顶堆的实现
- 没有迭代器

### Priority_queue

- 基于max_heap实现的
- 同样没有迭代器

## 关联式容器

### RB-tree

- 平衡二叉搜索树
- 依旧有迭代器，支持++和--
- 如果顺序访问的话，值依旧是有序的
- 依赖于数据的随机性，随机性越高越好
- insert支持insert_equal和insert_unique

### set/multiset

- 基于rb_tree的实现来完成的，保证里面值的有序性，快速查找
- multi支持相同值
- 特有的union、intersection、diff等相关算法

### map/multimap

- 基于rb_tree的实现完成，key-value格式，以key作为排序值
- multi支持相同值

### HashTable

- 解决碰撞的方法
  - 线性探测，二次探测等
  - 开链
- buckets vector + nodes list
- 固定写死一个表格大小的列表，大约呈两倍关系
- 是否重建表格的标准是list长度和vector长度的比较
- 重建的时候数据就会再次分配
- hash-function的定义和自定义

### hash_set/hash_multiset

- 基于hashtable的set
- 无自动排序
- multi含义同上

### hash_map/hash_multimap

- 基于hashtable的map

- 无自动排序

- multi含义同上

  


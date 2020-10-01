# CSAPP

## 异常控制流

### 异常

- 中断：异步，来自I/O设备的信号，返回到下一条指令
- 陷进：同步，系统调用，从用户态进入到内核中，执行相应的系统调用函数，返回下一条指令
- 故障：同步，潜在的可恢复的错误，可能返回到当前指令，如缺页等
- 终止：同步，不可恢复的错误，直接结束，不返回值

### 进程

操作系统给到进程两个关键抽象

- 一个独立的逻辑控制流，给程序一个独占处理器的假象
- 一个私有的地址空间，给程序一个独占存储器系统的假象

用户模式和内核模式，是由一个处理器的特殊控制寄存器的一个方式位提供的

上下文切换 context switch

### 信号

向用户进程通知异常发生的一种机制

- 发送信号，一般是调用系统的部分发送信号的函数或者内核自己检测到一个系统事件
- 接受信号，对应的进程接收到信号，然后做一定的处理，这个处理函数就是handler，这个函数里面的内容就是信号处理

信号处理

- 待处理的信号可被阻塞，即一个在处理的时候，第二个来了需要等待
- 待处理的信号不会排队，所以同样类型的多个信号会被丢弃
- 部分慢速系统调用可能会被信号处理中断，中断后甚至不会恢复，只会直接返回错误条件
  - 解决方法：添加一个函数，使得能在被中断后重新启动该指令，而不是直接返回一个错误

可以显示的阻塞信号以及解除阻塞的信号

- 书中给到的一个例子类似于锁的结构，保证add，后delete

C语言的非本地跳转

- setjmp相当于在这里打一个tag，保存一下环境，longjmp相当于告知跳转，跳转到最近的setjmp出，恢复setjmp处的环境，
- 两个最显著的应用
  - 高级语言的异常的抛出，catch相当于setjmp处， throw相当于longjmp指令
  - 通过结合信号，可以达成信号返回到一个原先指定过的setjmp的位置，而不是回到信号中断时的指令上去

## I/O

#### 文件打开关闭

```c
int open(char *filename, int flag, mode_t mode);
int close(int fd);
```

#### 文件读写

```c
ssize_t read(int fd, void * buf, size_t n);
ssize_t write(int fd, const void *buf, size_t n);
```

#### Rio包

自动处理不足值,同时解决中断的系统调用是自动恢复

- 无缓冲的输入输出

  ```c
  ssize_t rio_readn(int fd, void *ustbuf, size_t n);
  ssize_t rio_writen(int fd, void *usrbuf, size_t n);
  ```

- 带缓冲的输入

  ```c
  void rio_readinitb(rio_t *rp, int fd); //联系一个描述符fd和一个缓冲区地址rp
  
  ssize_t rio_readlineb(rio_t *rp, void *usrbuf, size_t maxlen);//读取文本行
  ssize_t rio_reanb(rio_t *rp, void *usrbuf, size_t n); //既包含文本行也包含二进制的数据文件(如http响应)
  ```

#### 读取文件的其他相关信息

（metadata)(如大小、权限等等)

```c
int stat(const char *filename, struct stat *buf); //根据文件名获取
int fstat(int fd, stat *buf); // 根据文件描述符fd获取
```

#### 共享文件

- 描述符表（每个进程独立拥有）
- 文件表（所有进程共享）
- v-node表（所有进程共享）

#### I/O重定向

```c
int dup2(int oldfd, int newfd);
```

#### 标准I/O库

ANSI C提供了一组高级输入输出函数，称为标准I/O库

- 也是对前面的一些内容的封装
- 对文件描述符和流缓冲区的抽象

## 网络编程

#### IP地址

```c
struct in_addr{
  unsigned int s_addr; //IP地址结构体
};
```

##### 主机字节顺序和网络字节顺序

```c
unsigned long int htonl(unsigned long int hostlong);
unsigned short int htons(unsigned short int hostshort);

unsigned long int ntohl(unsigned long int netlong);
unsigned short int ntohs(unsigned short int netshort);
```

##### 点分十进制和ip地址的转换

```c
int inet_aton(const char * cp, struct in_addr *inp);
char *inet_ntoa(struct in_addr in);
```

##### 获取DNS条目

```c
struct hostent{
  char *h_name;
  char **h_aliases;
  int h_addrtype;
  int h_length;
  char **h_addr_list;
};

struct hostent *gethostbyname(const char *name);
struct hostent *gethostbyaddr(const char *addr, int len, 0)
```

#### 套接字接口

##### 套接字地址结构

```c
struct sockaddr{
  unsigned short sa_family; //协议类型
  char sa_data[14]; // 地址数据内容
}; //作为所有类型的套接字地址结构的抽象，然后把解析的工作直接交给系统去做

struct sockaddr_in{
  unsigned short sin_family;
  unsigned short sin_port; //端口号
  struct in_addr sin_addr; // ip地址
  unsigned char sin_zero[8];
};
```

##### 套接字处理相关的函数

创建套接字描述符

```c
int socket(int domain, int type, int protocol);
```

客户端建立和服务器的连接

```c
int connect(int sockfd, struct sockaddr *serv_addr, int addrlen);
```

connect函数会阻塞，一直到连接成功建立或者发生错误

对其进行一系列封装，包含dns查询和建立连接的open_clientfd

```c
int open_clientfd(char *hostname, int port);
```

服务器中对套接字地址和套接字描述符的绑定

```c
int bind(int sockfd, struct sockaddr *my_addr, int addrlen);
```

描述套接字是监听套接字

```c
int listen(int sockfdm int backlog);
```

对其进行一系列的封装，创建一个监听描述符

```c
int open_listenfd(int port);
```

accept函数，等待客户端的连接请求

```c
int accept(int listenfd, struct sockaddr* addr, int *addrlen);
//很好的展示区别了listenfd和作为返回值的connfd的区别
```

## 并发编程

### 进程的并发

通过新建进程，然后子进程关闭listenfd,父进程不断的监听和覆盖connfd(等效close connfd)，达到多个进程的并行处理。所有通信只能通过IPC

### I/O多路复用

同时响应多个互相独立的I/O事件，那么该如何解决的问题？

```c
int select(int n, fd_set *fdset, NULL, NULL, NULL);//返回已经准备好读的描述符的个数
```

这里注意的就是select函数是会阻塞进程，然后进入内核态，知道有描述符可以读了才返回用户态

后续的处理就是用该描述符集合去判断和处理对应的描述符

#### 基于I/O多路复用的并发事件驱动服务器

这里就是一组状态机，然后根据输入事件转移状态

通俗语言就是一个pool里面同时包含多个I/O（这里面主要是多个connfd和一个listenfd），然后通过select来进入阻塞等待任何一个或者多个I/O的读就绪，然后去一个一个的处理。listenfd有新的，就加新的connfd给pool，然后直接处理pool里面的所有可读状态的connfd

### 线程

包含前面两者的优点

- 同进程一样，由内核自动调度
- 同I/O复用一样，运行在单一进程的上下文，共享进程地址空间

在这里面主线程除了是进程的第一个运行的线程之外，没有任何其他不同的概念

[主线程的退出对子线程的影响](http://originlee.com/2015/04/08/influence-of-main-threads-exiting-to-child-thread/)

​	区别了主线程的主动退出并结束进程和主线程被子线程kill的两种情况的不同结果

#### Posix线程

##### 创建线程

```c
int pthread_create(pthread_t *tid, pthread_attr_t *attr, func *f, void *arg); //创建一个新线程，带有输入变量arg，执行函数为f, attr表示创建线程的一些属性
pthread_t pthread_self(void); //新线程获取自己的线程ID
```

##### 终止线程

一个线程的终止方式

- 线程例程(执行函数func *f)返回时，线程会隐式的终止
- 调用pthread_exit函数显示的终止，但会一个指向返回值的指针
- 任何线程调用Unix的exit，会终止整个进程和与进程相关的线程
- 其他线程通过线程ID来终止当前线程

```c
int pthread_exit(void *thread_return);
int pthread_cancel(pthread_t tid);
```

##### 回收已终止线程资源

```c
int pthread_join(pthread_t tid, void **thread_return);
//这里就可以和前面的pthread_cancel作区别了，前面的cancel是直接终止，不关心最后的返回值，这里就是阻塞等待线程的终止，同时获取到返回值
```

##### 分离线程

```c
int pthread_detach(pthread_t tid);//一个已经分离的线程，是不能被其然的线程回收和杀死。资源也只能由系统默认的释放， 但是对于exit的处理还是得响应并被杀死
```

##### 初始化线程

```c
pthread_once_t once_control = PTHREAD_ONCE_INIT;
int pthread_once(pthread_once_t *once_control, void( *init_routine)(void)); //这里的func作为参数，可以自定义各种初始化的过程
```

##### 基于线程的并发服务器

这里的关键在于需要解决潜在的竞争问题，那么需要对于connfd做malloc和free操作，从而使得每一个connfd都是新建的，从而不存在同一变量的修改

### 多线程的共享变量

首先这里给了一个很好的例子，新建多个线程引用同一个函数，函数有静态变量，那么对于用该函数的多个线程共享这个变量

### 信号量同步线程

Posix信号量

```c
int sem_init(sem_t *sem, 0, unsigned int value); //初始化为value
int sem_wait(sem_t *s); //P
int sem_post(sem_t *s); //S
```

#### 利用信号量完成一个生产者消费者模型

包含一个buf数组，两个指针，以及对应的三个信号量控制缓冲区的同步访问

### 预线程化(线程池？)

由于创建一个新线程的代价是比较大的，那么对于一个服务器来说，如果对于新的请求不断的创建线程和结束线程的开销就会比较大，那么就可以用线程池的方法来解决

同时注意在这里对于每一个线程池里的线程来说，都是主动的去不断的从某一个缓冲区获取任务，而不是说缓冲区来分配这个任务给对应的线程的

同时在基于线程池的环境下，对于服务器支持多个请求的并发也就能很好的做支持了
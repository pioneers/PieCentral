from libc.stdint cimport uint8_t, int64_t
from libc.time cimport time_t
from libcpp cimport bool
from libcpp.string cimport string
from posix.stat cimport mode_t
from posix.types cimport off_t


cpdef enum:
    MAX_PARAMETERS = 16


cdef extern from "<fcntl.h>":
    cpdef enum:
        O_CREAT
        O_EXCL
        O_NOCTTY
        O_TRUNC
        O_APPEND
        O_DSYNC
        O_NONBLOCK
        O_RSYNC
        O_SYNC
        O_ACCMODE
        O_RDONLY
        O_RDWR
        O_WRONLY


cdef extern from "<sys/stat.h>":
    cpdef enum:
        S_IRWXU
        S_IRUSR
        S_IWUSR
        S_IXUSR
        S_IRWXG
        S_IRGRP
        S_IWGRP
        S_IXGRP
        S_IRWXO
        S_IROTH
        S_IWOTH
        S_IXOTH
        S_ISUID
        S_ISGID
        S_ISVTX


cdef extern from "<sys/mman.h>":
    int shm_open(const char *, int, mode_t)
    int shm_unlink(const char *)
    void *mmap(void *, size_t, int, int, int, off_t)
    int munmap(void *, size_t)
    cpdef enum:
        PROT_READ
        PROT_WRITE
        PROT_EXEC
        PROT_NONE
        MAP_SHARED
        MAP_SHARED_VALIDATE
        MAP_PRIVATE
        MAP_32BIT
        MAP_ANONYMOUS
        MAP_DENYWRITE
        MAP_EXECUTABLE
        MAP_FILE
        MAP_FIXED
        MAP_FIXED_NOREPLACE
        MAP_GROWSDOWN
        MAP_HUGETLB
        MAP_LOCKED
        MAP_NONBLOCK
        MAP_NORESERVE
        MAP_POPULATE
        MAP_STACK
        MAP_SYNC


cdef extern from "<pthread.h>" nogil:
    ctypedef struct pthread_mutex_t:
        pass
    ctypedef struct pthread_mutexattr_t:
        pass
    cpdef enum:
        PTHREAD_PROCESS_SHARED
        PTHREAD_MUTEX_RECURSIVE
        PTHREAD_PRIO_INHERIT
    int pthread_mutex_init(pthread_mutex_t *, const pthread_mutexattr_t *)
    int pthread_mutex_destroy(pthread_mutex_t *)
    int pthread_mutex_lock(pthread_mutex_t *)
    int pthread_mutex_unlock(pthread_mutex_t *)
    int pthread_mutexattr_init(pthread_mutexattr_t *)
    int pthread_mutexattr_destroy(pthread_mutexattr_t *)
    int pthread_mutexattr_setpshared(pthread_mutexattr_t *, int)
    int pthread_mutexattr_settype(pthread_mutexattr_t *, int)
    int pthread_mutexattr_setprotocol(pthread_mutexattr_t *, int)


cdef extern from "<time.h>" nogil:
    ctypedef struct timespec:
        time_t tv_sec
        long tv_nsec
    ctypedef struct clockid_t:
        pass
    cpdef enum:
        CLOCK_REALTIME
    int clock_gettime(clockid_t, timespec *)


cdef extern from "_buffer.cpp":
    pass


cdef extern from "_buffer.cpp" namespace "buffer":
    cdef cppclass RingBuffer:
        RingBuffer(size_t) nogil except +
        size_t size() nogil
        uint8_t operator[](size_t) nogil except +
        void clear() nogil except +
        void extend(string) nogil except +
        string read(int64_t) nogil except +


cdef class SharedMemory:
    cdef string name
    cdef Py_ssize_t size
    cdef Py_ssize_t shape[1]
    cdef Py_ssize_t ref_count
    cdef readonly int fd
    cdef uint8_t *buf


cdef struct Lock:
    pthread_mutex_t lock
    pthread_mutexattr_t settings
    Py_ssize_t peers


cdef class SharedLock:
    cdef SharedMemory mem
    cdef Lock *lock

    cpdef void acquire(self) nogil
    cpdef void release(self) nogil


cdef struct ParameterDescriptor:
    size_t value_offset
    size_t value_size
    size_t timestamp_offset


cdef class SensorBuffer:
    cdef SharedMemory buf
    cdef SharedLock access
    cdef size_t num_params
    cdef ParameterDescriptor offsets[MAX_PARAMETERS]

    cdef string get_bytes(self, Py_ssize_t offset, Py_ssize_t count) nogil
    cdef void set_bytes(self, size_t base, size_t count, uint8_t *bytes) nogil
    cdef string get_value(self, Py_ssize_t index) nogil
    cdef void set_value(self, Py_ssize_t, string bytes) nogil
    cdef size_t get_size(self, Py_ssize_t index) nogil

    cdef void acquire(self) nogil
    cdef void release(self) nogil


cdef class SensorReadBuffer(SensorBuffer):
    pass


cdef class SensorWriteBuffer(SensorBuffer):
    cdef size_t dirty_offset

    cpdef void set_dirty(self, Py_ssize_t index) nogil
    cpdef void clear_dirty(self, Py_ssize_t index) nogil
    cpdef bool is_dirty(self, Py_ssize_t index) nogil


cdef class BinaryRingBuffer:
    cdef RingBuffer *buf

    cpdef void extend(self, string buf)
    cpdef string read_with_timeout(self, double timeout)
    cpdef string read(self)
    cpdef void clear(self)
    cdef void _extend(self, string buf) nogil
    cdef string _read_with_timeout(self, double timeout) nogil
    cdef string _read(self) nogil
    cdef void _clear(self) nogil

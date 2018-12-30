# distutils: language = c++

"""
Runtime buffer module.
"""

import ctypes
import os
from libc.errno cimport errno, ENOENT, EPERM
from libc.string cimport strcpy, memcpy
from libc.stdint cimport uint8_t, int64_t
from libcpp.string cimport string
from posix.unistd cimport ftruncate
from libcpp cimport bool

cimport cython
from cython.operator cimport dereference as deref
from cpython cimport Py_buffer
from cpython.buffer cimport PyBUF_ND, PyObject_GetBuffer, PyBuffer_Release
from cpython.mem cimport PyMem_Malloc, PyMem_Free


class SharedMemoryIterator:
    def __init__(self, shm):
        self.index = 0
        self.shm = shm

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.shm):
            byte = self.shm[self.index]
            self.index += 1
            return byte
        raise StopIteration


cdef class SharedMemory:
    _SHM_BASE_PATH = '/dev/shm'
    _NAME_PREFIX = 'runtime-shm'

    def __cinit__(self,
                  str name,
                  Py_ssize_t size,
                  int shm_oflag = O_CREAT | O_RDWR,
                  int shm_mode = S_IRUSR | S_IWUSR,
                  int mmap_prot = PROT_READ | PROT_WRITE,
                  int mmap_flags = MAP_SHARED):
        if size < 0:
            raise ValueError('Size of shared memory must be a nonnegative number of bytes.')
        self.name = (self._NAME_PREFIX + '-' + name).encode()
        self.size = self.shape[1] = size
        self.ref_count = 0

        self.fd = shm_open(self.name.c_str(), shm_oflag, shm_mode)
        if self.fd == -1:
            raise OSError('Failed to open shared memory object.')
        ftruncate(self.fd, self.size)
        self.buf = <uint8_t *> mmap(NULL, size, mmap_prot, mmap_flags, self.fd, 0)

    def __dealloc__(self):
        message = None
        if munmap(self.buf, self.size):
            message = 'Failed to unmap buffer in memory.'

        # Ignore error if another buffer pointing at the same shared memory
        # has already unlinked it. It is fine to open and unlink the same
        # shared memory object multiple times.
        if shm_unlink(self.name.c_str()) and errno != ENOENT:
            message = 'Failed to unlink shared memory object.'

        # Violating this condition means there are serious corruption issues.
        if self.ref_count > 0:
            message = 'One or more memory views are still in use.'

        if message:
            raise OSError(message)

    def bound(self, Py_ssize_t index):
        if 0 <= index < self.size:
            return index
        elif -self.size <= index < 0:
            return index + self.size
        else:
            raise IndexError()

    def __getitem__(self, Py_ssize_t index):
        return self.buf[self.bound(index)]

    def __setitem__(self, Py_ssize_t index, uint8_t byte):
        self.buf[self.bound(index)] = byte

    def __len__(self):
        return self.size

    def __iter__(self):
        return SharedMemoryIterator(self)

    def __reduce__(self):
        suffix = self.name.decode('utf-8')[len(self._SHM_NAME_BASE)+1 :]
        return SharedMemory, (suffix, self.size)

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        if not (flags & PyBUF_ND):
            raise BufferError()
        buffer.buf = <char *> self.buf
        buffer.format = 'c'
        buffer.internal = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.len = buffer.itemsize * self.size
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = NULL
        buffer.suboffsets = NULL
        self.ref_count += 1

    def __releasebuffer__(self, Py_buffer *buffer):
        self.ref_count -= 1


@cython.final
cdef class SharedLock:
    """
    FIXME:
        `SharedLock` should really inherit from `SharedMemory`, but Cython
        inheritance works by calling `__cinit__` on all base classes implicitly.
    """
    def __cinit__(self, str name):
        self.mem = SharedMemory(name, sizeof(Lock))
        self.lock = <Lock *> self.mem.buf
        self.lock.peers += 1  # Small chance of a race condition here.
        cdef pthread_mutexattr_t *settings = <pthread_mutexattr_t *> &self.lock.settings
        if self.lock.peers == 1:
            pthread_mutexattr_init(settings)
            pthread_mutexattr_setpshared(settings, PTHREAD_PROCESS_SHARED)
            pthread_mutexattr_settype(settings, PTHREAD_MUTEX_RECURSIVE)
            pthread_mutex_init(<pthread_mutex_t *> &self.lock.lock, settings)

    def __dealloc__(self):
        self.lock.peers -= 1
        if self.lock.peers == 0:
            pthread_mutex_destroy(<pthread_mutex_t *> &self.lock.lock)
            pthread_mutexattr_destroy(<pthread_mutexattr_t *> &self.lock.settings)

    cpdef void acquire(self) nogil:
        cdef int status = pthread_mutex_lock(<pthread_mutex_t *> &self.lock.lock)
        if status != 0:
            raise OSError(f'Unable to acquire lock (status: {status}).')

    cpdef void release(self) nogil:
        cdef int status = pthread_mutex_unlock(<pthread_mutex_t *> &self.lock.lock)
        if status != 0 and status != EPERM:
            raise OSError(f'Unable to release lock (status: {status}).')

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.release()
        return self


cdef class SensorBuffer:
    def __cinit__(self, str name, sensor_struct):
        self.buf = SharedMemory(name, ctypes.sizeof(sensor_struct))
        self.access = SharedLock(name + '-lock')
        self.num_params = len(sensor_struct._params)
        for i, param in enumerate(sensor_struct._params_by_id):
            self.offsets[i].value_offset = getattr(sensor_struct, param.name).offset
            self.offsets[i].value_size = ctypes.sizeof(param.type)
            timestamp_name = sensor_struct._get_timestamp_name(param.name)
            self.offsets[i].timestamp_offset = getattr(sensor_struct, timestamp_name).offset

    cdef string get_bytes(self, Py_ssize_t offset, Py_ssize_t count) nogil:
        cdef string buf
        self.access.acquire()
        buf.insert(0, <const char *> (self.buf.buf + offset), count)
        self.access.release()
        return buf

    cdef void set_bytes(self, size_t base, size_t count, uint8_t *data) nogil:
        self.access.acquire()
        memcpy(<void *> (self.buf.buf + base), <void *> data, count)
        self.access.release()

    cdef string get_value(self, Py_ssize_t index) nogil:
        self.access.acquire()
        cdef string value
        value = self.get_bytes(self.offsets[index].value_offset,
                               self.offsets[index].value_size)
        self.access.release()
        return value

    cdef void set_value(self, Py_ssize_t index, string bytes) nogil:
        cdef timespec now
        cdef int status
        cdef double timestamp
        self.access.acquire()
        self.set_bytes(self.offsets[index].value_offset,
                       self.offsets[index].value_size, <uint8_t *> bytes.c_str())

        # TODO: verify this timestamp agrees with `time.time`
        status = clock_gettime(<clockid_t> CLOCK_REALTIME, <timespec *> &now)
        if status == 0:
            timestamp = (<double> now.tv_sec) + (<double> now.tv_nsec)/10e8
            self.set_bytes(self.offsets[index].timestamp_offset,
                           sizeof(double), <uint8_t *> &timestamp)
        self.access.release()

    cdef size_t get_size(self, Py_ssize_t index) nogil:
        return self.offsets[index].value_size

    cdef void acquire(self) nogil:
        self.access.acquire()

    cdef void release(self) nogil:
        self.access.release()

    def __len__(self):
        return len(self.buf)

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        PyObject_GetBuffer(self.buf, buffer, flags)

    def __releasebuffer__(self, Py_buffer *buffer):
        PyBuffer_Release(buffer)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.release()
        return self


@cython.final
cdef class SensorReadBuffer(SensorBuffer):
    pass


@cython.final
cdef class SensorWriteBuffer(SensorBuffer):
    def __cinit__(self, str name, sensor_struct):
        self.dirty_offset = sensor_struct.dirty.offset

    cpdef void set_value(self, Py_ssize_t index, string bytes) nogil:
        self.access.acquire()
        SensorBuffer.set_value(self, index, bytes)
        self.set_dirty(index)
        self.access.release()

    cpdef void set_dirty(self, Py_ssize_t index) nogil:
        self.access.acquire()
        self.buf.buf[self.dirty_offset] = self.buf.buf[self.dirty_offset] | (1 << index)
        self.access.release()

    cpdef void clear_dirty(self, Py_ssize_t index) nogil:
        self.access.acquire()
        self.buf.buf[self.dirty_offset] = self.buf.buf[self.dirty_offset] & ~(1 << index)
        self.access.release()

    cpdef bool is_dirty(self, Py_ssize_t index) nogil:
        self.access.acquire()
        cdef bool dirty = (self.buf.buf[self.dirty_offset] >> index) & 1
        self.access.release()
        return dirty


@cython.final
cdef class BinaryRingBuffer:
    DEFAULT_CAPACITY = 16 * 1024

    def __cinit__(self, size_t capacity = DEFAULT_CAPACITY):
        self.buf = new RingBuffer(capacity)

    def __dealloc__(self):
        del self.buf

    def __len__(self):
        return self.buf.size()

    def __getitem__(self, index):
        return deref(self.buf)[index]

    cpdef void extend(self, string buf):
        with nogil:
            self._extend(buf)

    cpdef string read_with_timeout(self, double timeout):
        with nogil:
            return self._read_with_timeout(timeout)

    cpdef string read(self):
        with nogil:
            return self._read()

    cpdef void clear(self):
        with nogil:
            self._clear()

    cdef void _extend(self, string buf) nogil:
        self.buf.extend(buf)

    cdef string _read_with_timeout(self, double timeout) nogil:
        return self.buf.read(<int64_t>(1e6*timeout))

    cdef string _read(self) nogil:
        return self.buf.read(-1)

    cdef void _clear(self) nogil:
        self.buf.clear()

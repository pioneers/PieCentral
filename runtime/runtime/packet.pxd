from libcpp.string cimport string


cdef extern from "_packet.cpp":
    pass


cdef extern from "_packet.cpp" namespace "packet":
    cpdef string cobs_encode(string) nogil
    cpdef string cobs_decode(string) nogil


cpdef string extract_from_frame(string) nogil

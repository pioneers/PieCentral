#ifndef BUFFER_H
#define BUFFER_H

namespace buffer {
    /**
     *  A fixed-length, synchronized, blocking ring buffer implementation.
     */
    class RingBuffer {
    private:
        size_t capacity, start, end;
        uint8_t *data;
        std::deque<size_t> delimeters;
        std::recursive_mutex lock;
        std::condition_variable_any data_ready;
        inline size_t wrap_index(size_t, size_t);
        size_t size_range(size_t, size_t);
    public:
        RingBuffer(size_t);
        ~RingBuffer();
        size_t size(void);
        uint8_t operator[](size_t);
        void clear(void);
        void extend(std::string);
        std::string read(int64_t);
    };
}

#endif

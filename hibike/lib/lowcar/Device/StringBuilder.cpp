#include "StringBuilder.h"
#include <cstdio>
#include <cstdlib>
#include <cstdarg>

StringBuilder::StringBuilder()
{
	this->buf_len = 0;
	this->buf_cap = this->init_buf_cap;
	this->buf = (char*)malloc(sizeof(char) * (this->buf_cap + 1));
}

void StringBuilder::add(const char *format, ...)
{
	va_list args;
	va_start(args, format);
	int len = snprintf(nullptr, 0, format, args);
	resize_buf(len);
	snprintf(buf + buf_len, len + 1, format, args);
	buf_len += len;
}

void StringBuilder::add_string(const char *str)
{
	int len = snprintf(nullptr, 0, "%s", str);
	resize_buf(len);
	snprintf(buf + buf_len, len + 1, "%s", str);
	buf_len += len;
}

void StringBuilder::add_char(char c)
{
	// first line is technically unnecessary since len = 1, but just making
	// it consistent with other functions
	int len = snprintf(nullptr, 0, "%c", c);
	resize_buf(len);
	snprintf(buf + buf_len, len + 1, "%c", c);
	buf_len += len;
}

void StringBuilder::add_int(int n)
{
	int len = snprintf(nullptr, 0, "%d", n);
	resize_buf(len);
	snprintf(buf + buf_len, len + 1, "%d", n);
	buf_len += len;
}

void StringBuilder::add_double(double f, int precision)
{
	int len = snprintf(nullptr, 0, "%.*f", precision, f);
	resize_buf(len);
	snprintf(buf + buf_len, len + 1, "%.*f", precision, f);
	buf_len += len;
}

void StringBuilder::resize_buf(int num_chars)
{
	if (buf_len + num_chars <= buf_cap)
	{
		return;
	}
	while (buf_len + num_chars > buf_cap)
	{
		buf_cap *= 2;
	}
	buf = (char*)realloc(buf, buf_cap + 1);
}

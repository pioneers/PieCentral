#ifndef STRING_BUILDER_H
#define STRING_BUILDER_H

// Class for building strings with various data types
class StringBuilder
{
public:
	StringBuilder();
	const char* str() { return buf; }
	int len() { return buf_len; }
	void add(const char *format, ...); // printf style format string
	void add_string(const char *str);
	void add_char(char c);
	void add_int(int n);
	void add_double(double f, int precision = 6); // precision is number of digits after decimal point
	void add_float(float f, int precision = 6) { add_double((double)f, precision); }
	void add_newline() { add_char('\n'); }
	void clear() { buf_len = 0; }

private:
	char *buf;
	int buf_len; // number of characters currently written in buf
	int buf_cap; // max number of characters that buf can store (excluding null terminator)
	const int init_buf_cap = 10;

	void resize_buf(int num_chars); // number of additional characters to add to buf
};

#endif

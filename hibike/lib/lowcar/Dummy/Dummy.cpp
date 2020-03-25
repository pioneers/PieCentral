#include "Dummy.h"

typedef enum {
	RUNTIME = 0;
	SHEPHERD = 1;
	DAWN = 2;
	DEVOPS = 3;
	ATLAS = 4;
	INFRA = 5;
	SENS = 6;
	PDB = 7;
	MECH = 8;
	CPR = 9;
	EDU = 10;
	EXEC = 11;
	PIEF = 12;
	FUNTIME = 13;
	SHEEP = 14;
	DUSK = 15;
} param;

Dummy::Dummy () :
{
	this->runtime = 1;
	this->shepherd = 0.1;
	this->dawn = true;
	
	this->devops = 1;
	this->atlas = 0.1;
	this->infra = true;
	
	this->sens = 0;
	this->pdb = -0.1;
	this->mech = false;
	
	this->cpr = 0;
	this->edu = 0.0;
	this->exec = false;
	
	this->pief = 0;
	this->funtime = -0.1;
	this->sheep = false;
	
	this->dusk = 0;
}

//retrieves the appropriate instance variable, this whole function is a big lol 
uint8_t Dummy::device_read (uint8_t param, uint8_t *data_buf, size_t data_buf_len)
{
	float *float_buf;
	bool *bool_buf;
	int *int_buf;
	
	switch (param) {
		
		case RUNTIME:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
		case SHEPHERD:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->shepherd;
			return sizeof(float);
			break;
		case DAWN:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf[0] = this->dawn;
			return sizeof(dawn);
			break;
		
		case DEVOPS:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
		case ATLAS:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->shepherd;
			return sizeof(float);
			break;
		case INFRA:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf[0] = this->dawn;
			return sizeof(dawn);
			break;
			
		case SENS:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
		case PDB:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->shepherd;
			return sizeof(float);
			break;
		case MECH:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf[0] = this->dawn;
			return sizeof(dawn);
			break;
			
		case CPR:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
		case EDU:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->shepherd;
			return sizeof(float);
			break;
		case EXEC:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf[0] = this->dawn;
			return sizeof(dawn);
			break;
			
		case PIEF:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
		case FUNTIME:
			if (data_buf_len < sizeof(float)) {
				return 0;
			}
			float_buf = (float *) data_buf;
			float_buf[0] = this->shepherd;
			return sizeof(float);
			break;
		case SHEEP:
			if (data_buf_len < sizeof(bool)) {
				return 0;
			}
			bool_buf[0] = this->dawn;
			return sizeof(dawn);
			break;
		
		case DUSK:
			if (data_buf_len < sizeof(int)) {
				return 0;
			}
			int_buf = (int *) data_buf;
			int_buf[0] = this->runtime;
			return sizeof(int);
			break;
	}
}

//writes the appropriate instance variable; this whole function is also a big lol
uint8_t Dummy::device_write (uint8_t param, uint8_t *data_buf)
{
	switch (param) {
		
		case RUNTIME:
			this->runtime = ((int *) data_buf)[0];
			return sizeof(int);
			break;
		case SHEPHERD:
			this->shepherd = ((float *) data_buf)[0];
			break;
		case DAWN:
			this->dawn = ((bool *) data_buf)[0];
			break;
		
		case DEVOPS:
			this->devops = ((int *) data_buf)[0];
			return sizeof(int);
			break;
		case ATLAS:
			this->atlas = ((float *) data_buf)[0];
			break;
		case INFRA:
			this->infra = ((bool *) data_buf)[0];
			break;
			
		case SENS:
			this->sens = ((int *) data_buf)[0];
			return sizeof(int);
			break;
		case PDB:
			this->pdb = ((float *) data_buf)[0];
			break;
		case MECH:
			this->mech = ((bool *) data_buf)[0];
			break;
			
		case CPR:
			this->cpr = ((int *) data_buf)[0];
			return sizeof(int);
			break;
		case EDU:
			this->edu = ((float *) data_buf)[0];
			break;
		case EXEC:
			this->exec = ((bool *) data_buf)[0];
			break;
			
		case PIEF:
			this->pief = ((int *) data_buf)[0];
			return sizeof(int);
			break;
		case FUNTIME:
			this->funtime = ((float *) data_buf)[0];
			break;
		case SHEEP:
			this->sheep = ((bool *) data_buf)[0];
			break;
						
		case DUSK:
			this->dusk = ((int *) data_buf)[0];
			return sizeof(int);
			break;	
	}
}

void Dummy::device_enable()
{
	//TODO: maybe put some logging call into here when that gets put in
	//for now, we just pass
	;
}

void Dummy::device_disable()
{
	//TODO: 1maybe put some logging call into here when that gets put in
	//for now, we just pass
	;
}

void Dummy::device_actions()
{
	this->runtime += 2;
	this->shepherd += 1.9;
	this->dawn = !this->dawn;
	
	this->devops++;
	this->atlas += 0.9;
	this->infra = true;
	
	this->sens++;
	this->pdb += 0.4;
	this->mech = !mech;
	
	this->cpr -= 1;
	this->edu -= 0.7;
	this->exec = false;
	
	this->pief -= 2;
	this->funtime -= 1.7;
	this->sheep = !sheep;
	
	this->dusk = 0;
}
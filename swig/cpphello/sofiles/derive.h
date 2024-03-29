#ifndef __DERIVE_H_8668D0FE443A0FFB609BCA79C150618C__
#define __DERIVE_H_8668D0FE443A0FFB609BCA79C150618C__


#include "base.h"

class DLL_INTERFACE Derive : public Base {
public:
	Derive();
	virtual ~Derive();
	virtual void hello(char* name);
};


#endif /* __DERIVE_H_8668D0FE443A0FFB609BCA79C150618C__ */

#ifndef __BASE_H_BB6B074E61D5FBB26BAD655BBC36D9F3__
#define __BASE_H_BB6B074E61D5FBB26BAD655BBC36D9F3__


#ifdef BUILDING_DLL
//#define DLL_INTERFACE __declspec(dllexport)
#define DLL_INTERFACE
#else
//#define DLL_INTERFACE __declspec(dllimport)
#define DLL_INTERFACE
#endif


class DLL_INTERFACE Base {
public:
	Base();
	virtual ~Base();
	virtual void hello(char* name);
};



#endif /* __BASE_H_BB6B074E61D5FBB26BAD655BBC36D9F3__ */

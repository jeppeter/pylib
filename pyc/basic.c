#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct CompoundEx CompoundEx;
typedef struct Node Node;

#define ARRAY_1_SIZE   32
#define ARRAY_2_SIZE   1
#define ARRAY_3_SIZE   50

struct Node {
	Node* m_node[ARRAY_1_SIZE][ARRAY_2_SIZE][ARRAY_3_SIZE];
	CompoundEx* m_parent[ARRAY_1_SIZE][ARRAY_2_SIZE][ARRAY_3_SIZE];
};


typedef void (*FuncImpl)(CompoundEx* args);
typedef void (FuncImplHandler)(CompoundEx* args);
typedef uint64_t addr64_t;
typedef _Bool bool;
typedef unsigned char hwaddr[6];

struct CompoundEx {
	CompoundEx* m_cmparr[ARRAY_1_SIZE][ARRAY_2_SIZE][ARRAY_3_SIZE];
	Node* m_carr[ARRAY_1_SIZE][ARRAY_2_SIZE][ARRAY_3_SIZE];
	uint32_t m_array[ARRAY_1_SIZE][ARRAY_2_SIZE][ARRAY_3_SIZE];
	FuncImpl m_func;
	void (*m_func2)(CompoundEx* args);
	char m_name3[32];
	uint32_t m_32bit;
	char* m_name;
	FuncImplHandler* m_func3;
	uint8_t* dsdt_code;
	uint32_t dsdt_size;
	int* m_intarr[ARRAY_1_SIZE * ARRAY_2_SIZE * ARRAY_3_SIZE];
	int* m_intarr2[ARRAY_2_SIZE * sizeof(Node)][ARRAY_3_SIZE*(ARRAY_1_SIZE+sizeof(int))];

};

int main(int argc,char* argv[])
{
	int i,j,k,l;
	char memname[256];
	CompoundEx* pex=NULL;
	pex = malloc(sizeof(*pex));
	memset(pex,0,sizeof(*pex));

#if 0
	l = 0;
	for (i=0;i<ARRAY_1_SIZE;i++) {
		for (j = 0;j<ARRAY_2_SIZE;j++) {
			for (k = 0;k<ARRAY_3_SIZE;k++) {
				pex->m_array[i][j][k] = l;
				l ++;
			}
		}
	}

	printf("pex %p\n",pex);
	for (i=0;i<ARRAY_1_SIZE;i++) {
		for (j = 0;j<ARRAY_2_SIZE;j++) {
			for (k = 0;k<ARRAY_3_SIZE;k++) {
				snprintf(memname,sizeof(memname),"m_array[%d][%d][%d]",i,j,k);
				printf("%s %d (%p)\n",memname,pex->m_array[i][j][k],&(pex->m_array[i][j][k]));
			}
		}
	}
#endif
	free(pex);
	return 0;
}
// crc32.cpp : 콘솔 응용 프로그램에 대한 진입점을 정의합니다.
//

#include "stdafx.h"


typedef unsigned int u32;

// definition for CRC32
#define POLYNOMIAL	0x04c11db7L
static u32 crc_table[256];

void gen_crc_table()
{
	register u32 i, j;
	register u32 crc_accum;

	for(i=0; i<256; i++)
	{
		crc_accum = ((u32) i << 24);
		for(j=0; j<8; j++)
		{
			if(crc_accum & 0x80000000L)
				crc_accum = (crc_accum << 1) ^ POLYNOMIAL;
			else
				crc_accum = (crc_accum << 1);
		}
		crc_table[i] = crc_accum;

		//printf("%03d=%lx, ", i, crc_accum);
		//if(i%7 == 0)
			//printf("\n");
	}
	return;

}



/* update the CRC on the data block one byte at a time */
u32 update_crc(u32 crc_accum, char *data_blk_ptr,int data_blk_size)
{
	register int i, j;

	for(j=0; j<data_blk_size; j++)
	{
		i = ((int)(crc_accum >> 24) ^ *data_blk_ptr++) & 0xff;
		crc_accum = (crc_accum << 8) ^ crc_table[i];
	}
	return crc_accum;
}

#define	MAXGENNO	1000
#define BULKSIZE32	65536	// 32MB
#define BULKSIZE16	32768	// 16MB
#define BULKSIZE8	16384	// 8MB
#define BULKSIZE4	8192	// 4MB


int _tmain(int argc, _TCHAR* argv[])
{
	u32 uarr[128] ; 
	u32	addr ;
	u32 remainder ; 
	u32 bulksize = BULKSIZE4 ; 

	gen_crc_table();
	

	for(int bulkcount = 0 ; bulkcount < MAXGENNO ; bulkcount++ )
	{
		remainder = 0 ; 
		for( int blockcount = 0 ; blockcount <  bulksize ; blockcount++)
		{
			addr =  bulkcount * bulksize + blockcount ;
			for(int i = 0 ; i < 128 ; i ++)
				uarr[i] = addr ;

			remainder = update_crc(remainder, (char*)uarr, 512 ) ;
		}

		printf("%d,%u\n",bulkcount*bulksize, remainder ) ;
	}
	return 0;
}


#include <stdio.h>
#include "base64.c"

#define MAX 512
int main(void) {
    unsigned char example[MAX];
    FILE *fp = fopen("log.txt", "rb");
    //fgets(example, MAX, file);
    do
    {
        // Taking input single character at a time
        char c = fgetc(fp);
 
        // Checking for end of file
        if (feof(fp))
            break ;
 
        printf("%c", c);
    }  while(1);


	//unsigned char* example = "8        wwwgooglecom   ";
    //scanf("%s", example);
    //scanf("%[^\n]",example);
    
    char* encoded_example = base64_encode(example);
    printf("%s\n",encoded_example);

	return 0;
}

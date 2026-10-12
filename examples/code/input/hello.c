#include <stdio.h>
#include <string.h>

/* count how many times each letter appears in the text given on the command line */

int main(int argc, char **argv)
{
    int counts[256];
    int i, j;
    if (argc < 2) {
        printf("usage: hello TEXT\n");
        return 1;
    }
    memset(counts, 0, sizeof(counts));
    for (i = 1; i < argc; i++)
        for (j = 0; j < (int) strlen(argv[i]); j++)
            counts[(unsigned char) argv[i][j]]++;
    for (i = 0; i < 256; i++)
        if (counts[i])
            printf("%c %d\n", i, counts[i]);
    return 0;
}

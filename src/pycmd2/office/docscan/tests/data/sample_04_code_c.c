#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *file; // 定义文件指针
    char filename[] = "example.txt"; // 要读取的文件名
    char buffer[1024]; // 缓冲区，用于存储读取的数据
    size_t result; // 存储每次读取的字节数

    // 尝试打开文件
    file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        return EXIT_FAILURE;
    }

    // 读取文件内容到缓冲区
    while ((result = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        // 打印缓冲区的内容
        fwrite(buffer, 1, result, stdout);
    }

    // 关闭文件
    fclose(file);

    return EXIT_SUCCESS;
}
#include <iostream>
#include <string>
#include <arvcamera.h>
#include "alex.h"

int main() 
{
    std::cout << "Hello, ";
    std::string name = getName();
    std::cout << name << "\n";
    
    ArvCamera* cam;
    cam = arv_camera_new(NULL);
    
    return 0;
}

/*
 * main.c
 * Example for elink
 *  
 * Copyright (c) 2018 Seeed Technology Co., Ltd.
 * Website    : www.seeed.cc
 * Author     : downey
 * Create Time: dec 2018
 * Change Log :
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdlib.h>     //exit()
#include <signal.h>     //signal()
#include <time.h>
#include "GUI_Paint.h"
#include "GUI_BMPfile.h"
#include "EPD_2in7b.h"

UBYTE *BlackImage, *RedImage;


int EPD_DC_PIN = 6;
int EPD_CS_PIN = 5;

//changing pins for diffrent displays
void setPinsAccToElinkId(int eLinkId)
{
    if (eLinkId == 1)
    {
        printf("here1 ");
        EPD_DC_PIN = 6;
        EPD_CS_PIN = 5;
    }

    if (eLinkId == 2)
    {
        printf("here2");
        EPD_DC_PIN = 6;
        EPD_CS_PIN = 5;
    }

}

void  Handler(int signo)
{
    printf("\r\nHandler:Goto Sleep mode\r\n");
    EPD_Sleep();
    DEV_ModuleExit();

    free(BlackImage);
    BlackImage = NULL;
    free(RedImage);
    RedImage = NULL;
    exit(0);
}

void start(){
//static int current_pic_num = 0;
    printf("2.7inch e-Paper B(C) demo\r\n");
    DEV_ModuleInit(); //sth

    // Exception handling:ctrl + c
    signal(SIGINT, Handler);
    
    if(EPD_Init() != 0) {
        printf("e-Paper init failed\r\n");
    }
    EPD_Clear();
    DEV_Delay_ms(500);
    //Create a new image cache named IMAGE_BW and fill it with white
    UWORD Imagesize = ((EPD_WIDTH % 8 == 0)? (EPD_WIDTH / 8 ): (EPD_WIDTH / 8 + 1)) * EPD_HEIGHT;
    if((BlackImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }
    if((RedImage = (UBYTE *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for red memory...\r\n");
        exit(0);
    }
    Paint_NewImage(BlackImage, EPD_WIDTH, EPD_HEIGHT, 270, WHITE);
    Paint_NewImage(RedImage, EPD_WIDTH, EPD_HEIGHT, 270, WHITE);

}

int main(int argc, char **argv)
{
    int elinkId[] = {1,2};
    
    for(int i = 0; i <sizeof(elinkId)/sizeof(int);i++){
        setPinsAccToElinkId(elinkId[i]);
        start();
        printf("argv[0]: %s argv[1]:%s\n",argv[0], argv[1] );
        // paint an image from the pic folder if image is invalid the old one remains
        Paint_SelectImage(BlackImage);
        Paint_Clear(WHITE);
        GUI_ReadBmp(argv[i+1], 0, 0);
        EPD_Display_Black(BlackImage,BlackImage);
    }


    return 0;
}

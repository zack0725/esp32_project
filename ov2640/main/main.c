#include <esp_log.h>
#include <esp_system.h>
#include <sys/param.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"

#define PWDN_GPIO_NUM 43
#define RESET_GPIO_NUM 44

#define VSYNC_GPIO_NUM 6
#define HREF_GPIO_NUM 7
#define PCLK_GPIO_NUM 13
#define XCLK_GPIO_NUM 15

#define SIOD_GPIO_NUM 4
#define SIOC_GPIO_NUM 5

#define Y9_GPIO_NUM 16
#define Y8_GPIO_NUM 17
#define Y7_GPIO_NUM 18
#define Y6_GPIO_NUM 12
#define Y5_GPIO_NUM 11
#define Y4_GPIO_NUM 10
#define Y3_GPIO_NUM 9
#define Y2_GPIO_NUM 8

char deviceUUID[17];

struct Pic_param_t
{
    char pic_name_p[50];
    char app_sub_topic[50];
};

typedef struct Pic_param_t *pic_param_t;

void app_main()
{

    printf("\n\n---------- Get Systrm Info-------------------------\n");

}
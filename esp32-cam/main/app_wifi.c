/* ESPRESSIF MIT License
 * 
 * Copyright (c) 2018 <ESPRESSIF SYSTEMS (SHANGHAI) PTE LTD>
 * 
 * Permission is hereby granted for use on all ESPRESSIF SYSTEMS products, in which case,
 * it is free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

#include "lwip/err.h"
#include "lwip/sys.h"

#include "mdns.h"
//wifi配置
#define EXAMPLE_ESP_WIFI_SSID      CONFIG_ESP_WIFI_SSID
#define EXAMPLE_ESP_WIFI_PASS      CONFIG_ESP_WIFI_PASSWORD
#define EXAMPLE_ESP_MAXIMUM_RETRY  CONFIG_ESP_MAXIMUM_RETRY
#define EXAMPLE_ESP_WIFI_AP_SSID   CONFIG_ESP_WIFI_AP_SSID
#define EXAMPLE_ESP_WIFI_AP_PASS   CONFIG_ESP_WIFI_AP_PASSWORD
#define EXAMPLE_MAX_STA_CONN       CONFIG_MAX_STA_CONN
#define EXAMPLE_IP_ADDR            CONFIG_SERVER_IP
#define EXAMPLE_ESP_WIFI_AP_CHANNEL CONFIG_ESP_WIFI_AP_CHANNEL
#define EXAMPLE_ESP_WIFI_STA_SSID           CONFIG_ESP_WIFI_SSID
#define EXAMPLE_ESP_WIFI_STA_PASSWD         CONFIG_ESP_WIFI_PASSWORD

/* The event group allows multiple bits for each event, but we only care about two events:
 * - we are connected to the AP with an IP
 * - we failed to connect after the maximum amount of retries */
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT      BIT1

static const char *TAG = "camera wifi";
static const char *TAG_STA = "WiFi Sta";

static int s_retry_num = 0;
/* FreeRTOS event group to signal when we are connected/disconnected */
static EventGroupHandle_t s_wifi_event_group;

static bool s_sta_is_connected = false;
static bool s_ethernet_is_connected = false;
static esp_err_t event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data)
{
    static uint8_t s_con_cnt = 0;
    ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
    switch(event_id) {
    case WIFI_EVENT_AP_STACONNECTED:
        ESP_LOGI(TAG, "Wi-Fi AP got a station connected");
        break;
    case WIFI_EVENT_AP_STADISCONNECTED:
        ESP_LOGI(TAG, "Wi-Fi AP got a station disconnected");
        break;
    case WIFI_EVENT_STA_START:
        esp_wifi_connect();
        break;
    case IP_EVENT_STA_GOT_IP:
        ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        break;
    case WIFI_EVENT_STA_DISCONNECTED:
        {
            if (s_retry_num < EXAMPLE_ESP_MAXIMUM_RETRY) {
                esp_wifi_connect();
                s_retry_num++;
                ESP_LOGI(TAG,"retry to connect to the AP");
            }
            ESP_LOGI(TAG,"connect to the AP fail");
            break;
        }
    default:
        break;
    }
    //系统事件处理程序此方法控制所有活动接口上的服务状态，应用程序需要从系统事件处理程序调用它才能正常运行mDNS服务。
    // mdns_handle_system_event(ctx, event);
    return ESP_OK;
}

#define IP4_ADDR(ipaddr, a, b, c, d) \
        ((ipaddr)->addr = ((uint32_t)(a & 0xff) << 24) |\
                        ((uint32_t)(b & 0xff) << 16) |\
                        ((uint32_t)(c & 0xff) << 8) |\
                        (uint32_t)(d & 0xff))

esp_netif_t *wifi_init_softap()
{
    
    esp_netif_t *esp_netif_ap = esp_netif_create_default_wifi_ap();
    //比较字符串
    if (strcmp(EXAMPLE_IP_ADDR, "192.168.4.1"))
    {
        int a, b, c, d;
        //读取格式化的字符串中的数据
        sscanf(EXAMPLE_IP_ADDR, "%d.%d.%d.%d", &a, &b, &c, &d);
        esp_netif_ip_info_t ip_info;
        //设置由4个字节部分指定的IP地址
        IP4_ADDR(&ip_info.ip, a, b, c, d);
        IP4_ADDR(&ip_info.gw, a, b, c, d);
        IP4_ADDR(&ip_info.netmask, 255, 255, 255, 0);
        ESP_ERROR_CHECK(esp_netif_dhcps_stop(WIFI_IF_AP));
        ESP_ERROR_CHECK(esp_netif_set_ip_info(WIFI_IF_AP, &ip_info));
        ESP_ERROR_CHECK(esp_netif_dhcps_start(WIFI_IF_AP));
    }
    wifi_config_t wifi_config = {
        .ap = {
            .ssid = EXAMPLE_ESP_WIFI_AP_SSID,
            .ssid_len = strlen(EXAMPLE_ESP_WIFI_AP_SSID),
            .password = EXAMPLE_ESP_WIFI_AP_PASS,
            .max_connection = EXAMPLE_MAX_STA_CONN,
            .authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .required = false,
            },
        },
    };
    
    if (strlen(EXAMPLE_ESP_WIFI_AP_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }
    //计算指定字符串的长度，但不包括结束字符（即 null 字符）
    if (strlen(EXAMPLE_ESP_WIFI_AP_CHANNEL)) {
        int channel;
        sscanf(EXAMPLE_ESP_WIFI_AP_CHANNEL, "%d", &channel);
        wifi_config.ap.channel = channel;
    }

    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_AP, &wifi_config));

    ESP_LOGI(TAG, "wifi_init_softap finished.SSID:%s password:%s channel:%s",
             EXAMPLE_ESP_WIFI_AP_SSID, EXAMPLE_ESP_WIFI_AP_PASS,EXAMPLE_ESP_WIFI_AP_CHANNEL);
    return esp_netif_ap;
}

esp_netif_t *wifi_init_sta()
{
    esp_netif_t *esp_netif_sta = esp_netif_create_default_wifi_sta();
    wifi_config_t wifi_config;
    wifi_config_t wifi_sta_config = {
        .sta = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .scan_method = WIFI_ALL_CHANNEL_SCAN,
            .failure_retry_cnt = EXAMPLE_ESP_MAXIMUM_RETRY,
        //  .threshold.authmode = ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD,
            .sae_pwe_h2e = WPA3_SAE_PWE_BOTH,
        },
    };
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config) );

    ESP_LOGI(TAG, "wifi_init_sta finished.");
    ESP_LOGI(TAG, "connect to ap SSID:%s password:%s", EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS);

    return esp_netif_sta;
}

void app_wifi_main()
{
    wifi_mode_t mode = WIFI_MODE_NULL;
    if (strlen(EXAMPLE_ESP_WIFI_AP_SSID) && strlen(EXAMPLE_ESP_WIFI_SSID)) {
        mode = WIFI_MODE_APSTA;
    } else if (strlen(EXAMPLE_ESP_WIFI_AP_SSID)) {
        mode = WIFI_MODE_AP;
    } else if (strlen(EXAMPLE_ESP_WIFI_SSID)) {
        mode = WIFI_MODE_STA;
    }
    if (mode == WIFI_MODE_NULL) {
        ESP_LOGW(TAG,"Neither AP or STA have been configured. WiFi will be off.");
        return;
    }
    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* Initialize event group */
    s_wifi_event_group = xEventGroupCreate();
    //tcpip适配器旧版初始化。它只用于设置esp netif的兼容模式，将启用esp netif的向后兼容。
    ESP_ERROR_CHECK(esp_netif_init());
    //初始化事件循环。该API是旧式事件系统的一部分。新代码应使用esp_event.h中的事件库API创建事件处理程序和任务
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_mode(mode));

    //&是将两个二进制的数逐位相与，结果是相与之后的结果。
    if (mode & WIFI_MODE_AP) {
        esp_netif_t *esp_netif_ap = wifi_init_softap();
        /* Start WiFi */
        ESP_ERROR_CHECK(esp_wifi_start());
         /* Enable napt on the AP netif */
        if (esp_netif_napt_enable(esp_netif_ap) != ESP_OK) {
            ESP_LOGE(TAG, "NAPT not enabled on the netif: %p", esp_netif_ap);
        }
    }

    if (mode & WIFI_MODE_STA) {
        esp_netif_t *esp_netif_sta = wifi_init_sta();
        /* Start WiFi */
        ESP_ERROR_CHECK(esp_wifi_start());
        /* Set sta as the default interface */
        esp_netif_set_default_netif(esp_netif_sta);
    }
    // /*
    //  * Wait until either the connection is established (WIFI_CONNECTED_BIT) or
    //  * connection failed for the maximum number of re-tries (WIFI_FAIL_BIT).
    //  * The bits are set by event_handler() (see above)
    //  */
    // EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
    //                                        WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
    //                                        pdFALSE,
    //                                        pdFALSE,
    //                                        portMAX_DELAY);

    // /* xEventGroupWaitBits() returns the bits before the call returned,
    //  * hence we can test which event actually happened. */
    // if (bits & WIFI_CONNECTED_BIT) {
    //     ESP_LOGI(TAG_STA, "connected to ap SSID:%s password:%s",
    //              EXAMPLE_ESP_WIFI_STA_SSID, EXAMPLE_ESP_WIFI_STA_PASSWD);
    // } else if (bits & WIFI_FAIL_BIT) {
    //     ESP_LOGI(TAG_STA, "Failed to connect to SSID:%s, password:%s",
    //              EXAMPLE_ESP_WIFI_STA_SSID, EXAMPLE_ESP_WIFI_STA_PASSWD);
    // } else {
    //     ESP_LOGE(TAG_STA, "UNEXPECTED EVENT");
    //     return;
    // }

    //设置wifi的省电模式
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
}

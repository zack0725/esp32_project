/*
  * ESPRESSIF MIT License
  *
  * Copyright (c) 2020 <ESPRESSIF SYSTEMS (SHANGHAI) PTE LTD>
  *
  * Permission is hereby granted for use on ESPRESSIF SYSTEMS products only, in which case,
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
  *
  */
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_camera.h"
#include "mdns.h"
#include "app_camera.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "esp_mac.h"

static const char *TAG = "camera mdns";

static const char * service_name = "_esp-cam";
static const char * proto = "_tcp";
static mdns_result_t * found_cams = NULL;
static SemaphoreHandle_t query_lock = NULL;
static char iname[64];
static char hname[64];
static char framesize[4];
static char pixformat[4];
static const char * model = NULL;

//摄像头的mdns查询
static void mdns_query_for_cams()
{
    mdns_result_t * new_cams = NULL;
    //查询服务的mdns
    esp_err_t err = mdns_query_ptr(service_name, proto, 5000, 4,  &new_cams);
    if(err){
        ESP_LOGE(TAG, "MDNS Query Failed: %s", esp_err_to_name(err));
        return;
    }
    //获取信号量，如果信号量无效，则最多等待portMAX_DELAY个系统节拍周期
	xSemaphoreTake(query_lock, portMAX_DELAY);
    if (found_cams != NULL) {
    	mdns_query_results_free(found_cams);
    }
	found_cams = new_cams;
    //完成访问共享资源后，必须释放信号量
	xSemaphoreGive(query_lock);
}

//mdns发现任务
static void mdns_task(void * arg)
{
	for (;;) {
		mdns_query_for_cams();
		//延时55秒
		vTaskDelay((55 * 1000) / portTICK_PERIOD_MS);
	}
    vTaskDelete(NULL);
}

/*
*  公共方法
*/

//mdns查询
const char * app_mdns_query(size_t * out_len)
{
	//构建json
    static char json_response[2048];
    char *p = json_response;
    *p++ = '[';

    //首先添加自己的数据
    esp_netif_ip_info_t ip;
    if (strlen(CONFIG_ESP_WIFI_SSID)) {
    	// esp_netif_get_ip_info(TCPIP_ADAPTER_IF_STA, &ip);
        esp_netif_get_ip_info(ESP_IF_WIFI_STA, &ip);
    } else {
    	esp_netif_get_ip_info(ESP_IF_WIFI_AP, &ip);
    }
    *p++ = '{';
    p += sprintf(p, "\"instance\":\"%s\",", iname);
    p += sprintf(p, "\"host\":\"%s.local\",", hname);
    p += sprintf(p, "\"port\":80,");
    p += sprintf(p, "\"txt\":{");
    p += sprintf(p, "\"pixformat\":\"%s\",", pixformat);
    p += sprintf(p, "\"framesize\":\"%s\",", framesize);
    p += sprintf(p, "\"stream_port\":\"81\",");
    p += sprintf(p, "\"board\":\"%s\",", CAM_BOARD);
    p += sprintf(p, "\"model\":\"%s\"", model);
    *p++ = '}';
    *p++ = ',';
	p += sprintf(p, "\"ip\":\"" IPSTR "\",", IP2STR(&(ip.ip)));
	p += sprintf(p, "\"id\":\"" IPSTR ":80\",", IP2STR(&(ip.ip)));
	p += sprintf(p, "\"service\":\"%s\",", service_name);
	p += sprintf(p, "\"proto\":\"%s\"", proto);
    *p++ = '}';

    //获取信号量
	xSemaphoreTake(query_lock, portMAX_DELAY);
    if (found_cams) {
    	*p++ = ',';
    }
    mdns_result_t * r = found_cams;
    mdns_ip_addr_t * a = NULL;
    int t;
    while(r){
    	*p++ = '{';
        if(r->instance_name){
            p += sprintf(p, "\"instance\":\"%s\",", r->instance_name);
        }
        if(r->hostname){
            p += sprintf(p, "\"host\":\"%s.local\",", r->hostname);
            p += sprintf(p, "\"port\":%u,", r->port);
        }
        if(r->txt_count){
            p += sprintf(p, "\"txt\":{");
            for(t=0; t<r->txt_count; t++){
            	if (t > 0) {
            		*p++ = ',';
            	}
                p += sprintf(p, "\"%s\":\"%s\"", r->txt[t].key, r->txt[t].value?r->txt[t].value:"NULL");
            }
    		*p++ = '}';
    		*p++ = ',';
        }
        a = r->addr;
        while(a){
            if(a->addr.type != ESP_IPADDR_TYPE_V6){
                p += sprintf(p, "\"ip\":\"" IPSTR "\",", IP2STR(&(a->addr.u_addr.ip4)));
            	p += sprintf(p, "\"id\":\"" IPSTR ":%u\",", IP2STR(&(a->addr.u_addr.ip4)), r->port);
                break;
            }
            a = a->next;
        }
        p += sprintf(p, "\"service\":\"%s\",", service_name);
        p += sprintf(p, "\"proto\":\"%s\"", proto);
    	*p++ = '}';
        r = r->next;
        if (r) {
        	*p++ = ',';
        }
    }
    //释放信号量
	xSemaphoreGive(query_lock);
    *p++ = ']';
    *out_len = (uint32_t)p - (uint32_t)json_response;
    *p++ = '\0';
    ESP_LOGI(TAG, "JSON: %uB", *out_len);
    return (const char *)json_response;
}

//mdns更新帧尺寸
void app_mdns_update_framesize(int size)
{
    //sprintf不能检查目标字符串的长度，可能造成众多安全问题,所以都会推荐使用snprintf
    //按照format的格式格式化为字符串，然后再将其拷贝至framesize中。可以方便用于不同进制的转换。
    snprintf(framesize, 4, "%d", size);
    //为服务TXT记录设置/添加TXT项，返回ESP_OK(具体值为0)，ESP_ERR为其他
    if(mdns_service_txt_item_set(service_name, proto, "framesize", (char*)framesize)){
        ESP_LOGE(TAG, "mdns_service_txt_item_set() framesize Failed");
    }
}
void app_mdns_main()
{	
    uint8_t mac[6];

    //创建二值信号量
    //xSemaphoreCreateCounting( 10, 0 );创建计数信号量，最大值为10,计数初始值为0.
    //xSemaphoreCreateMutex();创建互斥信号量
    //SemaphoreHandle_t xSemaphoreCreateRecursiveMutex( void );创建递归互斥量
	query_lock = xSemaphoreCreateBinary();
	if (query_lock == NULL) {
        ESP_LOGE(TAG, "xSemaphoreCreateMutex() Failed");
        return;
	}
    //完成访问共享资源后，必须释放信号量
	xSemaphoreGive(query_lock);

    //获取图像传感器控制结构指针
    sensor_t * s = esp_camera_sensor_get();
    if(s == NULL){
        return;
    }
    switch(s->id.PID){
        case OV2640_PID: model = "OV2640"; break;
        case OV3660_PID: model = "OV3660"; break;
        case OV5640_PID: model = "OV5640"; break;
        case OV7725_PID: model = "OV7725"; break;
        default: model = "UNKNOWN"; break;
    }
    
    if (strlen(CONFIG_ESP_HOST_NAME) > 0) {
        snprintf(iname, 64, "%s", CONFIG_ESP_HOST_NAME);
    } else {
        if (esp_read_mac(mac, ESP_MAC_WIFI_STA) != ESP_OK) {
            ESP_LOGE(TAG, "esp_read_mac() Failed");
            return;
        }
        snprintf(iname, 64, "%s-%s-%02X%02X%02X", CAM_BOARD, model, mac[3], mac[4], mac[5]);
    }

    snprintf(framesize, 4, "%d", s->status.framesize);
    snprintf(pixformat, 4, "%d", s->pixformat);

    char * src = iname, * dst = hname, c;
    while (*src) {
    	c = *src++;
    	if (c >= 'A' && c <= 'Z') {
    		c -= 'A' - 'a';
    	}
    	*dst++ = c;
    }
    *dst++ = '\0';

    //mdns初始化
    if(mdns_init() != ESP_OK){
        ESP_LOGE(TAG, "mdns_init() Failed");
        return;
    }

    //如果要播发服务，请设置mdns服务器所需的主机名
    if(mdns_hostname_set(hname) != ESP_OK){
        ESP_LOGE(TAG, "mdns_hostname_set(\"%s\") Failed", hname);
        return;
    }

    //设置mdns服务器的默认实例名称
    if(mdns_instance_name_set(iname) != ESP_OK){
        ESP_LOGE(TAG, "mdns_instance_name_set(\"%s\") Failed", iname);
        return;
    }

    //mdns服务添加
    if(mdns_service_add(NULL, "_http", "_tcp", 80, NULL, 0) != ESP_OK){
        ESP_LOGE(TAG, "mdns_service_add() HTTP Failed");
        return;
    }


    mdns_txt_item_t camera_txt_data[] = {
        {(char*)"board"         ,(char*)CAM_BOARD}, //开发板
        {(char*)"model"     	,(char*)model},     //摄像头类型
        {(char*)"stream_port"   ,(char*)"81"},      //数据流端口
        {(char*)"framesize"   	,(char*)framesize}, //帧尺寸
        {(char*)"pixformat"   	,(char*)pixformat}  //像素格式
    };

    //摄像头添加到mdns服务
    if(mdns_service_add(NULL, service_name, proto, 80, camera_txt_data, 5)) {
        ESP_LOGE(TAG, "mdns_service_add() ESP-CAM Failed");
        return;
    }

    //创建mdns任务
    xTaskCreate(mdns_task, "mdns-cam", 2048, NULL, 2, NULL);
}
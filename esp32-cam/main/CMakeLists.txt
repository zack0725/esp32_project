set(COMPONENT_SRCS  "main.c" 
                    "app_wifi.c" 
                    "app_camera.c" 
                    "app_httpd.c" 
                    "app_mdns.c")
set(COMPONENT_ADD_INCLUDEDIRS "include")

set(COMPONENT_REQUIRES
    nvs_flash
    esp_http_server
    mdns
    esp_wifi
    )

set(COMPONENT_EMBED_FILES
        "www/index_ov2640.html.gz"
        "www/index_ov5640.html.gz"
        "www/monitor.html.gz")

register_component()

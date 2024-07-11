if(IDF_TARGET STREQUAL "esp32")
  set(COMPONENT_SRCS
    driver/camera.c
    driver/sccb.c
    driver/sensor.c
    driver/xclk.c
    sensors/ov2640.c
    conversions/yuv.c
    conversions/to_jpg.cpp
    conversions/to_bmp.c
    conversions/jpge.cpp
    conversions/esp_jpg_decode.c
    )

  set(COMPONENT_ADD_INCLUDEDIRS
    driver/include
    conversions/include
    )

  set(COMPONENT_PRIV_INCLUDEDIRS
    driver/private_include
    sensors/private_include
    conversions/private_include
    )

  set(COMPONENT_REQUIRES 
    driver 
    esp_timer)
  set(COMPONENT_PRIV_REQUIRES freertos nvs_flash)

  register_component()
endif()
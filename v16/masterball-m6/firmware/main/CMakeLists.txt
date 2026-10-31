file(GLOB PD_FONTS "fonts/*.c")
idf_component_register(
    SRCS "app_main.cpp" "ui.cpp" "board_display.c" "board_io.c" "rtc_pcf85063.c" "ble_gatt.c" "assets.c" ${PD_FONTS}
    INCLUDE_DIRS "." "../../core")
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Wno-unused-parameter -Wno-missing-field-initializers)

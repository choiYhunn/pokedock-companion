# Phase M0 pre-display CMake scaffold only; no LVGL app is linked yet.
idf_component_register(
    SRCS "app_main.cpp" "../../core/study_engine.cpp"
    INCLUDE_DIRS "." "../../core"
    REQUIRES esp_timer
)

# idf_component_register(
#     SRCS "main.c"
                    
#     INCLUDE_DIRS "."

#     REQUIRES driver
#     )
set(COMPONENT_SRCS main.c)
set(COMPONENT_ADD_INCLUDEDIRS .)
register_component()
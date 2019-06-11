
add_clang_executable(qt4to5
  Qt4To5.cpp
)

target_link_libraries(qt4to5 PRIVATE
  clangEdit
  clangTooling
  clangBasic
  clangAST
  clangASTMatchers
)

## NOTE: This Project is no longer supported or maintained by KDAB. The code is kept here for historical reasons and the hopes that it proves useful

### Introduction

This tool ports from Qt 4 to Qt 5.

### Build

To build it:

  git clone http://llvm.org/git/llvm.git
  cd llvm/tools
  svn co http://llvm.org/svn/llvm-project/cfe/trunk clang
  cd clang/tools
  git clone https://github.com/KDAB/Qt4to5 qt4to5
  echo "add_subdirectory(qt4to5)" >> CMakeLists.txt
  cd ../../../ # Back down to the llvm checkout
  mkdir build && cd build
  cmake .. -DCLANG_BUILD_EXAMPLES=True

To run it, edit and run the portqt4to5.py script.


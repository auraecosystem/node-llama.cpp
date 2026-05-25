set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

set(target x86_64-pc-windows-msvc)
set(CMAKE_C_COMPILER_TARGET ${target})
set(CMAKE_CXX_COMPILER_TARGET ${target})

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.programFilesPaths.cmake")
setProgramFilesPaths("x64")

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.llvmUseGnuModeCompilers.cmake")
llvmUseGnuModeCompilers("x64")

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.ensureNinjaPath.cmake")
ensureNinjaPath()

# Preset HOST_CXX_COMPILER to the LLVM clang++ resolved above.
# cmake treats x86_64 (toolchain) != AMD64 (host) and sets CMAKE_CROSSCOMPILING=TRUE,
# causing the cross-compilation branch of llama.cpp's UI cmake to run find_program for
# a host compiler. Without this preset, find_program may pick up MinGW g++ from PATH,
# which produces binaries that fail with 0xc0000139 when CUDA/Vulkan SDK DLLs shadow
# newer MSVC runtime DLLs. Pinning to VS-bundled clang++ avoids the DLL conflict.
if(DEFINED LLVM_ROOT AND NOT "${LLVM_ROOT}" STREQUAL "")
    set(HOST_CXX_COMPILER "${LLVM_ROOT}/bin/clang++.exe" CACHE STRING "Host C++ compiler for cross-compilation helper tools" FORCE)
endif()

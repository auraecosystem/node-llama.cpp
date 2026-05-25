set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR arm64)

set(target arm64-pc-windows-msvc)
set(CMAKE_C_COMPILER_TARGET ${target})
set(CMAKE_CXX_COMPILER_TARGET ${target})

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.programFilesPaths.cmake")
setProgramFilesPaths("arm64")

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.llvmUseGnuModeCompilers.cmake")
llvmUseGnuModeCompilers("arm64")

include("${CMAKE_CURRENT_LIST_DIR}/../cmake/win32.ensureNinjaPath.cmake")
ensureNinjaPath()

set(arch_c_flags "-march=armv8.7-a -fvectorize -ffp-model=fast -fno-finite-math-only")
set(warn_c_flags "-Wno-format -Wno-unused-variable -Wno-unused-function -Wno-gnu-zero-variadic-macro-arguments")

set(CMAKE_C_FLAGS_INIT "${arch_c_flags} ${warn_c_flags}")
set(CMAKE_CXX_FLAGS_INIT "${arch_c_flags} ${warn_c_flags}")

# Preset HOST_CXX_COMPILER to the LLVM clang++ resolved above.
# This prevents find_program in the build from picking up MinGW g++ or other
# compilers from PATH that may produce host tools with DLL compatibility issues
# on CI (e.g., CUDA/Vulkan SDK shadowing runtime DLLs → exit 0xc0000139).
if(DEFINED LLVM_ROOT AND NOT "${LLVM_ROOT}" STREQUAL "")
    set(HOST_CXX_COMPILER "${LLVM_ROOT}/bin/clang++.exe" CACHE STRING "Host C++ compiler for cross-compilation helper tools" FORCE)
endif()

sudo apt update
sudo apt install curl wget xz-utils
 reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" /t REG_DWORD /d "1" /f
export VULKAN_VERSION="$(curl -fsSL https://vulkan.lunarg.com/sdk/latest/linux.txt)"                                                                                      

echo "Downloading Vulkan SDK version ${VULKAN_VERSION}"
curl --progress-bar "https://sdk.lunarg.com/sdk/download/${VULKAN_VERSION}/linux/vulkan_sdk.tar.xz" -o "/opt/vulkan-sdk.tar.xz"

echo "Installing Vulkan SDK to /opt/vulkan-sdk"
rm -rf "/opt/vulkan-sdk" && mkdir -p "/opt/vulkan-sdk"
tar -Jxf "/opt/vulkan-sdk.tar.xz" --strip-components=1 -C "/opt/vulkan-sdk"
rm -f "/opt/vulkan-sdk.tar.xz"

echo "Adding Vulkan SDK environment variables to shell profiles"
([ ! -f "$HOME/.bashrc" ] || grep -qxF "source /opt/vulkan-sdk/setup-env.sh" "$HOME/.bashrc") || (echo "source /opt/vulkan-sdk/setup-env.sh" >> "$HOME/.bashrc")
([ ! -f "$HOME/.zshrc" ] || grep -qxF "source /opt/vulkan-sdk/setup-env.sh" "$HOME/.zshrc") || (echo "source /opt/vulkan-sdk/setup-env.sh" >> "$HOME/.zshrc")
source /opt/vulkan-sdk/setup-env.sh

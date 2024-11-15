#!/bin/bash


# 为 Alist daed 安装某些软件包
sudo apt install libfuse-dev
sudo apt install llvm
sudo apt install libbpf-dev


# 克隆 YLYQ & 移动 patch 目录到  lede 目录
git clone --depth=1 https://github.com/QYKing233/YLYQ.git
mv ./YLYQ/patch ./


# 更改 luci 版本
patch -p1 < ./patch/general-change-luci-18.06.patch


# 添加 lede luci 软件包
./scripts/feeds update -a && ./scripts/feeds install -a


# 添加 luci-app-daed
git clone --depth=1 https://github.com/QiuSimons/luci-app-daed.git ./package/dae
# 调整 luci-app-daed 翻译文件
pushd ./package/dae/luci-app-daed/po
ln -s zh_Hans zh-cn
popd


# 创建 community 目录
mkdir -p package/community


# 把 community 目录置为当前
pushd package/community


# 添加 luci-app-alist
git clone -b lua --depth=1 https://github.com/sbwml/luci-app-alist.git


# 添加 luci-app-passwall
git clone --depth=1 https://github.com/xiaorouji/openwrt-passwall.git
git clone --depth=1 https://github.com/xiaorouji/openwrt-passwall-packages.git


# 添加 luci-app-ssr-plus
git clone --depth=1 https://github.com/fw876/helloworld.git


# 添加 luci-app-argon-config & luci-app-argon 
git clone -b 18.06 --depth=1 https://github.com/jerrykuku/luci-app-argon-config.git
git clone -b 18.06 --depth=1 https://github.com/jerrykuku/luci-theme-argon.git


# 添加 open-app-filter
git clone --depth=1 https://github.com/destan19/OpenAppFilter.git


# 添加 luci-app-filebrowser
git clone -b 18.06 --depth=1 https://github.com/xiaozhuai/luci-app-filebrowser.git


# 添加 luci-app-ddnsgo
git clone --depth=1 https://github.com/sirpdboy/luci-app-ddns-go.git


# 退出 community 目录
popd


# 创建 repo 目录
mkdir -p ./package/repo


# 把 repo 目录置为当前
pushd ./package/repo


# 添加 luci-app-adguardhome
git clone --depth=1 https://github.com/Boos4721/OpenWrt-Packages.git
mv ./OpenWrt-Packages/luci-app-adguardhome ../community


# 添加 OpenClash
git clone --depth=1 https://github.com/vernesong/OpenClash.git
mv ./OpenClash/luci-app-openclash ../community
rm -rf ./*


# 添加 luci-app-syncthing
git clone -b openwrt-18.06 --depth=1 https://github.com/immortalwrt/luci.git
mv ./luci/applications/luci-app-syncthing ../community
rm -rf ./*


# 添加 luci-app-beardropper & luci-app-onliner & luci-app-poweroff
git clone --depth=1 https://github.com/kenzok8/small-package.git
mv ./small-package/luci-app-beardropper ../community
mv ./small-package/luci-app-onliner ../community
mv ./small-package/luci-app-poweroff ../community
mv ./small-package/libcron ../community
rm -rf ./*


# 添加 luci-app-irqbalance 
git clone --depth=1 https://github.com/QiuSimons/OpenWrt-Add.git
mv ./OpenWrt-Add/luci-app-irqbalance ../community
rm -rf ./*


# 添加 Lienol luci-app-socat
git clone --depth=1 https://github.com/Lienol/openwrt-package.git
mv ./openwrt-package/luci-app-socat ../community
rm -rf ./*


# 退出 repo 目录
popd


# 调整 luci-app-irqbalance 翻译文件
pushd ./package/community/luci-app-irqbalance/po
ln -s zh_Hans zh-cn
popd


# 删除LEDE luci-app-socat
rm -rf feeds/luci/applications/luci-app-socat


# 调整 luci-app-filebrowser 到 NAS 菜单
sed -i 's/services/nas/g' ./package/community/luci-app-filebrowser/luasrc/controller/*.lua
sed -i 's/services/nas/g' ./package/community/luci-app-filebrowser/luasrc/view/filebrowser/*.htm
sed -i 's/services/nas/g' ./package/community/luci-app-filebrowser/luasrc/model/cbi/filebrowser/*.lua


# 调整 luci-app-aliyundrive-fuse 到 NAS 菜单
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-fuse/luasrc/controller/*.lua
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-fuse/luasrc/view/aliyundrive-fuse/*.htm
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-fuse/luasrc/model/cbi/aliyundrive-fuse/*.lua


# 调整 luci-app-aliyundrive-webdav到 NAS 菜单
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-webdav/luasrc/controller/*.lua
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-webdav/luasrc/view/aliyundrive-webdav/*.htm
# sed -i 's/services/nas/g' ./feeds/luci/applications/luci-app-aliyundrive-webdav/luasrc/model/cbi/aliyundrive-webdav/*.lua


# 调整 luci-app-v2ray-server 到 VPN 菜单
sed -i 's/services/vpn/g' ./feeds/luci/applications/luci-app-v2ray-server/luasrc/controller/*.lua
sed -i 's/services/vpn/g' ./feeds/luci/applications/luci-app-v2ray-server/luasrc/model/cbi/v2ray_server/api/*.lua
sed -i 's/services/vpn/g' ./feeds/luci/applications/luci-app-v2ray-server/luasrc/model/cbi/v2ray_server/*.lua
sed -i 's/services/vpn/g' ./feeds/luci/applications/luci-app-v2ray-server/luasrc/view/v2ray_server/*.htm


# 调整 Nps 内网穿透 服务器地址数据类型为 string
sed -i 's/ipaddr/string/g' ./feeds/luci/applications/luci-app-nps/luasrc/model/cbi/nps.lua
sed -i '/Must an IPv4 address/d' ./feeds/luci/applications/luci-app-nps/luasrc/model/cbi/nps.lua


# 调整 ShadowsocksR Plus+ 的 wireguard 本地地址数据类型为 string
sed -i '857 s/cidr/string/g' ./package/community/helloworld/luci-app-ssr-plus/luasrc/model/cbi/shadowsocksr/client-config.lua
sed -i '882 s/cidr/string/g' ./package/community/helloworld/luci-app-ssr-plus/luasrc/model/cbi/shadowsocksr/client-config.lua


# 调整 Makefile 文件中 include 的路径
sed -i 's/..\/..\/luci.mk/$(TOPDIR)\/feeds\/luci\/luci.mk/g' ./package/community/*/Makefile


# 删除默认 luci-theme-argon & luci-app-argon-config 插件
rm -rf feeds/luci/themes/luci-theme-argon 
rm -rf feeds/luci/applications/luci-app-argon-config


# 调整 luci-theme-argon 的背景图片 
pushd package/community/luci-theme-argon/htdocs/luci-static/argon/img
rm -rf ./bg1.jpg
wget https://raw.githubusercontent.com/QYKing233/YLYQ/main/files/bg1.jpg
popd


# 更换 OpenWRT 官方仓库 gcc
rm -rf ./feeds/packages/devel/gcc
git clone -b openwrt-23.05 --depth=1 https://github.com/openwrt/packages ./gcc
mv ./gcc/devel/gcc ./feeds/packages/devel
rm -rf ./gcc


# 调整主题为黑暗模式
sed -i 's/normal/dark/g' ./package/community/luci-app-argon-config/root/etc/config/argon


# 调整默认 IP 与 Hostname
sed -i 's/192.168.1.1/192.168.5.1/g' package/base-files/files/bin/config_generate
sed -i 's/OpenWrt/YLYQ/g' package/base-files/files/bin/config_generate


# 调整日期样式
sed -i 's/os.date()/os.date("%a %Y-%m-%d %H:%M:%S")/g' package/lean/autocore/files/*/index.htm


# 添加编译日期
date_version=$(date +"%Y-%m-%d")
sed -i "56 s/LEDE/LEDE ($date_version) Build_By : YLYQ/g" ./package/lean/default-settings/files/zzz-default-settings


# 调整默认 shell 为 zsh
sed -i 's/\/bin\/ash/\/usr\/bin\/zsh/g' package/base-files/files/etc/passwd


# 调整 kernel 版本
# sed -i 's/5.15/5.10/g' target/linux/rockchip/Makefile


# 调整 banner
pushd package/base-files/files/etc
rm -rf ./banner
wget https://raw.githubusercontent.com/QYKing233/YLYQ/main/files/banner
popd


# 安装 oh-my-zsh
mkdir -p files/root
pushd files/root
# Clone oh-my-zsh repository
git clone https://github.com/robbyrussell/oh-my-zsh ./.oh-my-zsh
# Install extra plugins
git clone https://github.com/zsh-users/zsh-autosuggestions ./.oh-my-zsh/custom/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ./.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-completions ./.oh-my-zsh/custom/plugins/zsh-completions
wget https://raw.githubusercontent.com/QYKing233/YLYQ/main/files/.zshrc
popd


# 修复 python3 编译失败
patch -p1 < ./patch/general-change-setuptools-scm.patch


# 添加 x86.config
rm -rf ./.config
mv ./YLYQ/x86.config ./
# mv ./YLYQ/dae.config ./
# cat ./dae.config >> ./x86.config
mv ./x86.config ./.config


# 删除 YLYQ
rm -rf ./YLYQ
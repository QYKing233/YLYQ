docker run --detach \
  --name wg-easy \
  --env LANG=chs \
  --env WG_HOST=laotansuancai.top \
  --env PASSWORD_HASH='$2y$10$1CDWm9yvJYxLK0C.Eht5Uu3attSYd88wiVLG/hEGExPfzxsYSxtyS' \
  --env PORT=5844 \
  --env WG_PORT=5833 \
  --env WG_MTU=1420 \
  --env WG_PERSISTENT_KEEPALIVE=25 \
  --env WG_DEFAULT_DNS=192.168.0.2 \
  --volume /opt/wg-easy:/etc/wireguard \
  --publish 5833:51820/udp \
  --publish 5844:51821/tcp \
  --cap-add NET_ADMIN \
  --cap-add SYS_MODULE \
  --restart unless-stopped \
  ghcr.io/wg-easy/wg-easy
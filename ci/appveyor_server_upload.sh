pacman -S --noconfirm git rsync
if [ ! -d "/home/appveyor/.ssh" ]; then
  mkdir "/home/appveyor/.ssh"
fi
echo -e "$1\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
cp "$(dirname "$0")/id_rsa" ~/.ssh/id_rsa
echo "copying from $(cygpath -u "$2"), $3 to root@$1:/web/downloads/$4"
rsync -avh -e --include=$3 "ssh -p 2458" "$(cygpath -u "$2")" root@$1:/web/downloads/$4

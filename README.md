Репозиторий и роли предназначены для использования на Ubuntu 20.04

Подготовка хоста с ansible
```
sudo apt -y install python3-pip python3-venv sshpass
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
```

Установка pxe dhcp
```
ansible-playbook -i inventory playbooks/dhcp.yml
```

Установка foreman server и foreman proxy
```
ansbile-playbook -i inventory playbooks/foreman.yml
python3 sr/run.py
```

Примеры использования api foreman
```
ls -lah sr
```
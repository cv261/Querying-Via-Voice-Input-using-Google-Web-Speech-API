set -xe

clone_repo() {
    echo -n     "Enter Github Username: "
    read username
    echo -n "Enter Github Password: "
    read -s password
    echo 
    cd /home/ec2-user
    git clone https://$username:$password@github.com/Praneethct/DatabaseProject2.git
}


install_docker() {
    sudo yum update -y
    sudo amazon-linux-extras install docker
    sudo service docker start
}


docker rm -f databaseproject2 || echo "container not found"
[ -d "/home/ec2-user/DatabaseProject2" ] || clone_repo
cd /home/ec2-user/DatabaseProject2 && git pull origin
[[ `docker -v` ]] || install_docker
docker build -t databaseflaskapp2 app
docker run --name databaseproject2 -p 80:80 -d databaseflaskapp2

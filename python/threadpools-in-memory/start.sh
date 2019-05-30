docker build -t web-service:latest .

if [[ $1 = background ]]
then
  docker run -d --name web-service-container -p 5000:5000 web-service
else
  docker run -p 5000:5000 web-service
fi

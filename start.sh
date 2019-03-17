docker build -t flask_app .

if [[ $1 = background ]]
then
  docker run -d --name flask_container -p 5000:5000 flask_app
else
  docker run -p 5000:5000 flask_app
fi

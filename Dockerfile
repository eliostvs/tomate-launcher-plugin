FROM eliostvs/tomate

RUN apt-get update -qq && apt-get -yqq install dbus-x11 gir1.2-unity-5.0

WORKDIR /code/

ENTRYPOINT ["make"]

CMD ["test"]

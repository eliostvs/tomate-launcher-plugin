FROM eliostvs/tomate

ENV PROJECT /code/

COPY ./ $PROJECT

RUN apt-get update -qq && apt-get -yqq install dbus-x11 gir1.2-unity-5.0

WORKDIR $PROJECT

ENTRYPOINT ["make"]

CMD ["test"]
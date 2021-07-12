FROM amazoncorretto:11 as builder

COPY . /srv
WORKDIR /srv
RUN ./mvnw package spring-boot:repackage


FROM amazoncorretto:11

COPY --from=builder /srv/target/spring-boot-demo-1.0.0.jar /srv/
EXPOSE 8080

ENTRYPOINT ["java","-jar", "/srv/spring-boot-demo-1.0.0.jar"]

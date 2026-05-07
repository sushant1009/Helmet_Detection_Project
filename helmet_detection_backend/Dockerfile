
FROM eclipse-temurin:17-jdk-jammy AS builder
WORKDIR /app
COPY . .


RUN chmod +x gradlew

RUN ./gradlew build -x test

FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","app.jar"]
>>>>>>> 4e36137e82b7d781730191966632ea034cfd8d7e

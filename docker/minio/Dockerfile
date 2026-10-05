# MinIO Community Edition — build from source (public Docker Hub / Quay images removed Sep 2026).
# Pin: github.com/minio/minio@RELEASE.2025-10-15T17-29-55Z
FROM golang:1.24-alpine AS build
RUN apk add --no-cache git ca-certificates
WORKDIR /src
ENV CGO_ENABLED=0 GOOS=linux
RUN go install -v github.com/minio/minio@RELEASE.2025-10-15T17-29-55Z

FROM alpine:3.20
RUN apk add --no-cache ca-certificates curl
COPY --from=build /go/bin/minio /usr/bin/minio
RUN chmod +x /usr/bin/minio
EXPOSE 9000 9001
VOLUME ["/data"]
ENTRYPOINT ["/usr/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]

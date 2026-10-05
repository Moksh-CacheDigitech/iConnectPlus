# MinIO Client (mc) — build from source (public images removed Sep 2026).
FROM golang:1.24-alpine AS build
RUN apk add --no-cache git ca-certificates
WORKDIR /src
ENV CGO_ENABLED=0 GOOS=linux
RUN go install -v github.com/minio/mc@RELEASE.2025-08-13T08-35-41Z

FROM alpine:3.20
RUN apk add --no-cache ca-certificates curl
COPY --from=build /go/bin/mc /usr/bin/mc
RUN chmod +x /usr/bin/mc
ENTRYPOINT ["/usr/bin/mc"]

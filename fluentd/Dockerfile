FROM fluent/fluentd:v1.12-debian-1

USER root

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
      make gcc

RUN gem install bundler

COPY Gemfile Gemfile

RUN bundle update && bundle install

RUN \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
      make gcc

# USER fluent

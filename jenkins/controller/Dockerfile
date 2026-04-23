FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

USER jenkins
COPY --chown=jenkins:jenkins jenkins/plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

COPY --chown=jenkins:jenkins jenkins/controller/init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/

class: DockerRequirement
#dockerImageId: scidap/bwa:v0.7.12 #not yet ready
dockerPull: scidap/bwa:v0.7.12
dockerFile: |
  #################################################################
  # Dockerfile
  #
  # Software:         bwa
  # Software Version: 0.7.12
  # Description:      SciDAP bwa Image
  # Website:          http://scidap.com/
  # Provides:         bwa
  # Base Image:       scidap/scidap:v0.0.1
  # Build Cmd:        docker build --rm -t scidap/bwa:v0.7.12 .
  # Pull Cmd:         docker pull scidap/bwa:v0.7.12
  # Run Cmd:          docker run --rm scidap/bwa:0.7.12 bwa
  #################################################################


  ### Base Image
  FROM scidap/scidap:v0.0.1
  MAINTAINER Andrey V Kartashov "porter@porter.st"
  ENV DEBIAN_FRONTEND noninteractive

  ################## BEGIN INSTALLATION ######################

  WORKDIR /tmp

  ### Install bwa

  ENV VERSION 0.7.12
  ENV NAME bwa
  ENV URL "https://github.com/lh3/bwa/archive/${VERSION}.tar.gz"

  RUN wget -q -O - $URL | tar -zxv && \
      cd ${NAME}-${VERSION} && \
      make -j 4 && \
      cd .. && \
      cp ./${NAME}-${VERSION}/${NAME} /usr/local/bin/ && \
      strip /usr/local/bin/${NAME}; true && \
      rm -rf ./${NAME}-${VERSION}/

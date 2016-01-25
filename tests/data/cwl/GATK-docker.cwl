class: DockerRequirement
dockerPull: scidap/gatk:v3.5
#dockerImageId: scidap/gatk:v3.5 #not yet ready
dockerFile: |
  #################################################################
  # Dockerfile
  #
  # Software:         GATK
  # Software Version: 3.5
  # Description:      GATK image for SciDAP
  # Website:          http://scidap.com/
  # Provides:         GATK|bwa|picard

  # Base Image:       scidap/scidap:v0.0.1
  # Build Cmd:        docker build --rm -t scidap/gatk:v3.5 .
  # Pull Cmd:         docker pull scidap/gatk:v3.5
  # Run Cmd:          docker run --rm scidap/gatk:v3.5 GenomeAnalysisTK
  #################################################################

  ### Base Image
  FROM scidap/scidap:v0.0.1
  MAINTAINER Andrey V Kartashov "porter@porter.st"
  ENV DEBIAN_FRONTEND noninteractive

  ################## BEGIN INSTALLATION ######################

  WORKDIR /tmp

  ### Install required packages (samtools)

  RUN apt-get clean all &&\
      apt-get update &&\
      apt-get install -y --no-install-recommends \
          libncurses5-dev \
          bzip2 \
          zlib1g-dev \
          libncursesw5-dev \
          openjdk-7-jdk \
          maven && \
      apt-get clean && \
      apt-get purge && \
      rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*


  ### Installing BWA

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


  ### Installing samtools/htslib/tabix/bgzip

  ENV VERSIONH 1.2.1
  ENV NAMEH htslib
  ENV URLH "https://github.com/samtools/htslib/archive/${VERSIONH}.tar.gz"

  ENV VERSION "1.2"
  ENV NAME "samtools"
  ENV URL "https://github.com/samtools/samtools/archive/${VERSION}.tar.gz"

  RUN wget -q -O - $URLH | tar -zxv && \
      cd ${NAMEH}-${VERSIONH} && \
      make -j 4 && \
      cd .. && \
      cp ./${NAMEH}-${VERSIONH}/tabix /usr/local/bin/ && \
      cp ./${NAMEH}-${VERSIONH}/bgzip /usr/local/bin/ && \
      cp ./${NAMEH}-${VERSIONH}/htsfile /usr/local/bin/ && \
      strip /usr/local/bin/tabix; true && \
      strip /usr/local/bin/bgzip; true && \
      strip /usr/local/bin/htsfile; true && \
      ln -s ./${NAMEH}-${VERSIONH}/ ./${NAMEH} && \
      wget -q -O - $URL | tar -zxv && \
      cd ${NAME}-${VERSION} && \
      make -j 4 && \
      cd .. && \
      cp ./${NAME}-${VERSION}/${NAME} /usr/local/bin/ && \
      strip /usr/local/bin/${NAME}; true && \
      rm -rf ./${NAMEH}-${VERSIONH}/ && \
      rm -rf ./${NAME}-${VERSION}/



  ### INSTALL PICARD

  ENV VERSION "1.141"
  ENV NAME "picard-tools"
  ENV ZIP ${NAME}-${VERSION}.zip
  ENV URL https://github.com/broadinstitute/picard/releases/download/${VERSION}/${ZIP}

  RUN wget -q $URL -O ${ZIP} && \
      unzip $ZIP && \
      rm $ZIP && \
      cd ${NAME}-${VERSION} && \
      mv * /usr/local/bin && \
      cd .. && \
      bash -c 'echo -e "#!/bin/bash\njava -jar /usr/local/bin/picard.jar \$@" > /usr/local/bin/picard' && \
      chmod +x /usr/local/bin/picard && \
      rm -rf ${NAME}-${VERSION}


  ### INSTALL GATK

  ENV VERSION "3.5"
  ENV NAME "gatk-protected"
  ENV URL https://github.com/broadgsa/gatk-protected/archive/${VERSION}.tar.gz

  ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64/
  ENV PATH /usr/lib/jvm/java-7-openjdk-amd64/bin:/usr/local/bin:$PATH

  RUN wget -q -O - $URL | tar -zxv --strip-components=1 && \
      grep -v "oracle.jrockit.jfr.StringConstantPool" /tmp/public/gatk-tools-public/src/main/java/org/broadinstitute/gatk/tools/walkers/varianteval/VariantEval.java >/tmp/public/gatk-tools-public/src/main/java/org/broadinstitute/gatk/tools/walkers/varianteval/VariantEval.1.java && \
      mv -f /tmp/public/gatk-tools-public/src/main/java/org/broadinstitute/gatk/tools/walkers/varianteval/VariantEval.1.java /tmp/public/gatk-tools-public/src/main/java/org/broadinstitute/gatk/tools/walkers/varianteval/VariantEval.java && \
      mvn verify -Ddisable.shadepackage '-P!queue' && \
      cd ./target/executable/ && \
      cp -r ./ /usr/local/bin/ && \
      cd /tmp && \
      rm -rf ./* && \
      bash -c 'echo -e "#!/bin/bash\njava -jar /usr/local/bin/GenomeAnalysisTK.jar  \$@" > /usr/local/bin/GenomeAnalysisTK' && \
      chmod +x /usr/local/bin/GenomeAnalysisTK



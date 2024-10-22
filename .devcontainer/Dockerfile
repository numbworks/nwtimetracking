FROM python:3.12.5-bookworm

RUN pip install numpy==1.26.3
RUN pip install pyarrow==15.0.0
RUN pip install openpyxl==3.1.0
RUN pip install pandas==2.2.0
RUN pip install requests==2.31.0
RUN pip install coverage==7.6.1
RUN pip install parameterized==0.9.0
RUN pip install 'git+https://github.com/numbworks/nwshared.git@v1.4.0#egg=nwshared&subdirectory=src'
RUN pip install ipykernel==6.29.5
RUN pip install jupyter==1.0.0
RUN pip install tabulate==0.9.0
RUN pip install 'git+https://github.com/numbworks/nwpackageversions.git@v1.0.0#egg=nwpackageversions&subdirectory=src'

RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \
    && dpkg -i pandoc-3.4-1-amd64.deb \
    && rm -f pandoc-3.4-1-amd64.deb
FROM python:3.12.5-bullseye

RUN pip install --upgrade pip \
    && pip install numpy==1.26.3 \
    && pip install pyarrow==15.0.0 \ 
    && pip install openpyxl==3.1.0 \ 
    && pip install pandas==2.2.0 \ 
    && pip install requests==2.31.0 \ 
    && pip install coverage==7.2.3 \ 
    && pip install parameterized==0.9.0 \ 
    && pip install -e 'git+https://github.com/numbworks/nwshared.git#egg=nwshared&subdirectory=src' \ 
    && pip install ipykernel==6.29.5 \ 
    && pip install jupyter==1.0.0
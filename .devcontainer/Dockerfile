FROM python:3.12.5-bookworm

# MODULE DEPENDENCIES
RUN pip install numpy==2.1.2
RUN pip install pyarrow==17.0.0
RUN pip install openpyxl==3.1.5
RUN pip install pandas==2.2.3
RUN pip install requests==2.32.3
RUN pip install tabulate==0.9.0
RUN pip install 'git+https://github.com/numbworks/nwshared.git@v1.8.1#egg=nwshared&subdirectory=src'
RUN pip install matplotlib==3.9.2

# JUPYTER NOTEBOOK
RUN pip install ipykernel==6.29.5
RUN pip install jupyter==1.1.0
RUN pip install 'git+https://github.com/numbworks/nwpackageversions.git@v1.8.1#egg=nwpackageversions&subdirectory=src'

# UNIT TESTING
RUN pip install coverage==7.6.4
RUN pip install parameterized==0.9.0
RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \
    && dpkg -i pandoc-3.4-1-amd64.deb \
    && rm -f pandoc-3.4-1-amd64.deb

# MAKEFILE
RUN pip install mypy==1.13.0
RUN pip install pandas-stubs==2.2.3.241009
RUN pip install types-openpyxl==3.1.5.20241126
RUN pip install types-requests==2.32.0.20241016
RUN pip install radon==6.0.1

# OTHERS
RUN pip install --upgrade pip==24.3.1
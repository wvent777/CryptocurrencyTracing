ENV APP_HOME/streamlit_app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

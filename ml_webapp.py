import streamlit as st
import pandas as pd
#from pycaret.classification import *
import classification_test as ct
import numpy as np


from datetime import datetime

# from streamlit.server.Server import Server
# import streamlit.ReportThread as ReportThread
import SessionState

import base64
import os
import json
import pickle
import uuid
import re





def read_file(): 
    '''
    Function that helps a user to manually define their own CSV file
    
    Arguments
    =========
    None
    
    Returns
    =======
    df: A Pandas DataFrame

    Comments
    ========

    Creates df: A user-defined DataFrame that renders the CSV file used for the rest of the session
    '''

#File location
    
    st.write("### It's really great that you are curious! :smile: This is where you can add your own files if you download the source code")
    reading_data_choice= st.selectbox("Choose a way to read a file",["By uploading a CSV file","By manually writing the commands"])
   
    if reading_data_choice=="By uploading a CSV file":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df.head())

    if reading_data_choice=="By manually writing the commands":
        
        DATA_FOLDER = st.text_area("Enter Folder path", '')
        DATA_FILE = st.text_input("Enter File path", 'bank-additional-full.csv')
        sepretaion = st.text_input("Enter Seperation", ',')
        # DATA_FILE = 'bank-additional-full.csv'
        df=read_data(DATA_FOLDER,DATA_FILE,sepretaion)
        #df= pd.read_csv(os.path.join(DATA_FOLDER,DATA_FILE), sep=';')
        documentation_substring= f"File {DATA_FILE} successfully read from {DATA_FOLDER}\n"
        
        documentation_string+=documentation_substring+'\n'
    
    return df 

#@st.cache(allow_output_mutation=True)
def read_data(DATA_FOLDER,DATA_FILE,sepretaion):
    df= pd.read_csv(os.path.join(DATA_FOLDER,DATA_FILE), sep=sepretaion)
    return df


def create_model_function(estimator):
    return ct.create_model(estimator)

def ml_analysis():
    
    session_state = SessionState.get(df=None,target_name=None,setup_model=None,comparison_model=None,compare_models_=None,model=None,
                                     model_results=None,model_choice=None,best_model=None)

    session_state.df=pd.DataFrame()
    #target=pd.Series()
    # If you want to add your own dataset 
    files1={'file_name':["bank-additional-full.csv","diabetes data.csv","<Experimental Reading data>"],
            'name':["Bank information","Diabetes information","<Experimental Reading data>"],
            'target':["y","Diabetes","Find your target variable"],
            'description':["This is a relatively cleaned dataset with balanced categorical and numeric values.","This dataset contains numeric-heavy features.",
            "This dataset shows how you could locally add your own data to explore"]   }

    files=pd.DataFrame(files1)
    st.write("")
    st.write("")
    st.write("Continuing from the EDA, the streamlined ML predictions were designed to work best on binary classification datasets")
    st.write("")

    st.write('## Data Input')
    #read_file()
    st.info('NOTE: You can also upload your own CSV data to play around with through the <Experimental Reading Data> option below')
    option = st.selectbox(
        'Choose which type of data',files.name)
    st.write("You have chosen "+option)
    option_index=files.index[files['name']==option]
    # st.write(files.loc[option_index,'file_name'].item())
    option_name=files.loc[option_index,'file_name'].item()
    st.write(files.loc[option_index,'description'].item())
    if (option_name=='<Experimental Reading data>'):
        session_state.df=read_file()
    else: 
        session_state.df= read_data("",option_name,",")

    st.write("### Define the target variable")
    st.write("")
    
    if st.checkbox('Find the target variable'):
        if (files.loc[option_index,'name'].item() == "<Experimental Reading data>") and (files.loc[option_index,'target'].item()=="Find your target variable"):
            st.info("Search for the target variable from your dataset")
            st.write(session_state.df.head())
        else:
            st.write("For this dataset, it is {0}".format(files.loc[option_index,'target'].item()) )
        session_state.target_name = st.text_input("Enter the target name",files.loc[option_index,'target'].item())
        
        st.write("Target: ",session_state.target_name)
    

# df = pd.read_csv("bank-additional-full.csv",sep=",")



    if session_state.setup_model == None:
        session_state.setup_model= ct.setup(session_state.df, target = session_state.target_name,silent=True,sampling=False,html=False)
        
    st.write("")
    st.write("")
    st.write("### Inital model setup")
    st.write("This shows the general preprocessing steps taken before building the model")
    st.table(session_state.setup_model[-1])

    st.write("")
    st.write("### Compare Various Models <Optional>")
    st.write("This evaluates a few models at a high level with a 5 folds Cross Validatation")
    if session_state.comparison_model == None:
        st.write("Here are some of the models that the data will be evaluated on:")
        st.write(ct.models()['Name'])
    if st.checkbox("Comapare models:"):        
        if session_state.comparison_model == None:
            session_state.comparison_model,session_state.compare_models_=ct.compare_models(verbose = False, fold =5)
        st.write("### Table of scores")
        st.table(session_state.compare_models_)
        st.write("### Best model with parameters")
        st.write(session_state.comparison_model)
        #X_test_ ,display_container = ct.predict_model(model)
    
    st.write("")
    st.write("### Choose your specific model")
    st.write("### Depending on the desired metrics, you can choose a model that you see fit")
    if st.checkbox("Create a specific model"):
        model_dict = {  'Choose a value': 'Choose a value',
                        'Logistic Regression' : 'lr',
                    'Linear Discriminant Analysis' : 'lda', 
                    'Ridge Classifier' : 'ridge', 
                    'Extreme Gradient Boosting' : 'xgboost',
                    'Ada Boost Classifier' : 'ada', 
                    'CatBoost Classifier' : 'catboost', 
                    'Light Gradient Boosting Machine' : 'lightgbm', 
                    'Gradient Boosting Classifier' : 'gbc', 
                    'Random Forest Classifier' : 'rf',
                    'Naive Bayes' : 'nb', 
                    'Extra Trees Classifier' : 'et',
                    'Decision Tree Classifier' : 'dt', 
                    'K Neighbors Classifier' : 'knn', 
                    'Quadratic Discriminant Analysis' : 'qda',
                    'SVM - Linear Kernel' : 'svm',
                    'Gaussian Process Classifier' : 'gpc',
                    'MLP Classifier' : 'mlp',
                    'SVM - Radial Kernel' : 'rbfsvm'}

        model_choice= st.selectbox("Choose your model",list(model_dict.keys()))
        st.write("Model Choice:"+ model_choice)
        if model_choice != "Choose a value":
            st.write(model_dict.get(model_choice))
            if session_state.model == None or session_state.model_choice !=model_choice:
                session_state.model,session_state.model_results = create_model_function(model_dict.get(model_choice))
                session_state.model_choice =model_choice
            
            st.table(session_state.model_results)
            st.write(session_state.model)
        
        # st.write("")
        # st.write("### Tune the model")
        # st.write("This can be use to further tune the model hyperparameters")
        # if st.checkbox("Tune the above model"):
            
        #     session_state.model,model_results = ct.tune_model(session_state.model)
        #     st.table(model_results)
        #     st.write(session_state.model)
            ######
    
    st.write("")
    st.write("### Visualize the model metrics")
    st.write("You can get a much more intuitive analysis of the model")
    if st.checkbox("Plot the model metrics"):
        # make a selection for various models
        plot_dict=dict([('Choose a value', 'Choose a value'),
                                        ('Hyperparameters', 'parameter'),
                                        ('AUC', 'auc'), 
                                        ('Confusion Matrix', 'confusion_matrix'), 
                                        ('Threshold', 'threshold'),
                                        ('Precision Recall', 'pr'),
                                        ('Error', 'error'),
                                        ('Class Report', 'class_report'),
                                        ('Feature Selection', 'rfe'),
                                        ('Learning Curve', 'learning'),
                                        ('Manifold Learning', 'manifold'),
                                        ('Calibration Curve', 'calibration'),
                                        ('Validation Curve', 'vc'),
                                        ('Dimensions', 'dimension'),
                                        ('Feature Importance', 'feature'),
                                        ('Decision Boundary', 'boundary')
                                    ])
        plot_options=st.selectbox("Choose your plots type",list(plot_dict.keys()))
        if plot_options!= "Choose a value":
            ct.plot_model(session_state.model,plot=plot_dict.get(plot_options))
            st.pyplot()

         #Tree interpretability   
        # if st.checkbox("Interpret the tree-based model"):
        #     # make a selection for tree-based models
        #     allowed_models = ['RandomForestClassifier',
        #                 'DecisionTreeClassifier',
        #                 'ExtraTreesClassifier',
        #                 'GradientBoostingClassifier',
        #                 'XGBClassifier',
        #                 'LGBMClassifier',
        #                 'CatBoostClassifier']
            
        #     ct.plot_model(model)
        #     st.pyplot()
    st.write("")
    st.write("### Model prediction")
    st.write("This provides with some prediction metrics from some data that was held out for testing")   
    if st.button("Predict Model"):
        X_test_ ,display_container = ct.predict_model(session_state.model)
        #st.write(X_test_)
        st.table(display_container[0])
        st.table(display_container[1])

    st.write("")
    st.write("### Model saving")
    st.write("This saves the preprocessing steps and as well as the model built")
    if st.button("Save Model"):
        # a=ct.save_model(session_state.model, 'lr_model_23122016')
        # st.write(a)
        combined_pickle=[]
        #Getting the model pipeline steps
        combined_pickle.append(session_state.setup_model[7])
        combined_pickle.append(session_state.model)
        
        now = datetime.now()
        current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name="streamlined_ML_"+current_time+'.pkl'
        st.write("The File will be saved as ", file_name)
        st.write("Confirm the download by clicking on the button below")
        st.markdown(download_button(combined_pickle, file_name, 'Pickle the model!',pickle_it=True), unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    if st.button("You're done!! Click here to celebrate"):    
        st.balloons()
    


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.

    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.

    Returns:
    -------
    (str): the anchor tag to download object_to_download

    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')

    """


    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;

            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

# if st.button("Download as pickle 2"):
#     st.markdown(download_button(session_state.model, 'YOUR_MODEL.pkl', 'Click to download data!',pickle_it=True), unsafe_allow_html=True)



# st.write(a)
# lda = create_model('lda')
# tuned_lda = tune_model('lda')
# ensembled_lda = ensemble_model(lda)
# plot_model(tuned_lda)
# evaluate_model(lda)
# lda_predictions_holdout = predict_model(lda)
# final_rf = finalize_model(tuned_lda)

if __name__ == "__main__":
    #st.info('Do look at the menu at the left for the various projects')
    st.write("# Streamlined ML")
    ml_analysis()
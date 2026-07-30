import streamlit as st
import re
import sqlite3 
import pickle
import pandas as pd
import os
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
st.set_page_config(page_title="Crop Recommendation", page_icon="fevicon.png", layout="centered", initial_sidebar_state="auto", menu_items=None)
file_path = "model.pkl"
if not os.path.isfile(file_path):
    data=pd.read_csv("Crop_recommendation.csv")
    data=data.dropna(how='any')
    colums=data.columns
    X=data.loc[:,colums[:7]]
    y=data.loc[:,colums[7]]
    #array Conver
    X=X.to_numpy()
    #spilit data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)   
    names = ["K-Nearest Neighbors", "SVM",
             "Decision Tree", "Random Forest",
             "Naive Bayes","ExtraTreesClassifier","VotingClassifier"]
    classifiers = [
        KNeighborsClassifier(),
        LinearSVC(),
        DecisionTreeClassifier(),
        RandomForestClassifier(),
        GaussianNB(),
        ExtraTreesClassifier(),
        VotingClassifier(estimators=[('DT', DecisionTreeClassifier()), ('rf', RandomForestClassifier()), ('et', ExtraTreesClassifier())], voting='hard')]
    clfF=[]
    for name, clf in zip(names, classifiers):
        clf.fit(X_train, y_train)
        y_pred=clf.predict(X_test)
        print(name)
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred))
        print('--------------------------------------------------------------')
        clfF.append(clf)
    pickle.dump(clfF, open("model.pkl", 'wb'))  


conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(FirstName TEXT,LastName TEXT,Mobile TEXT,City TEXT,Email TEXT,password TEXT,Cpassword TEXT)')
def add_userdata(FirstName,LastName,Mobile,City,Email,password,Cpassword):
    c.execute('INSERT INTO userstable(FirstName,LastName,Mobile,City,Email,password,Cpassword) VALUES (?,?,?,?,?,?,?)',(FirstName,LastName,Mobile,City,Email,password,Cpassword))
    conn.commit()
def login_user(Email,password):
    c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?',(Email,password))
    data = c.fetchall()
    return data
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()
def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
          f"""
          <style>
          .stApp {{https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS22fzVJd5l2JyBKdLCGncMVj04Kynl64_E1-37WAnkvjmjlTYWhkbHnFE&s=10
              background: url("avender_field_at_Hartley_Park_Farm_-_geograph.org.uk_-_1949000.jpg");
              background-size: cover
          }}
          </style>
          """,
          unsafe_allow_html=True
      )
set_bg_hack_url()


menu = ["Home","Login","SignUp"]
choice = st.sidebar.selectbox("Menu",menu)

if choice=="Home":
    st.markdown(
        """
        <h2 style="color:white">Welcome to Crop Recommendation</h2>
        <h1>    </h1>
        <p align="justify">
        <b style="color:white">Indian economy is contributed heavily by agriculture. Most of the Indian farmers rely on their instincts to decide the crop to be sown at a particular time of year. They do not realize that the crop output is circumstantial, and depended heavily on the present-day weather and soil conditions. A single uninformed decision by the farmer can have undesirable consequences on the economic conditions of the region and also mental and financial impacts on the farmer himself. Applying systematic Machine Learning models will effectively help to alleviate this issue. The dataset used in the project is built by adding up the datasets of India's rainfall, climate, and Soil. Machine learning models will be used on the dataset to get the highest accuracy model to recommend a crop for the farm's location. This recommendation will help the farmers in India to make learned decisions about the crops. The recommendation will take into account the parameters like the farm's location, sowing season, soil properties, and climate.</b>
        </p>
        """
        ,unsafe_allow_html=True)
    
if choice=="Login":
    Email = st.sidebar.text_input("Email")
    Password = st.sidebar.text_input("Password",type="password")
    b1=st.sidebar.checkbox("Login")
    if b1:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):
            create_usertable()
            if Email=='a@a.com' and Password=='123':
                st.success("Logged In as {}".format("Admin"))
                Email=st.text_input("Delete Email")
                if st.button('Delete'):
                    delete_user(Email)
                user_result = view_all_users()
                clean_db = pd.DataFrame(user_result,columns=["FirstName","LastName","Mobile","City","Email","password","Cpassword"])
                st.dataframe(clean_db)
            else:
                result = login_user(Email,Password)
                if result:
                    st.success("Logged In as {}".format(Email))
                    menu2 = ["K-Nearest Neighbors", "SVM",
                             "Decision Tree", "Random Forest",
                             "Naive Bayes","ExtraTreesClassifier","VotingClassifier"]
                    choice2 = st.selectbox("Select ML",menu2)

                    N=float(st.slider('N Value', 0.0, 140.0))
                    P=float(st.slider('P Value', 5.0, 145.0))
                    K=float(st.slider('K Value', 5.0, 205.0))
                    temp=float(st.slider('temp Value', 8.0, 44.0))
                    Hum=float(st.slider('Humidity Value', 14.0, 100.0))
                    Ph=float(st.slider('ph Value', 3.5, 10.0))
                    Rain=float(st.slider('rainfall Value', 20.0, 299.0))
                    b2=st.button("Recommand")
                    model=pickle.load("model.pkl", "rb")
                    tdata=[N,P,K,temp,Hum,Ph,Rain]                        
                    if b2:
                        if choice2=="K-Nearest Neighbors":
                            test_prediction = model[0].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                        if choice2=="SVM":
                            test_prediction = model[1].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)                 
                        if choice2=="Decision Tree":
                            test_prediction = model[2].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                        if choice2=="Random Forest":
                            test_prediction = model[3].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                        if choice2=="Naive Bayes":
                            test_prediction = model[4].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                        if choice2=="ExtraTreesClassifier":
                            test_prediction = model[5].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                        if choice2=="VotingClassifier":
                            test_prediction = model[6].predict([tdata])
                            query=test_prediction[0]
                            st.success(query)
                            
                else:
                    st.warning("Incorrect Email/Password")
        else:
            st.warning("Not Valid Email")
                
           
if choice=="SignUp":
    Fname = st.text_input("First Name")
    Lname = st.text_input("Last Name")
    Mname = st.text_input("Mobile Number")
    Email = st.text_input("Email")
    City = st.text_input("City")
    Password = st.text_input("Password",type="password")
    CPassword = st.text_input("Confirm Password",type="password")
    b2=st.button("SignUp")
    if b2:
        pattern=re.compile("(0|91)?[7-9][0-9]{9}")
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if Password==CPassword:
            if (pattern.match(Mname)):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(Fname,Lname,Mname,City,Email,Password,CPassword)
                    st.success("SignUp Success")
                    st.info("Go to Logic Section for Login")
                else:
                    st.warning("Not Valid Email")         
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Pass Does Not Match")
            
        

    

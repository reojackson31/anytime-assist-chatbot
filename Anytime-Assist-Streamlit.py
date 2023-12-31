import re
import pandas as pd
import math
import matplotlib.pyplot as plt
import warnings
import nltk

# Download NLTK resources for SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import datetime
from datetime import date, time, datetime, timedelta

import calendar
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
#pip install streamlit #run in console
import streamlit as st 

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore")
count=0

def increment():
    global count 
    count+=1

def get_user_info():
    st.write("Take the time to discover Anytime Fitness. Access is FREE, and we'd love to show you around our gym!")
    first_name = st.text_input("What's your first name? ",key=count)
    increment()
    last_name = st.text_input("What's your last name? ",key=count)
    increment()
    email = st.text_input("What's your email address? ",key=count)
    increment()
    if email:
        if not validate_email(email):
            st.write("Invalid email format. Please enter a valid email address.")
    phone_number = st.text_input("What's your phone number? ",key=count)
    increment()
    if phone_number:
        if not validate_phone_number(phone_number):
            st.write("Invalid phone number format. Please enter a valid phone number.")
        increment()
    zipcode = st.text_input("What's your zipcode? ",key=count)
    increment()
    if zipcode:
        if not validate_zipcode(zipcode):
            st.write("Invalid zipcode format. Please enter a valid zipcode.")
    return first_name, last_name, email, phone_number, zipcode

def validate_email(email):
    # Very basic email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone_number(phone_number):
    #Phone number validation
    return re.match(r"\d{10}", phone_number)

def validate_zipcode(zipcode):
    return re.match(r"(\d{5})|([a-zA-Z]\d[a-zA-Z]\d[a-zA-Z]\d)", zipcode)

def display_terms_and_conditions():
    text = '''Please select your membership plan from our options: 
    
\n1. Standard Membership:
\nOfferings: Access to gym facilities, including cardio and strength training areas.
\nPrice: $30/month

\n2. Premium Membership:
\nOfferings: Access to gym facilities, group fitness classes, and personalized training sessions.
\nPrice: $50/month

\n3. Platinum Membership:
\nOfferings: All-inclusive access, including premium gym features and spa services.
\nPrice: $80/month'''

    st.write(text)
    membership_type = st.text_input("\nPlease enter your choice (Enter 1/2/3): ",key=count)
    increment()
    if membership_type:
        if membership_type not in ["1","2","3"]:
            st.write("Please select a valid membership plan (1/2/3)")
            return display_terms_and_conditions()
        elif membership_type:
            text = '''\nHere are our terms and conditions:
    \n1. Must be 18 years of age or older. Valid ID required.
    \n2. Valid at participating locations only.
    \n3. Terms and conditions may vary.
    \n4. Each Anytime Fitness is independently owned and operated.
    \n5. By submitting my information, I accept the Terms & Conditions, Privacy Notice, and consent to receive marketing and other communications by email, phone and text from Anytime Fitness Franchisor LLC, its affiliates, franchisees and/or their authorized designees.
    \n6. I can withdraw my consent at any time.
    \n7. Message and data rates apply.
    \n8. Full terms and conditions can be found at: www.anytimefitness.com or your local Anytime Fitness club.'''
            st.write(text)
            
        return membership_type
        
def submit_info(first_name, last_name, email, phone_number, zipcode,membership_type):
    st.write("\nThank you for providing your information, {}!".format(first_name))
    st.write("You're now eligible for a 7-day free trial pass at Anytime Fitness.")
    st.write("We'll send you an email with more information on how to activate your trial pass.")
    st.write("Thank you for choosing AnytimeAssistant and Anytime Fitness!")
    df = pd.read_excel('user_data.xlsx')
    customer_id = 'gym_' + str(len(df) + 1)
    
    new_row = {
    'customerId': customer_id,
    'first_name': first_name,
    'last_name': last_name,
    'email': email,
    'phone': phone_number,
    'zipcode': zipcode,
    'membershipPlan': membership_type,
    'status': 'Active',
    'cancelReason': 'NA',
    'trainer': 'NA'
}

    df = df.append(new_row, ignore_index=True)
    df.to_excel('user_data.xlsx',index=False)
    try:
        email_sender(customer_id, first_name, email, membership_type)
    except:
        pass
    
def existing_user_options(target_id):
    st.write(f'''\n** Existing User Options **
    \nYou're an existing user! Here are some options:
    \n1. Manage Membership
    \n2. Profile Analytics
    \n3. Find your nearest gym
    \n4. Find a personal trainer
    \n5. Recommend Exercise
    \n6. Find best time to go to gym
    \n7. FAQs''')
    
    choice = st.text_input("Please choose an option (1/2/3/4/5/6/7)",key=count)
    increment()
    if choice == "1":
        manage_membership(target_id)
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "2":
        st.write("Here's information about your profile.")
        calculate_macronutrients(target_id)
        analyze_gym_usage(target_id)
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "3":
        input_for_nearest_gym()
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "4":
        input_for_sentiment_analysis(target_id)
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "5":
        suggest_exercises()
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "6":
        gym_occupancy()
        repeat_trigger_existing_user_flow(target_id)
    elif choice == "7":
        query1 = st.text_input("\nEnter your query: ",key=count)
        increment()
        gym_faq(query1)
        repeat_trigger_existing_user_flow(target_id)     
    elif choice:
        st.write("Sorry, we couldn't understand your choice.")
        repeat_trigger_existing_user_flow(target_id)
        
def general_info():
    st.write("\n** Here are some options: **")
    st.write("1. Membership plans")
    st.write("2. Promotions & Offers")
    st.write("3. Find your nearest gym")
    st.write("4. FAQs")
    choice = st.text_input("Please choose an option (1/2/3/4): ",key=count)
    increment()
    
    if choice == "1":
        st.write("Here's information about our membership plans.")
        display_membership_plans()
        repeat_trigger_new_user_flow()
    elif choice == "2":
        st.write("Here's information promotions & Offers.")
        st.write('''\n1. Student Offers - If you are a student, please let us know at the time of enrollment. We have a special offer for you!
\n2. 30 Days Free Membership - If you sign up for a 12-month plan, you can get the first month of your membership free of cost.
\n3. 7 Day Pass/Try Us Free - If you are a new customer with a valid address in your home gym city, you are eligible to have a free 7-day trial at no cost.
\n4. Free Fitness Consultation - Not sure about your fitness plan? Head over to any of our centers for a free fitness consultation with our expert to plan your fitness routine.''')
        repeat_trigger_new_user_flow()
    elif choice == "3":
        input_for_nearest_gym()
        repeat_trigger_new_user_flow()
    elif choice == "4":
        query1 = st.text_input("\nEnter your query: ",key=count)
        increment()
        gym_faq(query1)
        repeat_trigger_new_user_flow()
    elif choice:
        st.write("Sorry, we couldn't understand your choice.")
        repeat_trigger_new_user_flow()

            
def new_user_registration():
    st.write("\n** New User Registration **")
    first_name, last_name, email, phone_number, zipcode = get_user_info()
    if first_name and last_name and  email and phone_number and zipcode:
        membership_type = display_terms_and_conditions()
        if membership_type:
            agreement = st.text_input("\nDo you agree to the terms and conditions? (type 'yes' or 'no') ",key=count)
            increment()
            if agreement:
                membership_type = membership_type.replace("1","Standard").replace("2","Premium").replace("3","Platinum")        
                if agreement.lower() == 'yes':
                    submit_info(first_name, last_name, email, phone_number, zipcode, membership_type)
                    st.write("Registration successful!")
                elif agreement.lower():
                    st.write("We're sorry, you need to agree to the terms and conditions to continue.")
                    increment()
def new_user_options():
    st.write("Welcome, new user! How can we assist you today?")
    st.write("1. Enroll in Anytime Fitness")
    st.write("2. General Information")
    choice = st.text_input("Please choose an option (1/2): ",key=count)
    increment()
    
    if choice == "1":
        new_user_registration()
    elif choice == "2":
        general_info()
    elif choice:
        st.write("Sorry, we couldn't understand your choice.")
        
def display_membership_plans():
    st.write("\n** Membership Plans **")
    st.write("1. Standard Membership: Access to gym facilities.")
    st.write("2. Premium Membership: Access to gym facilities, group classes, and personal training sessions.")
    st.write("3. Platinum Membership: All-inclusive access, including premium features and spa services.")
    choice = st.text_input("Please choose a membership plan (1/2/3): ",key=count)
    increment()
    if choice == "1":
        st.write("Standard Membership:")
        st.write("Access to gym facilities, including cardio and strength training areas.")
        st.write("Price: $30/month")
    elif choice == "2":
        st.write("Premium Membership:")
        st.write("Access to gym facilities, group fitness classes, and personalized training sessions.")
        st.write("Price: $50/month")
    elif choice == "3":
        st.write("Platinum Membership:")
        st.write("All-inclusive access, including premium gym features and spa services.")
        st.write("Price: $80/month")
    elif choice:
        st.write("Sorry, we couldn't understand your choice.")
        
def info_about_other_offers():
    st.write("Hello! I'm here to answer your questions about Anytime Fitness. How can I assist you today?")       

    user_input = st.text_input("Your question: ",key=count)
    increment()
    if "guest" in user_input.lower() or "guests" in user_input.lower():
        st.write("Yes! We do allow guests if you would like to bring a friend.")
        st.write("Our “Bring a Friend” guest policy varies from membership to membership.")
        st.write("The best way to learn about guest passes included in your membership is to contact your local club or review your membership agreement.")
        st.write("Our guest policy requires that visitors come in between 16:00 hours and 18:00 hours after coordinating with the local gym’s staff.")
        
    elif "policy on children" in user_input.lower() or "bring my kid when I workout" in user_input.lower():
        st.write("Anytime Fitness locations do not offer child care or day care.")
        st.write("For that reason, our child policy does not allow for children to be present with their parent while working out unless the child is a member in our system and meets our minimum age requirements (which are set individually by each club!).")

    elif "purchase a day pass" in user_input.lower() or "area on vacation" in user_input.lower() or "cost" in user_input.lower():
        st.write("We’d love to have you! Anytime Fitness offers a single-entry pass for visitors who are unable to commit to a 7-day trial.")
        st.write("This pass allows you to drop in and work out for one day only.")
        st.write("To learn more about our one-day pass policy and price, find your gym online and call the club.")

    elif "exit" in user_input.lower() or "bye" in user_input.lower():
        st.write("Thank you for chatting with me! If you have more questions in the future, feel free to ask.")

    elif user_input.lower():
        st.write("I'm here to help with Anytime Fitness-related questions. Please feel free to ask again or type 'exit' to end the conversation.")


def find_aerial_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    
    # Convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def has_amenities(row,am_list):
    amenities = set(row['amenities'].lower().split(', '))
    return any(item in amenities for item in am_list)


def find_nearest_gym(zipcode, amenities):
    gym_master = pd.read_excel('gym_data.xlsx')
    zip_mapping = pd.read_excel('zipcode_master.xlsx')
    zip_list = zip_mapping['zipcode'].tolist()
    cx_zip = zipcode[:3]
    for i in range(len(zip_list)):
        if(cx_zip==zip_list[i]):
            break
    cx_lat = zip_mapping.iloc[i]['lat']
    cx_long = zip_mapping.iloc[i]['long']
    gym_master['distance'] = 0
    for i in range(len(gym_master)):
        gym_master.at[i,'distance'] = find_aerial_distance(cx_lat,cx_long,gym_master.iloc[i]['lat'],gym_master.iloc[i]['long'])
        
    return gym_master

def input_for_nearest_gym():
    zipcode = st.text_input("Enter your zipcode: ",key=count).upper()
    increment()
    amenities = st.text_input("Enter the gym amenities: ",key=count)
    increment()
    if zipcode and amenities:
        zip_mapping = pd.read_excel('zipcode_master.xlsx')
        zip_list = zip_mapping['zipcode'].tolist()
        cx_zip = zipcode[:3]
    
        if(cx_zip not in zip_list and cx_zip!=''):
            st.write("Sorry, we are not available in your location yet. We are constantly working to expand our network and will be available in your location soon!")
    
        elif (cx_zip in zip_list):
            gym_master = find_nearest_gym(zipcode, amenities)
            
            cx_am = set(amenities.lower().split(', '))
            gym_with_amenities = gym_master[gym_master.apply(has_amenities, args=(cx_am,), axis=1)]
        
        
            if(len(gym_with_amenities)>0):
                gym_with_amenities = gym_with_amenities.sort_values(by='distance').head(5)
                st.write("The centers closest to your location are:\n")
                for i in range(len(gym_with_amenities)):
                    text=f'''({i+1})
    \nLocation: {gym_with_amenities.iloc[i]['address']}, {gym_with_amenities.iloc[i]['location']}, {gym_with_amenities.iloc[i]['zipCode']} 
    \nAmenities: {gym_with_amenities.iloc[i]['amenities']}
    \nDistance: {gym_with_amenities.iloc[i]['distance']:.2f} km
    \n'''
                    st.write(text)  
                
            elif len(gym_with_amenities)==0:            
                text = "Sorry, there are no available gyms with the amenities you have requested. You can also check out these other gyms close to your location:\n\n" 
                for i in range(5):
                    text=f'''({i+1})
    Location: {gym_master.iloc[i]['address']}, {gym_master.iloc[i]['location']}, {gym_master.iloc[i]['zipCode']} 
    Amenities: {gym_master.iloc[i]['amenities']}
    Distance: {gym_master.iloc[i]['distance']:.2f} km
    \n'''
                    st.write(text)


def gym_faq(question):
    question=question.lower()
    if ('all' in question or 'another' in question or 'any ' in question) and  ('gym ' or 'center' and 'anyfitness' in question):
        st.write("Yes your access key will allow you access to all gyms at any location and can work out at any gym you choose. However, there is one exception. There is a 30-day delay on reciprocity when you initially begin your membership. So for the first 30 days it will work only in your home gym")
    elif any(keyword in question for keyword in ['abroad', 'international', 'vacation', 'different country', 'outside Canada']):
        st.write("Yes, globetrotter! When you are a part of the Anytime Fitness family, you can work out at gyms nationwide AND around the globe thanks to our worldwide club access. Think of it as a global membership plan.")
    elif ('lost' in question or "can't find" in question or 'cannot find' in question or 'missing' in question or "don't know where" in question or 'misplaced' in question) and 'key' in question:
        st.write("Oh no! If you’ve lost your key fob, contact your home club ASAP and they will help you purchase a replacement key, for a small fee.")
    elif 'personal' in question and any(keyword in question for keyword in ['train', 'coach', 'specialist']):
        st.write("Anytime Fitness has lots of training options available. Personal Training is offered in a one-on-one format lead by a certified personal trainer, providing a very personalized experience. Small group training is similar to personal training, only it’s more fun as there are typically 2-4 people in a session. Team workouts include 5+ people and provide accountability and an energy-filled atmosphere that keeps you motivated. Make sure to check with your local gym to learn more about personal and team training.")
    elif any(keyword in question for keyword in ['shower', 'locker']):
        st.write("Yes, we do! Making healthy happen should be as easy as possible and the option to take a quick shower after a workout is sometimes the difference between “I can work out” and “I can’t work out.” While all clubs have showers and bathrooms, not all locations offer lockers.")
    elif 'wifi' in question:
        st.write("While many Anytime Fitness locations offer Wifi in their club, it is up to the owner to make it available to members. Don’t hesitate to ask your local club if you do not find the login information readily posted. Each location has separate a Wifi password. Reach out to your local gym to find more information on Wifi availability!")
    elif any(keyword in question for keyword in ['guest', 'visitor', 'friend']):
        st.write("Yes! We do allow guests if you would like to bring a friend. Our guest policy requires that visitors come in during staffed hours after coordinating with the local gym’s staff. Think of staffed hours as guest hours because each guest is required to sign in for the safety of our members!")
    elif any(keyword in question for keyword in ['child', 'kid', 'son', 'daughter', 'baby', 'toddler']):
        st.write("Anytime fitness locations do not offer child care or day care. For that reason, our child policy does not allow for children to be present with their parent while working out unless the child is a member in our system and meets our minimum age requirements (which are set individually by each club!).")
    elif any(keyword in question for keyword in ['age', 'old']):
        st.write("While there isn’t a set age limit, each of our Anytime Fitness locations must comply with state laws on age requirements and age restrictions. Check in with your local gym to learn what the age policy is near you.")
    elif question:
        st.write("I'm sorry, but I couldn't find an answer to your question.")

def repeat_trigger_new_user_flow():
    ip = st.text_input("\n\nEnter 1 - To return to previous menu\n\nEnter 2 - To exit\n\nPlease enter your choice (1/2): ",key=count)
    increment()
    if(ip=="1"):
        new_user_options()
    elif ip:
        st.write("Thank you for talking to us today. Have a nice day!")

def repeat_trigger_existing_user_flow(target_id):
    ip = st.text_input("\n\nEnter 1 - To return to previous menu\n\nEnter 2 - To exit\n\nPlease enter your choice (1/2): ",key=count)
    increment()
    if(ip=="1"):
        existing_user_options(target_id)
    elif ip:
        st.write("Thank you for talking to us today. Have a nice day!")

def manage_membership(target_id):
    df = pd.read_excel('user_data.xlsx')
    #df = df.astype(str)
    reply=st.text_input("\nWould you like to pause,cancel,reactivate or transfer your membership: ",key=count).lower()
    increment()
    if 'pause' in reply:
        condition=df['customerId']==target_id
        # Find the index of the row that matches the condition
        row_index = df[condition].index[0]
        df.at[row_index, 'status'] = "Paused"
        st.write("We have successfully paused your membership. Your automatic billing will stop at the end of this month, access on your key has also been paused")
    elif 'cancel' in reply:
        st.write("You also have the option to pause your membership. Would you like to do that instead?")
        y_n=st.text_input("Enter yes/no :",key=count).lower()
        increment()
        if 'yes' in y_n:
            st.write("Taking you back to manage membership page, hope to see you again at anytimefitness!")
            return manage_membership(target_id)
        elif 'no' in y_n:
            reason=st.text_input("Please enter reason for cancellation",key=count).lower()
            increment()
            condition=df['customerId']==target_id
            # Find the index of the row that matches the condition
            row_index = df[condition].index[0]
            df.at[row_index, 'status'] = "Cancel"
            df.at[row_index, 'cancelReason'] = reason
            st.write("We are sorry to see you go! please return your key to your home gym to complete the process, you have been a valued customer.")
    elif 'reactivate' in reply:
        condition=df['customerId']==target_id
        # Find the index of the row that matches the condition
        row_index = df[condition].index[0]
        if df.at[row_index, 'status'] == "Active":
            st.write("You are already an active member!")
        elif df.at[row_index, 'status']:
            df.at[row_index, 'status'] = "Active"
            st.write("We have successfully reactivated your membership. Your automatic billing will start from today, access on your key has also been activated")
    elif 'transfer' in reply:
        first_name = st.text_input("What's the transfer members first name? ",key=count)
        increment()
        last_name = st.text_input("What's the transfer members last name? ",key=count)
        increment()
        email = st.text_input("What's your email address? ",key=count)
        increment()
        if not validate_email(email):
            st.write("Invalid email format. Please enter a valid email address.")
        phone_number = st.text_input("What's your phone number? ",key=count)
        increment()
        if not validate_phone_number(phone_number):
            st.write("Invalid phone number format. Please enter a valid phone number.")
        zipcode = st.text_input("What's your zipcode? ",key=count)
        increment()
        if not validate_zipcode(zipcode):
            st.write("Invalid zipcode format. Please enter a valid zipcode.")
            condition=df['customerId']==target_id
        # Find the index of the row that matches the condition
        row_index = df[condition].index[0]
        df.at[row_index, 'first_name'] = first_name
        df.at[row_index, 'last_name'] = last_name
        df.at[row_index, 'email'] = email
        df.at[row_index, 'phone'] = phone_number
        df.at[row_index, 'zipcode'] = zipcode
        df.at[row_index, 'status'] = "Transfer"
        st.write("We have successfully transferred your account. The transferred member will be able to use the gym till your membership expires at the end of the year, they can then choose to renew it")
    
    df.to_excel('user_data.xlsx',index=False)
    return True

def calculate_macronutrients(target_id):
    df = pd.read_excel('user_data.xlsx')
    target_df = df[df.customerId == target_id]
    gender = target_df.iloc[0]['gender']
    age = target_df.iloc[0]['age']
    weight = target_df.iloc[0]['weight']
    height = target_df.iloc[0]['height']
    activity_level = target_df.iloc[0]['activity_level']
       
    # Macronutrient ratios based on activity level
    activity_levels = {
        'low': {'carbs': 45, 'protein': 25, 'fat': 30},
        'moderate': {'carbs': 50, 'protein': 30, 'fat': 20},
        'active': {'carbs': 55, 'protein': 35, 'fat': 10}
    }

    # Calculate macronutrient values
    activity_ratio = activity_levels.get(activity_level.lower())
    if not activity_ratio:
        st.write(f"Invalid activity level: {activity_level}")
        return None

    total_calories = 10 * weight + 6.25 * height - 5 * age + 5
    carb_calories = (activity_ratio['carbs'] / 100) * total_calories
    protein_calories = (activity_ratio['protein'] / 100) * total_calories
    fat_calories = (activity_ratio['fat'] / 100) * total_calories

    # Convert calories to grams
    carb_grams = carb_calories / 4
    protein_grams = protein_calories / 4
    fat_grams = fat_calories / 9

    # Create a DataFrame to store the results
    nutrient_data = {
        'Nutrient': ['Carbohydrates', 'Protein', 'Fat'],
        'Grams': [carb_grams, protein_grams, fat_grams]
    }
    
    nutrient_df = pd.DataFrame(nutrient_data)
    st.write("Your macronutrient levels are: \n")
    for i in range(len(nutrient_df)):
        st.write(f'''{nutrient_df.iloc[i]['Nutrient']}: {nutrient_df.iloc[i]['Grams']:.2f} gm''')    

def analyze_gym_usage(target_id):

    # Read the CSV file into a DataFrame
    df = pd.read_csv('gym_usage_2.csv')
    df2 = pd.read_excel('user_data.xlsx')
    target_df = df2[df2.customerId == target_id]
    name = target_df.iloc[0]['first_name']
    # Filter data for the specified GymID
    gym_data = df[df['customerId'] == target_id]
    # Calculate total hours spent at the gym
    #gym_data['Session Duration (hours)'] = gym_data['Session Duration (hours)'].str.replace(',', '.').astype(float)
    # Group by date and sum session durations
    total_hours = gym_data.groupby('Date').sum()
    hours_sum = total_hours['Session Duration (hours)'].sum() 
    dates = total_hours.index 
    hours = total_hours['Session Duration (hours)']
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(dates, hours)
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title(f"Daily Workout Time for {name}")

    st.pyplot()

    st.write(f"Total hours spent in gym by {name}: {hours_sum:.2f} hours")


def recommend_trainer(user_req, trainers_df):
    sia = SentimentIntensityAnalyzer()
    reviews_df = pd.read_csv('gym_trainer_reviews.csv')
    user_req = user_req.lower()

    vectorizer = CountVectorizer()
    spec_matrix = vectorizer.fit_transform(trainers_df['Specialization'].str.lower()).toarray()

    user_vector = vectorizer.transform([user_req]).toarray()

    cosine_sim = cosine_similarity(user_vector, spec_matrix)[0]
    sorted_indices = cosine_sim.argsort()[::-1]

 

    best_match = None
    for idx in sorted_indices:
        if trainers_df['Review_Score'][idx] == trainers_df['Review_Score'][sorted_indices[0]]:
            best_match = trainers_df.iloc[idx]
            break

 

    return best_match

 

def map_review_score_to_rating(review_score):
    rating = round(1 + (review_score + 1) * 2)
    return min(max(rating, 1), 5)

 

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    return sentiment_scores['compound']


def input_for_sentiment_analysis(target_id):
    df = pd.read_excel('user_data.xlsx')
    trainers_df = pd.read_csv('gym_trainers_dataset.csv')
    reviews_df = pd.read_csv('gym_trainer_reviews.csv')

    reviews_df['Review_Score'] = reviews_df['Review'].apply(analyze_sentiment)

    trainers_df = trainers_df.merge(reviews_df.groupby('Trainer')['Review_Score'].mean(), left_on='Name', right_on='Trainer', how='left')

    trainers_df['Review_Score'].fillna(0, inplace=True)
    trainers_df['Rating'] = trainers_df['Review_Score'].apply(map_review_score_to_rating)

    assigned_trainers = set()

    user_req = st.text_input("Please enter your trainer requirement (e.g., yoga, weight training, cardio): ",key=count).lower()
    increment()
    if user_req:
        if user_req in trainers_df['Specialization'].tolist():
            matched_trainer = recommend_trainer(user_req, trainers_df)
            if matched_trainer is not None:
                st.write("We found a trainer for you!")
                st.write("Trainer Name:", matched_trainer["Name"])
                st.write("Specialization:", matched_trainer["Specialization"])
                st.write("Age:", matched_trainer["Age"])
                st.write("Rating:", matched_trainer["Rating"])
                df.loc[df['customerId']==target_id,'trainer'] = matched_trainer['Name']
                df.to_excel('user_data.xlsx',index=False)
            elif matched_trainer:
                st.write("Sorry, no available trainers match your requirement.")
        elif user_req:
            st.write("Sorry, you seem to have entered an incorrect gymId. Please try again")
            input_for_sentiment_analysis(target_id)

def gym_occupancy():
    df = pd.read_csv('gym_occupancy.csv')
    gym_data = pd.read_excel('gym_data.xlsx')
    gym_id = st.text_input("\nPlease enter your home gymId: ",key=count)
    increment()
    if gym_id:
        gym_id = int(gym_id)
        if gym_id in gym_data['gymId'].tolist():
            var = st.text_input("\nWhen are you planning to go to the gym? ",key=count)
            increment()
            if var:
                if var=='today':
                    req_date = datetime.now().date()
                elif var =='tomorrow':
                    req_date = (datetime.now() + timedelta(days=1)).date()
                elif var:
                    req_date = datetime.now().date()
                
                df2 = pd.merge(df,gym_data[['gymId','capacity']],how='inner',on='gymId')
                df2['occupancy'] = df2['number_people'] / df2['capacity']
                
                X = df2[['gymId', 'month', 'day_of_week', 'hour']]
                y = df2['occupancy']
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                model = RandomForestRegressor()
            
                model.fit(X_train, y_train)
                
                days = 7
                hours_per_day = 15  # From 7 am to 10 pm
                new_data = pd.DataFrame(columns=['gymId', 'month', 'day_of_week', 'hour'])
                
                new_data.to_excel('test.xlsx',index=False)
            
                for day in range(days):
                    for hour in range(hours_per_day):
                        new_data = new_data.append({'gymId': gym_id,'month': int((req_date + timedelta(days=days)).strftime("%m")),'day_of_week': day,'hour': 7 + hour}, ignore_index=True)
            
                predicted_occupancy = model.predict(new_data)
                new_data['predicted_occupancy'] = predicted_occupancy
                
                dfx = new_data.copy()
              
                if var=='today':
                    day_of_week = req_date.weekday()
                    hour = int(datetime.now().strftime("%H"))
                    dfx = new_data[(new_data['day_of_week']==day_of_week)&(new_data['hour']>=hour)]
                    if(len(dfx)>0):
                        dfx = dfx.sort_values(by='predicted_occupancy').head(5)
                        st.write("\nThe best time for you to visit the gym today is: ")
                        text = ''
                        for i in range(len(dfx)):
                            if(dfx.iloc[i]['hour']<12):
                                text+= f'''{dfx.iloc[i]['hour']} AM, '''
                            elif(dfx.iloc[i]['hour']==12):
                                text+= f'''{int(dfx.iloc[i]['hour'])} PM, '''
                            elif(dfx.iloc[i]['hour']>12):
                                text+= f'''{int(dfx.iloc[i]['hour'])-12} PM, '''
                        st.write(text[:-2])
                    elif len(dfx)==0:
                        st.write("Sorry, there is no suitable time to visit the gym today")
                    
                if len(dfx)==0 or var=='tomorrow':
                    day_of_week = req_date.weekday()
                    dfx = new_data[(new_data['day_of_week']==day_of_week)]
                    if(len(dfx)>0):
                        dfx = dfx.sort_values(by='predicted_occupancy').head(5)
                        st.write("\nThe best time for you to visit the gym tomorrow is: ")
                        text = ''
                        for i in range(len(dfx)):
                            if(dfx.iloc[i]['hour']<12):
                                text+= f'''{dfx.iloc[i]['hour']} AM, '''
                            elif(dfx.iloc[i]['hour']==12):
                                text+= f'''{int(dfx.iloc[i]['hour'])} PM, '''
                            elif(dfx.iloc[i]['hour']>12):
                                text+= f'''{int(dfx.iloc[i]['hour'])-12} PM, '''
                        st.write(text[:-2])
                
                elif len(dfx)==0 or (var!='tomorrow' and var!='today'):
                    st.write("\nThe best time for you to visit the gym on: \n")
                    for i in range(7):
                        dfx = new_data[new_data['day_of_week']==i]
                        dfx = dfx.sort_values(by='predicted_occupancy').head(5)
                        text = calendar.day_name[i] + ': '
                        for i in range(len(dfx)):
                            if(dfx.iloc[i]['hour']<12):
                                text+= f'''{dfx.iloc[i]['hour']} AM, '''
                            elif(dfx.iloc[i]['hour']==12):
                                text+= f'''{int(dfx.iloc[i]['hour'])} PM, '''
                            elif(dfx.iloc[i]['hour']>12):
                                text+= f'''{int(dfx.iloc[i]['hour'])-12} PM, '''
                        st.write(text[:-2])
        elif gym_id:
            st.write("Sorry, you seem to have entered an incorrect gymId. Please try again")
            gym_occupancy()


def suggest_exercises():
    try:
        pattern = re.compile(r'<.*?>')
        var = st.text_input("\nWhat muscles are you planning to workout on?(For eg. Biceps, Shoulders, Triceps etc)\nPlease enter your choice: ",key=count).capitalize()
        increment()
        if var:
            url = 'https://wger.de/api/v2/muscle'  
            response = requests.get(url)
            data = response.json()
            results = data['results']
            df_muscles = pd.DataFrame(results)
            if var in df_muscles['name_en'].tolist():
                mid = df_muscles.loc[df_muscles['name_en'] == var, 'id'].values[0]
                url = f'https://wger.de/api/v2/exercise/?muscles={mid}&language=2'  
                response = requests.get(url)
                data = response.json()
                results = data['results']
                dfex = pd.DataFrame(results)
                dfex = dfex.sort_values(by='id').head(5).reset_index(drop=True)
                st.write(f"\nThe following are the recommended exercises to workout your {var}: \n")
                for i in range(len(dfex)):
                    url = f"https://wger.de/api/v2/exerciseimage/?is_main=True&exercise_base={dfex.iloc[i]['exercise_base']}"
                    response = requests.get(url)
                    data = response.json()
                    results = data['results']
                    dfim = pd.DataFrame(results)
                    if(len(dfim)>0):
                        img_url = dfim.iloc[0]['image']
                        text= f'''Exercise Name: {dfex.iloc[i]['name']}
\nDescription: {re.sub(pattern, '', dfex.iloc[i]['description'])}\n'''
                        st.write(text)
                        st.image(img_url, width=200)
                    elif(len(dfim)==0):
                        text= f'''Exercise Name: {dfex.iloc[i]['name']}
\nDescription: {re.sub(pattern, '', dfex.iloc[i]['description'])}\n'''
                        
            elif var not in df_muscles['name_en'].tolist():
                st.write("\nSorry, you seem to have entered an invalid input. Please try again\n")
                suggest_exercises()
    except:
        pass
    #         st.write("\nSorry, we encountered an internal error. Please try again.\n")
    #         suggest_exercises()
        
        
def email_sender(customer_id, first_name, email, membership_type):
    
    text = f'''Dear {first_name},

\n We are excited to welcome you to Anytime Fitness! Your enrollment in our gym's membership program is confirmed, and we're thrilled to have you on board.

\n Here are your enrollment details:

\n Customer ID: {customer_id}
\n Membership Plan: {membership_type}

\n We're committed to helping you achieve your fitness goals and providing you with a positive gym experience. If you have any questions or need assistance, feel free to reach out to our team or talk to AnytimeAssistant, our personalized chatbot.

\n Once again, welcome to Anytime Fitness! We can't wait to see you at the gym and support you on your fitness journey.

\n Best regards,
\n Anytime Fitness Team'''

    fromName = "Anytime Fitness"
    fromAddr = "jacksonreo31@gmail.com"
    toaddr = email
    rcpt = [toaddr]
    msg = MIMEMultipart('alternative')
    msg['From'] = "{} <{}>".format(fromName,fromAddr)
    msg['To'] = toaddr
    msg['Subject'] = "Gym Membership Enrollment Confirmation"
    body = text
    msg.attach(MIMEText(body, 'plain'))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromAddr, "zjtbyqyzaxncawqq")
    text = msg.as_string()
    s.sendmail(fromAddr, rcpt, text)
    s.quit() 



def main():
    st.write('<style>body { background-color: #F3EFFF; }</style>', unsafe_allow_html=True)
    # Display an image from a local file path
    image_path = "AnytimeFitnessLogo-with-Tag.png"
    st.image(image_path, use_column_width=True)
#Start of Main 

    st.write("Hello! Welcome to AnytimeAssistant, the chatbot for Anytime Fitness.")

    user_data = pd.read_excel('user_data.xlsx')

    response = st.text_input("\nAre you a new user, an existing user, or do you want to exit? (type 'new', 'existing', or 'exit'): ",key=count)
    increment()

    if response.lower() == 'new':
        new_user_options()
    elif response.lower() == 'existing':
        target_id = st.text_input("\nPlease enter your customer id: ",key=count).lower()
        increment()
        if target_id in user_data['customerId'].tolist():
            existing_user_options(target_id)
        elif target_id :
            st.write("Sorry, you seem to have entered an invalid customer id. Please try again.")
            
    elif response.lower() == 'exit':
        st.write("Thank you! Have a nice day.")
    elif response:
        st.write("We're sorry, we couldn't understand your response. Please type 'new', 'existing', or 'exit'.")    
  
if __name__ == "__main__":
 main()
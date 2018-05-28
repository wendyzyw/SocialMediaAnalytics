# Python
import oauth2 as oauth
import cgi
import urllib.parse
import time
import json
import tweepy
import calendar
import simplejson
import facebook
import requests
import random
import nltk
import sys
import unicodedata
import string
nltk.download('stopwords')
nltk.download('wordnet')
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from operator import itemgetter
from watson_developer_cloud import PersonalityInsightsV3, ToneAnalyzerV3
from watson_developer_cloud import WatsonApiException
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
	import Features, KeywordsOptions, ConceptsOptions

# Django
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, \
    PasswordResetDoneView, PasswordChangeDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from social_django.models import UserSocialAuth

# my app
from .models import Profile, User
from .forms import LoginForm, ChangepassForm, EdituserinfoForm, RegisterForm, MyPasswordResetForm

####################################
# twitter login 
consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

# step 1
request_token_url = 'https://api.twitter.com/oauth/request_token'
# step 2
authenticate_url = 'https://api.twitter.com/oauth/authenticate'
# step 3
access_token_url = 'https://api.twitter.com/oauth/access_token'

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
regex_str = [
 emoticons_str,
 r'<[^>]+>',  # HTML tags
 r'(?:@[\w_]+)',  # @-mentions
 r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
 r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

 r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
 r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
 r'(?:[\w_]+)',  # other words
 r'(?:\S)'  # anything else
]

tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

# primary pages
def index(request):
    return render(request, 'index.html')

def login(request):
    # User.objects.filter(username='ElfWx').delete()
    if request.method == "POST":
        uf = LoginForm(request.POST)
        if uf.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth_login(request, user)
                return render(request, 'account-home.html')
            else:
                return render(request, 'Login.html',{'uf': uf, 'message': 'username or password is not correct, please check or signup!'})
        else:
            return render(request, 'Login.html', {'uf': uf,'message': 'please fill in all the information or note the format of entered password!'})
    else:
        uf = LoginForm()
    return render(request, 'Login.html', {'uf': uf})
	# return render(request, 'Login.html')


def register(request):
    if request.method == 'POST':  # when submit the form
        uf = RegisterForm(request.POST)  # include the data submitted
        if uf.is_valid():  # if the data submitted is valid
            username = request.POST.get('username', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')
            if password != password_confirm:
                return render(request, 'signup.html', {'uf': uf, 'message': 'please confirm your new password!'})
            else:
                try:
                    User.objects.create_user(username=username, password=password, email=email,
                                                 phone='0', first_name=first_name, last_name=last_name)
                    return login(request)
                except:
                    return render(request, 'signup.html', {'uf': uf, 'message': 'user has existed！'})
        else:
            return render(request, 'signup.html', {'uf': uf,
                                                   'message': 'Please fill in all information or note the format of '
                                                              'entered password!'})
    else:
        uf = RegisterForm()
        return render(request, 'signup.html', {'uf': uf})
		
def forgetPw(request):
    return render(request, 'forget_password.html')


def account(request):
    return render(request, 'account-home.html')


def manage1(request):
    if request.method == "POST":
        uf = ChangepassForm(request.POST)
        if uf.is_valid():
            username = request.user.username
            old_password = request.POST.get('old_password', '')
            user = auth.authenticate(username=username, password=old_password)
            if user is not None and user.is_active:
                new_password1 = request.POST.get('new_password1', '')
                if new_password1 == old_password:
                    return render(request, 'Manage1_privacy.html',
                                  {'uf': uf, 'message': 'Please set one different new password!'})
                else:
                    new_password2 = request.POST.get('new_password2', '')
                    if new_password1 != new_password2:
                        return render(request, 'Manage1_privacy.html',
                                      {'uf': uf, 'message': 'Please confirm your new password!'})
                    else:
                        user.set_password(new_password1)
                        user.save()
                        return render(request, 'Manage1_privacy.html', {'uf': uf, 'message': 'success!'})
            else:
                return render(request, 'Manage1_privacy.html',
                              {'uf': uf, 'message': 'Your old password is not correct!'})
        else:
            return render(request, 'Manage1_privacy.html', {'uf': uf, 'message':
                'Please fill in all the information or note the format of entered password (at least 8 characters, including both numbers and letters)!'})
    else:
        uf = ChangepassForm()
        return render(request, 'Manage1_privacy.html', {'uf': uf})


def manage2(request):
    if request.method == "POST":
        uf = EdituserinfoForm(request.POST)
        if uf.is_valid():
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            address = request.POST.get('address', '')
            phone = request.POST.get('phone', '')
            zip_code = request.POST.get('zip_code', '')
            gender = request.POST.get('gender', '')
            state = request.POST.get('state', '')
            city = request.POST.get('city', '')
            email = request.POST.get('email', '')
            username = request.user.username
            User.objects.filter(username=username).update(first_name=first_name, last_name=last_name,
                                                              address=address, phone=phone, zip_code=zip_code,
                                                              gender=gender,
                                                              state=state, city=city, email=email)
            return render(request, 'account-home.html', {'uf': uf, 'message': 'success!'})
        else:
            return render(request, 'Manage2_Personal.html',
                          {'uf': uf, 'message': 'Please fill in all your information!'})
    else:
        uf = EdituserinfoForm()
        return render(request, 'Manage2_Personal.html', {'uf': uf})


def manage3(request):
    user = request.user
    twitter_account = None
    twitter_name = None
    twitter_date = None
    facebook_account = None
    facebook_date = None
    facebook_id = None

    try:
        twitter_account = user.social_auth.get(provider='twitter')
        if twitter_account is not None:
            twitter_json = twitter_account.extra_data
            twitter_name = twitter_json['access_token']['screen_name']
            twitter_date = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(twitter_json['auth_time']))

    except UserSocialAuth.DoesNotExist:
        twitter_account = None

    try:
        facebook_account = user.social_auth.get(provider='facebook')
        if facebook_account is not None:
            facebook_json = facebook_account.extra_data
            facebook_date = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(facebook_json['auth_time']))
            facebook_id = facebook_json['id']
            # get image url
            fb_profile_url = url = "http://graph.facebook.com/%s/picture?type=large" % facebook_id

    except UserSocialAuth.DoesNotExist:
        facebook_account is None

    # social_backend = request.session['social_auth_last_login_backend']
    return render(request, 'Manage3_social.html',
                  {'twitter_account': twitter_account, 'twitter_date': twitter_date,
                   'twitter_name': twitter_name, 'facebook_account': facebook_account, 'facebook_date': facebook_date,
                   'facebook_id': facebook_id})


def user_preferences(request):
    likely = []
    unlikely = []
    final_likely = []
    final_unlikely = []
    preferences = request.session['preferences']
    for preference in preferences:
        for consumption_preference in preference["consumption_preferences"]:
            if (consumption_preference["score"] == 1):
                consumption_preference2 = consumption_preference["name"]
                consumption_preference3 = consumption_preference2.replace('Likely to', ' ')
                likely.append(consumption_preference3)
            else:
                consumption_preference4 = consumption_preference["name"]
                consumption_preference5 = consumption_preference4.replace('Likely to', ' ')
                unlikely.append(consumption_preference5)
    for i in range(0, 4):
        r = random.randint(0, len(likely)-1)
        final_likely.append(likely[r])
    for i in range(0, 4):
        r = random.randint(0, len(unlikely)-1)
        final_unlikely.append(unlikely[r])
    return render(request, 'user_preferences.html', {'likely': final_likely, 'unlikely': final_unlikely})


def keywords(request):
    keywords = request.session['keywords']
    # create nodes data
    node_data = {'name': 'outermost', 'children': [
        {'name': 'positive', 'children': []},
        {'name': 'negative', 'children': []}
    ]}
    # construct data with emotion values
    data_by_id = {}
    id_by_name = {}
    id_by_name['outermost'] = ''
    id_by_name['positive'] = '1'
    id_by_name['negative'] = '2'
    data_with_values = {}
    for keyword in keywords:
        temp = {'name': keyword['text'], 'ID': '', 'relevance': int(keyword['relevance'] * 100)}
        if keyword['sentiment']['label'] == 'positive':
            id = '1.' + str(len(node_data['children'][0]['children']) + 1)
            temp['ID'] = id
            node_data['children'][0]['children'].append(temp)

        else:
            id = '2.' + str(len(node_data['children'][0]['children']) + 1)
            temp['ID'] = id
            node_data['children'][1]['children'].append(temp)

        id_by_name[keyword['text']] = id
        value_obj = {'key': id, 'values': []}
        
        # to avoid keyerror if keyword has no emotion key 
        if 'emotion' in keyword:
            sadness = {'ID': id, 'emotion': 'sadness', 'value': keyword['emotion']['sadness']}
            joy = {'ID': id, 'emotion': 'joy', 'value': keyword['emotion']['joy']}
            fear = {'ID': id, 'emotion': 'fear', 'value': keyword['emotion']['fear']}
            disgust = {'ID': id, 'emotion': 'disgust', 'value': keyword['emotion']['disgust']}
        	anger = {'ID': id, 'emotion': 'anger', 'value': keyword['emotion']['anger']}
        else:
            sadness = {'ID': id, 'emotion': 'sadness', 'value': 0}
            joy = {'ID': id, 'emotion': 'joy', 'value': 0}
            fear = {'ID': id, 'emotion': 'fear', 'value': 0}
            disgust = {'ID': id, 'emotion': 'disgust', 'value': 0}
            anger = {'ID': id, 'emotion': 'anger', 'value': 0}
             	
        value_obj['values'].extend([sadness, joy, fear, disgust, anger])
        data_with_values[id] = value_obj

    return render(request, 'keywords.html',
                  {'node_data': node_data, 'id_by_name': id_by_name, 'data_with_values': data_with_values})


def tone_analysis(request):
    tone = request.session['tone']
    document_tone = tone['document_tone']
    sentences_tone = tone['sentences_tone']

    # build data structure to stores aggregated scores for all 13 tones
    allTones = []
    t1 = {'Id': 1, 'DisplayName': 'Anger', 'category': 'Emotion Tone', 'IndexScore': 0.0, 'AllText': []}
    t2 = {'Id': 2, 'DisplayName': 'Disgust', 'category': 'Emotion Tone', 'IndexScore': 0.0, 'AllText': []}
    t3 = {'Id': 3, 'DisplayName': 'Fear', 'category': 'Emotion Tone', 'IndexScore': 0.0, 'AllText': []}
    t4 = {'Id': 4, 'DisplayName': 'Joy', 'category': 'Emotion Tone', 'IndexScore': 0.0, 'AllText': []}
    t5 = {'Id': 5, 'DisplayName': 'Sadness', 'category': 'Emotion Tone', 'IndexScore': 0.0, 'AllText': []}
    t6 = {'Id': 6, 'DisplayName': 'Analytical', 'category': 'Language Tone', 'IndexScore': 0.0, 'AllText': []}
    t7 = {'Id': 7, 'DisplayName': 'Confident', 'category': 'Language Tone', 'IndexScore': 0.0, 'AllText': []}
    t8 = {'Id': 8, 'DisplayName': 'Tentative', 'category': 'Language Tone', 'IndexScore': 0.0, 'AllText': []}
    t9 = {'Id': 9, 'DisplayName': 'Openness', 'category': 'Social Tone', 'IndexScore': 0.0, 'AllText': []}
    t10 = {'Id': 10, 'DisplayName': 'Conscientiousness', 'category': 'Social Tone', 'IndexScore': 0.0, 'AllText': []}
    t11 = {'Id': 11, 'DisplayName': 'Extraversion', 'category': 'Social Tone', 'IndexScore': 0.0, 'AllText': []}
    t12 = {'Id': 12, 'DisplayName': 'Agreeableness', 'category': 'Social Tone', 'IndexScore': 0.0, 'AllText': []}
    t13 = {'Id': 13, 'DisplayName': 'Emotional Range', 'category': 'Social Tone', 'IndexScore': 0.0, 'AllText': []}
    allTones.extend([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13])

    # calculate aggregated score for each tone
    for sentence in sentences_tone:
        categories = sentence['tone_categories']
        emotion = categories[0]['tones']
        language = categories[1]['tones']
        social = categories[2]['tones']
        counter1 = 0
        for each in emotion:
            allTones[counter1]['IndexScore'] += each['score']
            counter1 += 1
        counter2 = 5
        for each in language:
            allTones[counter2]['IndexScore'] += each['score']
            counter2 += 1
        counter3 = 8
        for each in social:
            allTones[counter3]['IndexScore'] += each['score']
            counter3 += 1
    # print(allTones)

    return render(request, 'toneAnalysis.html', {'tone_data': allTones})


def user_personality(request):
    personality = request.session['user_personality']
    sbData = {'name': 'Sources', 'color': "#d8c51d", 'percent': '', 'children': []}
    totalScore = 0.0
    # top level children list
    for eachPersonality in personality:
        # to hold 5 traits within each personality
        onePersonality = {'name': eachPersonality['name'], 'color': "#d8c51d",
                          'size': round(eachPersonality['raw_score'], 4), 'percent': 0, 'children': []}
        trait1 = eachPersonality['children'][0]
        trait2 = eachPersonality['children'][1]
        trait3 = eachPersonality['children'][2]
        trait4 = eachPersonality['children'][3]
        trait5 = eachPersonality['children'][4]
        totalScore = trait1['raw_score'] + trait2['raw_score'] + trait3['raw_score'] + trait4['raw_score'] + trait5['raw_score']
        child1 = {'name': trait1['name'], 'color': '#d8c51d', 'size': round(trait1['raw_score'], 4),
                  'percentile': round(trait1['percentile'], 4), 'percent': round(trait1['raw_score'] / totalScore, 4)}
        child2 = {'name': trait2['name'], 'color': '#d8c51d', 'size': round(trait2['raw_score'], 4),
                  'percentile': round(trait2['percentile'], 4), 'percent': round(trait2['raw_score'] / totalScore, 4)}
        child3 = {'name': trait3['name'], 'color': '#d8c51d', 'size': round(trait3['raw_score'], 4),
                  'percentile': round(trait3['percentile'], 4), 'percent': round(trait3['raw_score'] / totalScore, 4)}
        child4 = {'name': trait4['name'], 'color': '#d8c51d', 'size': round(trait4['raw_score'], 4),
                  'percentile': round(trait4['percentile'], 4), 'percent': round(trait4['raw_score'] / totalScore, 4)}
        child5 = {'name': trait5['name'], 'color': '#d8c51d', 'size': round(trait5['raw_score'], 4),
                  'percentile': round(trait5['percentile'], 4), 'percent': round(trait5['raw_score'] / totalScore, 4)}
        onePersonality['children'].extend([child1, child2, child3, child4, child5])
        sbData['children'].append(onePersonality)
        totalScore += eachPersonality['raw_score']

    sbData['children'][0]['percent'] = round(personality[0]['raw_score'] / totalScore, 4)
    sbData['children'][1]['percent'] = round(personality[1]['raw_score'] / totalScore, 4)
    sbData['children'][2]['percent'] = round(personality[2]['raw_score'] / totalScore, 4)
    sbData['children'][3]['percent'] = round(personality[3]['raw_score'] / totalScore, 4)
    sbData['children'][4]['percent'] = round(personality[4]['raw_score'] / totalScore, 4)

    return render(request, 'user_personality.html', {'sbData': sbData})


def user_values(request):
    values = request.session['user_values']
    radarObj = []
    for eachValue in values:
        temp = {"axis": eachValue["name"], "value": round(eachValue["raw_score"], 2),
                "percentile": round(eachValue["percentile"], 2)}
        radarObj.append(temp)
    print(radarObj)
    radarData = simplejson.dumps(radarObj)

    return render(request, 'user_values.html', {'radarData': radarData})


def data(request):
    user = request.user
    facebook_account = None
    twitter_account = None
    radarData = []
    try:
        twitter_account = user.social_auth.get(provider='twitter')
        if twitter_account is not None:
            twitter_json = twitter_account.extra_data

            # retriev user timeline
            auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
            auth.set_access_token(twitter_json['access_token']['oauth_token'],
                                  twitter_json['access_token']['oauth_token_secret'])
            # store twitter tokens to request.session
            request.session['twitter_token'] = twitter_json['access_token']['oauth_token']
            request.session['twitter_secret'] = twitter_json['access_token']['oauth_token_secret']
            api = tweepy.API(auth)
            data = api.user_timeline()

            # format timeline data from twitter for request format to PersonalityInsightsV3 api
            reqJson = []
            for each in data:
                temp = {'content': each.text, 'contenttype': "text/plain", 'id': each.id, 'language': 'en'}
                reqJson.append(temp)
            json_input = {'contentItems': reqJson}

            try:
                ###############################################################
                personality_insights = PersonalityInsightsV3(
                    version='2017-10-13',
                    username='9576f431-9a16-435e-85d3-d9dcf455969d',
                    password='0HOzAgnxjz3d'
                )

                profile = personality_insights.profile(
                    content=json_input, content_type='application/json',
                    raw_scores=True, consumption_preferences=True)
                # print(json.dumps(profile["values"], indent=2))

                personality = profile["personality"]
                needs = profile["needs"]
                values = profile["values"]
                # behavior = profile["behavior"]
                # print("h4")
                consumption_preferences = profile["consumption_preferences"]

                # format the values data to pipeline for radar chart
                radarObj = []
                for eachNeed in needs:
                    temp = {"axis": "Need " + eachNeed["name"], "value": round(eachNeed["raw_score"], 2),
                            "percentile": round(eachNeed["percentile"], 2)}
                    radarObj.append(temp)
                radarData = simplejson.dumps(radarObj)

                # store into session
                request.session['user_values'] = values
                request.session['user_needs'] = needs
                request.session['user_personality'] = personality
                request.session['preferences'] = consumption_preferences

                ###############################################################
                reqStrList = []
                for each in data:
                    reqStrList.append(each.text)
                reqStr = '. '.join(reqStrList)

                tone_analyzer = ToneAnalyzerV3(
                    version='2016-05-19',
                    username='6c984f2f-56ea-4a07-a59c-9c86e5b5d00f',
                    password='GlMwVmKrNpwt'
                )
                tone_analyzer.set_default_headers({'x-watson-learning-opt-out': "true"})

                content_type = 'application/json'
                tone = tone_analyzer.tone({"text": reqStr}, content_type)

                # print(json.dumps(tone, indent=2))
                request.session['tone'] = tone
                ###############################################################
                natural_language_understanding = NaturalLanguageUnderstandingV1(
                    username='fc0c4c4c-a1aa-4428-b624-1d995c7d4183',
                    password='m6QGBRl7hG3w',
                    version='2018-03-16')

                response = natural_language_understanding.analyze(
                    text=reqStr,
                    features=Features(
                        keywords=KeywordsOptions(
                            emotion=True,
                            sentiment=True,
                            limit=50)))

                # print(json.dumps(response, indent=2))
                request.session['keywords'] = response['keywords']

            except WatsonApiException as ex:
                print("Method failed with status code " + str(ex.code) + ": " + ex.message)

    except:
        twitter_account = None

    ###########################################################################
    # retrieve facebook account information
    try:
        facebook_account = user.social_auth.get(provider='facebook')
        if facebook_account is not None:
            facebook_json = facebook_account.extra_data

            request.session['facebook_token'] = facebook_json['access_token']

    except UserSocialAuth.DoesNotExist:
        facebook_account is None

    return render(request, 'user_needs.html', {'radarData': radarData})


def social_network(request):
    # get friends from twitter
    consumer_key = settings.TWITTER_TOKEN
    consumer_secret = settings.TWITTER_SECRET
    access_token = request.session['twitter_token']
    access_token_secret = request.session['twitter_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    my_followers = api.followers()
    my_friends = api.friends()
    my = api.me()
    friends = []
    edges = []
    info = dict(nodes=friends, links=edges)
    user = {'id': my.screen_name, 'group': 1}
    twitter_dict = {'id': 'twitter', 'group': 2}
    facebook_dict = {'id': 'facebook', 'group': 3}
    tumblr_dict = {'id': 'tumblr', 'group': 6}
    reddit_dict = {'id': 'reddit', 'group': 7}
    edges1 = {'source': my.screen_name, 'target': 'facebook', 'value': 2}
    edges2 = {'source': my.screen_name, 'target': 'twitter', 'value': 2}
    edges3 = {'source': my.screen_name, 'target': 'tumblr', 'value': 2}
    edges4 = {'source': my.screen_name, 'target': 'reddit', 'value': 2}
    friends.append(twitter_dict)
    friends.append(user)
    friends.append(facebook_dict)
    friends.append(tumblr_dict)
    friends.append(reddit_dict)
    for follower in my_followers:
        for friend in my_friends:
            if friend.id == follower.id:
                temp = {'id': friend.screen_name, 'group': 4}
                friends.append(temp)
    for line in friends:
        if line['id'] != 'facebook' and line['id'] != 'twitter' and line['id'] != my.screen_name and line[
            'id'] != 'tumblr' and line['id'] != 'reddit':
            temp2 = {'source': 'twitter', 'target': line['id'], 'value': 2}
            edges.append(temp2)
    edges.append(edges1)
    edges.append(edges2)
    edges.append(edges3)
    edges.append(edges4)
    # get friends from facebook
    token = request.session['facebook_token']
    graph = facebook.GraphAPI(access_token=token)
    facebook_friends = graph.get_connections(id='me', connection_name='friends')
    for post in facebook_friends["data"]:
        temp3 = {'id': post["name"], 'group': 5}
        friends.append(temp3)
    for post2 in facebook_friends["data"]:
        temp4 = {'source': 'facebook', 'target': post2["name"], 'value': 2}
        edges.append(temp4)
    # return JsonResponse(info,safe = False)
    return render(request, 'social_network.html', {'network_info': info})


def time_heatmap(request):
    user = request.user
    twitter_account = user.social_auth.get(provider='twitter')
    twitter_json = twitter_account.extra_data
    # retriev user timeline
    auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
    auth.set_access_token(twitter_json['access_token']['oauth_token'],
                          twitter_json['access_token']['oauth_token_secret'])
    api = tweepy.API(auth)
    data = api.user_timeline()
    array = [[0] * 24 for _ in range(7)]

    for each in data:
        created_time = each.created_at
        weekday = created_time.isoweekday()
        hour = created_time.hour
        if hour == 0:
            hour = 24
        array[weekday - 1][hour - 1] += 1

    facebook_token = request.session['facebook_token']
    user = 'BillGates'

    person = 'https://graph.facebook.com/v3.0/me/posts?access_token=' + facebook_token

    posts = requests.get(person).json().get('data')
    reqJson_f = []
    for post in posts:
        message = post.get('message')
        created_time = post.get('created_time')
        datetime_object = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+%f')

        # print('message = ', message)
        # print('created_time = ', created_time)
        # print('datetime = ', datetime_object)
        # print(type(datetime_object))
        # print('weekday = ', )

        if message != None:
            weekday = datetime_object.isoweekday()
            hour = datetime_object.hour
            if hour == 0:
                hour = 24
            array[weekday - 1][hour - 1] += 1

    tf_list = []

    for i in range(7):
        for j in range(24):
            ele = {'day': i + 1, 'hour': j + 1, 'value': array[i][j]}
            tf_list.append(ele)

    heatmapData = simplejson.dumps(tf_list)
    # print('tf_list = ', tf_list)

    return render(request, 'heatmap.html', {'heatmapData': heatmapData})

def tokenize(s):
 return tokens_re.findall(s)

def preprocess(s, lowercase=False):
 tokens = tokenize(s)
 if lowercase:
  tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
 return tokens


def remove_non_ascii_2(text):
 return re.sub(r'[^\x00-\x7F]', ' ', text)


def get_string_list(request):
	user = request.user
	twitter_account = user.social_auth.get(provider='twitter')
	twitter_json = twitter_account.extra_data
	# retriev user timeline
	auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN,settings.TWITTER_SECRET)
	auth.set_access_token(twitter_json['access_token']['oauth_token'],twitter_json['access_token']['oauth_token_secret'])
	api = tweepy.API(auth)

	lemmatizer = WordNetLemmatizer()
	stop_words = set(stopwords.words('english'))
	tweet_text = []
	#facebook_token = 'EAACEdEose0cBAHr03FDFLi5mt6fXJZBB4eHehYMm41FXIyoZAmqSw4DicBzJVpRmXcecvdnGJgGAu2aghZAfuDRMZA8jnWfXNnCNPopMBW6GFzZCLS0M8Kt9ndEb5VZC3kEIasDXKBfXN2raZC38vzJ90DeuhnZC2znS1MSZBdaUVZAKoafNukRKj6gzDVmCAPiJOjSuoL4aHkMgZDZD'
	#person = 'https://graph.facebook.com/v3.0/me/posts?access_token=' + facebook_token

	#posts = requests.get(person).json().get('data')
	#for post in posts:
		#sentence = post.get('message')
		#if sentence != None:
			#tweet_text.append(sentence)

	for tweet in tweepy.Cursor(api.user_timeline).items():
		tweet_text.append(tweet._json['text'])

	BOW = {}
	hashtag_list = []
	word_list = []
	http_list = []
	string_list = []
	for sentence in tweet_text:
		sentence = preprocess(sentence.lower())
		for word in sentence:
			ret_match = re.match('https?://\S+', word);
			if word.startswith('#'):
				hashtag_list.append(word)
			elif (ret_match):
				http_list.append(word)
			else:
				word = remove_non_ascii_2(word)
				if word not in string.punctuation:
					word_list.append(word)
	
	# WordNetLemmatizer.ensure_loaded()
	for word in word_list:
		word = lemmatizer.lemmatize(word)
		if word not in stop_words and word != ' ':
			BOW[word] = BOW.get(word, 0) + 1
		sorted(BOW.items(), key=lambda t: t[1], reverse=True)
	for word in BOW:
		string_item = {'text':word, 'size':BOW[word]}
		string_list.append(string_item)
	string_list.sort(key=lambda x: x['size'], reverse=True)
	Json_string_list = json.dumps(string_list)

	return render(request, 'wordcount.html', {'Json_string_list': Json_string_list})


def get_hashtag_list(request):
	user = request.user
	twitter_account = user.social_auth.get(provider='twitter')
	twitter_json = twitter_account.extra_data
	# retriev user timeline
	auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN,settings.TWITTER_SECRET)
	auth.set_access_token(twitter_json['access_token']['oauth_token'],twitter_json['access_token']['oauth_token_secret'])
	api = tweepy.API(auth)

	lemmatizer = WordNetLemmatizer()
	stop_words = set(stopwords.words('english'))
	tweet_text = []
	#facebook_token = 'EAACEdEose0cBAHr03FDFLi5mt6fXJZBB4eHehYMm41FXIyoZAmqSw4DicBzJVpRmXcecvdnGJgGAu2aghZAfuDRMZA8jnWfXNnCNPopMBW6GFzZCLS0M8Kt9ndEb5VZC3kEIasDXKBfXN2raZC38vzJ90DeuhnZC2znS1MSZBdaUVZAKoafNukRKj6gzDVmCAPiJOjSuoL4aHkMgZDZD'
	#person = 'https://graph.facebook.com/v3.0/me/posts?access_token=' + facebook_token

	#posts = requests.get(person).json().get('data')
	#for post in posts:
		#sentence = post.get('message')
		#if sentence != None:
			#tweet_text.append(sentence)

	for tweet in tweepy.Cursor(api.user_timeline).items():
		tweet_text.append(tweet._json['text'])
	BOW = {}
	hashtag_list = []
	word_list = []
	http_list = []
	string_list = []
	for sentence in tweet_text:
		sentence = preprocess(sentence.lower())
		for word in sentence:
			ret_match = re.match('https?://\S+', word);
			if word.startswith('#'):
				hashtag_list.append(word)
			elif (ret_match):
				http_list.append(word)
			else:
				word = remove_non_ascii_2(word)
				if word not in string.punctuation:
					word_list.append(word)

	for word in hashtag_list:
		word = lemmatizer.lemmatize(word)
		if word not in stop_words and word != ' ':
			BOW[word] = BOW.get(word, 0) + 1
		sorted(BOW.items(), key=lambda t: t[1], reverse=True)
	for word in BOW:
		string_item = {'text': word, 'count': BOW[word]}
		string_list.append(string_item)
		print(string_list)
	Json_string_list = json.dumps(string_list)
	return render(request, 'bubble.html', {'Json_string_list': Json_string_list})


def twitter_login(request):
    # step 1: send req token request to twitter
    resp, content = client.request(request_token_url, "POST")
    if resp['status'] != '200':
        raise Exception("Request token request fail.")

    # step 2: store req tokken in a session
    print("In Log in :")
    print(request.session.items())
    request_token = request.session['request_token'] = dict(urllib.parse.parse_qsl(content.decode("utf-8")))

    # #step 3: redirect to authentication url
    url = "%s?oauth_token=%s" % (authenticate_url, request.session['request_token']['oauth_token'])
    return HttpResponseRedirect(url)


@login_required
def twitter_logout(request):
    auth_logout(request)
    # redirect back to homepage
    return HttpResponseRedirect('/')


def twitter_authenticated(request):
    # step 1: use the oauth-token to build new client
    token = oauth.Token(request.session['request_token']['oauth_token'],
                        request.session['request_token']['oauth_token_secret'])
    token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)

    # step 2: request the access token from twitter
    resp, content = client.request(access_token_url, "POST")
    if resp['status'] != '200':
        print(content)
        raise Exception("Access token request fail")

    # step 3: store use id with screen name
    access_token = dict(urllib.parse.parse_qsl(content.decode("utf-8")))
    try:
        user = User.objects.get(username=access_token['screen_name'])
    except User.DoesNotExist:
        # creat user if not already exist
        user = User.objects.create_user(access_token['screen_name'], '%s@twitter.com' % access_token['screen_name'],
                                        password=access_token['oauth_token_secret'])
        print("After created")
        print(user)

        profile = Profile()
        profile.user = user
        profile.oauth_token = access_token['oauth_token']
        profile.oauth_secret = access_token['oauth_token_secret']
        profile.save()

    # step 4: authenticate user and log them in
    # auth_user = twt_authenticate(username=access_token['screen_name'],
    # password=access_token['oauth_token_secret'])
    twt_login(request, user, 'django.contrib.auth.backends.ModelBackend')

    # auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
    # auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
    # api = tweepy.API(auth)

    # for status in tweepy.Cursor(api.user_timeline, screen_name=access_token['screen_name']).items():
    # print(status._json['text'])

    return HttpResponseRedirect('/socialtracker/account')


# Password changed and go back to login
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


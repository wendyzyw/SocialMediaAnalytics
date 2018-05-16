# COMP90044 Distributed Computing Project
# Web-based mental analytics app on social media
# Author: Xin Wang, Yiwen Zeng, Yu Han, Chenxi Hou
# Created on: 03/2018

# Python Import
import oauth2 as oauth
import urllib.parse
import time
import simplejson
import tweepy
import requests
import facebook
from datetime import datetime

from nltk import WordNetLemmatizer
from watson_developer_cloud import PersonalityInsightsV3, NaturalLanguageUnderstandingV1, ToneAnalyzerV3
from watson_developer_cloud import WatsonApiException
from watson_developer_cloud.natural_language_understanding_v1 \
    import Features, KeywordsOptions, ConceptsOptions

# Django Import
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import logout as twt_logout, login as twt_login, update_session_auth_hash
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, \
    PasswordResetDoneView, PasswordChangeDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Social_Django Import
from social_django.models import UserSocialAuth

# App Import
from .forms import LoginForm, ChangepassForm, EdituserinfoForm, RegisterForm, MyPasswordResetForm

# from .models import UserInfo, TwitterProfile, FackbookProfile, GithubProfile


# app name
app_name = 'socialtracker'


# twitter login authentication
# consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
# client = oauth.Client(consumer)
#
# # step 1
# request_token_url = 'https://api.twitter.com/oauth/request_token'
# # step 2
# authenticate_url = 'https://api.twitter.com/oauth/authenticate'
# # step 3
# access_token_url = 'https://api.twitter.com/oauth/access_token'
#
#
# def twitter_login(request):
#     # step 1: send req token request to twitter
#     resp, content = client.request(request_token_url, "POST")
#     if resp['status'] != '200':
#         raise Exception("Request token request fail.")
#
#     # step 2: store req token in a session
#     print("In Log in :")
#     print(request.session.items())
#     request_token = request.session['request_token'] = dict(urllib.parse.parse_qsl(content.decode("utf-8")))
#
#     # #step 3: redirect to authentication url
#     url = "%s?oauth_token=%s" % (authenticate_url, request.session['request_token']['oauth_token'])
#     return HttpResponseRedirect(url)
#
#
@login_required(login_url='/socialtracker/')
def twitter_logout(request):
    print(request.session.items())
    twt_logout(request)
    # redirect back to homepage
    return HttpResponseRedirect('/socialtracker')


#
#
# def twitter_authenticated(request):
#     # step 1: use the oauth-token to build new client
#     token = oauth.Token(request.session['request_token']['oauth_token'],
#                         request.session['request_token']['oauth_token_secret'])
#     token.set_verifier(request.GET['oauth_verifier'])
#     client = oauth.Client(consumer, token)
#
#     # step 2: request the access token from twitter
#     resp, content = client.request(access_token_url, "POST")
#     if resp['status'] != '200':
#         print(content)
#         raise Exception("Access token request fail")
#
#     # step 3: store user id with screen name
#     access_token = dict(urllib.parse.parse_qsl(content.decode("utf-8")))
#     try:
#         user = User.objects.get(username=access_token['screen_name'])
#     except User.DoNotExist:
#         # creat user if not already exist
#         user = User.objects.create_user(access_token['screen_name'], '%s@twitter.com' % access_token['screen_name'],
#                                         password=access_token['oauth_token_secret'])
#         print("After created")
#         print(user)
#
#         profile = TwitterProfile()
#         profile.user = user
#         profile.t_token = access_token['oauth_token']
#         profile.t_secret = access_token['oauth_token_secret']
#         profile.save()
#
#     # step 4: authenticate user and log them in
#     # auth_user = twt_authenticate(username=access_token['screen_name'],
#     # password=access_token['oauth_token_secret'])
#     twt_login(request, user, 'django.contrib.auth.backends.ModelBackend')
#
#     # auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
#     # auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
#     # api = tweepy.API(auth)
#
#     # for status in tweepy.Cursor(api.user_timeline, screen_name=access_token['screen_name']).items():
#     # print(status._json['text'])
#
#     # return HttpResponseRedirect('/socialtracker/account')
#     return HttpResponseRedirect('/%s/account' % app_name)


# The main page.
def index(request):
    return render(request, 'index.html')


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


def login(request):
    if request.method == "POST":
        uf = LoginForm(request.POST)
        if uf.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                twt_login(request, user)
                request.session['username'] = user.username
                request.session['password'] = user.password
                request.session['first_name'] = user.first_name
                request.session['last_name'] = user.last_name
                request.session['email'] = user.email
                request.session['phone'] = user.phone
                request.session['city'] = user.city
                request.session['zip_code'] = user.zip_code
                request.session['address'] = user.address
                return render(request, 'account-home.html')
            else:
                return render(request, 'login.html',
                              {'uf': uf, 'message': 'username or password is not correct, please check or signup!'})
        else:
            return render(request, 'login.html', {'uf': uf,
                                                  'message': 'please fill in all the information or note the format of entered password!'})
    else:
        uf = LoginForm()
        return render(request, 'login.html', {'uf': uf})


@login_required(login_url='/socialtracker/')
def account(request):
    return render(request, 'account-home.html')


@login_required(login_url='/socialtracker/')
def manage1(request):
    if request.method == "POST":
        uf = ChangepassForm(request.POST)
        if uf.is_valid():
            username = request.session.get('username')
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


@login_required(login_url='/socialtracker/')
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
            username = request.session.get('username')
            User.objects.filter(username=username).update(first_name=first_name, last_name=last_name,
                                                          address=address, phone=phone, zip_code=zip_code,
                                                          gender=gender,
                                                          state=state, city=city)
            user = User.objects.get(username=username)
            request.session['username'] = user.username
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            request.session['phone'] = user.phone
            request.session['city'] = user.city
            request.session['zip_code'] = user.zip_code
            request.session['address'] = user.address
            return render(request, 'Manage2_Personal.html', {'uf': uf, 'message': 'success!'})
        else:
            return render(request, 'Manage2_Personal.html',
                          {'uf': uf, 'message': 'Please fill in all your information!'})
    else:
        uf = EdituserinfoForm()
        return render(request, 'Manage2_Personal.html', {'uf': uf})


@login_required(login_url='/socialtracker/')
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
        print('twitter_account = ', twitter_account)
        if twitter_account is not None:
            print(twitter_account)
            twitter_json = twitter_account.extra_data
            twitter_name = twitter_json['access_token']['screen_name']
            twitter_date = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(twitter_json['auth_time']))

    except UserSocialAuth.DoesNotExist:
        twitter_account = None
        print('twitter_account = ', twitter_account)

    try:
        facebook_account = user.social_auth.get(provider='facebook')
        if facebook_account is not None:
            facebook_json = facebook_account.extra_data
            facebook_date = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(facebook_json['auth_time']))
            facebook_id = facebook_json['id']
            # get image url
            fb_profile_url = url = "http://graph.facebook.com/%s/picture?type=large" % facebook_id

    except UserSocialAuth.DoesNotExist:
        facebook_account = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    # social_backend = request.session['social_auth_last_login_backend']
    # return render(request, 'Manage3_social.html',
    #               {'social_backend': social_backend, 'twitter_account': twitter_account, 'twitter_date': twitter_date,
    #                'twitter_name': twitter_name, 'facebook_account': facebook_account, 'facebook_date': facebook_date,
    #                'facebook_id': facebook_id, 'can_disconnect': can_disconnect})
    return render(request, 'Manage3_social.html',
                  {'twitter_account': twitter_account, 'twitter_date': twitter_date,
                   'twitter_name': twitter_name, 'facebook_account': facebook_account, 'facebook_date': facebook_date,
                   'facebook_id': facebook_id, 'can_disconnect': can_disconnect})


@login_required(login_url='/socialtracker/')
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'password.html', {'form': form})


# Enter email address to reset password
class MyPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    form_class = MyPasswordResetForm


# Email Sent
class MyPasswordResetDone(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


# Reset the password without requirement of the old password
class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'


# Password changed and go back to login
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

    ####################################################
    # This two views below are for changing password with requirement of old password.
    ####################################################

    # class MyPasswordChangeView(PasswordChangeView):
    # template_name = 'password_change.html'

    # class MyPasswordChangeDoneView(PasswordChangeDoneView):
    # template_name = 'password_reset_complete.html'


# main page for analysis
@login_required(login_url='/socialtracker/')
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
                        concepts=ConceptsOptions(
                            limit=10)))

            # print(json.dumps(response, indent=2))

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

    return render(request, 'data.html', {'radarData': radarData})


# sunburst user personality
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
        totalScore = trait1['raw_score'] + trait2['raw_score'] + trait3['raw_score'] + trait4['raw_score'] + trait5[
            'raw_score']
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
        onePersonality['children'].append(child1)
        onePersonality['children'].append(child2)
        onePersonality['children'].append(child3)
        onePersonality['children'].append(child4)
        onePersonality['children'].append(child5)
        sbData['children'].append(onePersonality)
        totalScore += eachPersonality['raw_score']

    sbData['children'][0]['percent'] = round(personality[0]['raw_score'] / totalScore, 4)
    sbData['children'][1]['percent'] = round(personality[1]['raw_score'] / totalScore, 4)
    sbData['children'][2]['percent'] = round(personality[2]['raw_score'] / totalScore, 4)
    sbData['children'][3]['percent'] = round(personality[3]['raw_score'] / totalScore, 4)
    sbData['children'][4]['percent'] = round(personality[4]['raw_score'] / totalScore, 4)

    return render(request, 'user_personality.html', {'sbData': sbData})


# radar chart for user values
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


# sentiment for key words
def keywords(request):
    return render(request, 'keywords.html')


# curve for tone analysis
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


# force directed graph for social network
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


# heat map for number of posts
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

    person = 'https://graph.facebook.com/v3.0/me/posts?access_token=' + facebook_token

    posts = requests.get(person).json().get('data')
    for post in posts:
        message = post.get('message')
        created_time = post.get('created_time')
        datetime_object = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+%f')

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

    return render(request, 'heatmap.html', {'heatmapData': heatmapData})


def get_hashtag_list(request):
    user = request.user
    twitter_account = user.social_auth.get(provider='twitter')
    twitter_json = twitter_account.extra_data
    # retriev user timeline
    auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
    auth.set_access_token(twitter_json['access_token']['oauth_token'],
                          twitter_json['access_token']['oauth_token_secret'])
    api = tweepy.API(auth)

    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tweet_text = []
    # facebook_token = 'EAACEdEose0cBAHr03FDFLi5mt6fXJZBB4eHehYMm41FXIyoZAmqSw4DicBzJVpRmXcecvdnGJgGAu2aghZAfuDRMZA8jnWfXNnCNPopMBW6GFzZCLS0M8Kt9ndEb5VZC3kEIasDXKBfXN2raZC38vzJ90DeuhnZC2znS1MSZBdaUVZAKoafNukRKj6gzDVmCAPiJOjSuoL4aHkMgZDZD'
    # person = 'https://graph.facebook.com/v3.0/me/posts?access_token=' + facebook_token

    # posts = requests.get(person).json().get('data')
    # for post in posts:
    # sentence = post.get('message')
    # if sentence != None:
    # tweet_text.append(sentence)

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
    Json_string_list = simplejson.dumps(string_list)
    return render(request, 'bubble.html', {'Json_string_list': Json_string_list})

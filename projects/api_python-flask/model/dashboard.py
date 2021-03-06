import json
import os
import pprint
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from pymongo import MongoClient 

class Dashboard(Resource):
    def post(self):
        db = None
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='')
            args = parser.parse_args()

            token = args['token'] if 'token' in args else None

            if (token == None):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            db = Database.connect()
            surveyData = db.survey.find_one({ 'token': token })

            if (surveyData == None):
                return {
                    'success' : False,
                    'message' : 'Survey does not exist'
                }, 404
            else:
                current_response_count = db.survey_response.count_documents({ 'survey_token': token })
                motivated_response_count = db.survey_response.count_documents({ 'survey_token': token, 'motivated': True })
                demotivated_reponse_count = db.survey_response.count_documents({ 'survey_token': token, 'motivated': False })

                latestReceivedResponseDate = db.survey_response.find_one({ 'survey_token': token }, { '_id': 0, 'created_at': 1 }, sort=[( 'created_at', -1 )])

                response_limit = surveyData['no_of_respondents']
                survey_expiration_date = surveyData['expires_at']

                mention_count_for_keyword = []
                keywordSelectionData = db.survey_settings.find_one({}, { '_id': 0, 'keywords_selection': 1 })

                for keywords_selection_option in keywordSelectionData['keywords_selection']:
                    keyword_result_motivated = db.survey_response.count_documents({ 
                        'survey_token': token,
                        'motivated': True,
                        'keywords': keywords_selection_option
                    })
                    keyword_result_demotivated = db.survey_response.count_documents({ 
                        'survey_token': token,
                        'motivated': False,
                        'keywords': keywords_selection_option
                    })
                    response_count_data = {
                        'keyword': keywords_selection_option,
                        'motivated': keyword_result_motivated,
                        'demotivated': keyword_result_demotivated
                    }
                    mention_count_for_keyword.append(response_count_data)

                data = {
                    'current_response_count': current_response_count,
                    'response_limit': response_limit,
                    'motivated_response_count': motivated_response_count,
                    'demotivated_response_count': demotivated_reponse_count,
                    'mention_count_for_keyword': mention_count_for_keyword,
                    'survey_expiration_date': str(survey_expiration_date)
                }

                if (latestReceivedResponseDate != None):
                    latestReceivedResponseDate = latestReceivedResponseDate['created_at']
                    data['latest_response_received_date'] = str(latestReceivedResponseDate)

                return {
                    'success': True,
                    'data': data
                }

        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()
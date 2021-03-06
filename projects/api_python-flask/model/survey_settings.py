import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from pymongo import MongoClient

class SurveySettings(Resource):
    def getNoOfRespondents(self):
        db = Database.connect()
        data = db.survey_settings.find_one({}, { '_id': 0, 'number_of_respondents': 1 })
        number_of_respondents_options = []
        for number_of_respondents_option in data['number_of_respondents']:
            number_of_respondents_options.append(int(number_of_respondents_option))
        return number_of_respondents_options

    def getKeywords(self):
        db = Database.connect()
        data = db.survey_settings.find_one({}, { '_id': 0, 'keywords_selection': 1 })
        keyword_options = []
        for keyword_selection in data['keywords_selection']:
            keyword_options.append(keyword_selection)
        return keyword_options
        
    def get(self):
        db = None
        setting_param_option_respondents = "respondents"
        setting_param_option_keywords = "keywords"
        setting_param_options = [setting_param_option_respondents, setting_param_option_keywords]
        try:
            setting = request.args.get('setting') if 'setting' in request.args else None

            if (setting == None):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (setting == setting_param_option_respondents):
                return {
                    'data': self.getNoOfRespondents()
                }

            elif (setting == setting_param_option_keywords):
                return {
                    'data': self.getKeywords()
                }
            
            else:
                return {
                    'success' : False,
                    'message' : '`setting` parameter does not have the proper value'
                }, 400
                

        except Exception as exception:
            return {'error': str(exception)}, 400
        finally:
            if type(db) == MongoClient:
                db.close()
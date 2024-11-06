import json, random
from Levenshtein import distance
from dotenv import load_dotenv, dotenv_values
from registrability.knowledge_graph import KnowledgeGraph 
import os
from concurrent.futures import ThreadPoolExecutor
from models import RegistrabilityRequest
import pprint
from classifier.endpoint import classifier_infer


from classifier.endpoint import registrability_mark_name

class FeatureParams:

    def __init__(self) -> None:
        pass

    def get_famous_marks(self,mark_name: str) -> tuple:

        mark_name = mark_name.lower()
        mark_name = mark_name.replace("d","b")
        mark_name = mark_name.replace("p","q")
        data = json.load(open("./json/trademark_data.json"))

        distances = []
        mark_name_list = mark_name.lower().split()

        for mark in mark_name_list:
            for item in data:
                item_distance = min(
                                distance(mark, item["trademark_name"].lower()),
                                distance(mark,item["trademark_name"].lower().replace("d","b").replace("p","q")),
                                ) / len(mark)
                distances.append(
                        {"mark": mark, "item": item, "distance": item_distance}
                    )
        
        sorted_distances = sorted(distances, key=lambda x: x["distance"])

        most_similar_trademarks = []
        zero_count = 0
        for data in sorted_distances:
        
            if data["distance"] < 0.334:
                if data["distance"] == 0:
                    zero_count += 1
                most_similar_trademarks.append(
                    {
                        "name": data["item"]["trademark_name"]# .("b", "d").replace("q", "p"),
                        
                    }
                )

        if len(most_similar_trademarks) == 0:
            return 1, most_similar_trademarks
        if zero_count == 0:
            return 0.5,most_similar_trademarks
        
        return 4 / (100* zero_count), most_similar_trademarks
    
    def get_famous_personality(self,trademark_name : str) -> tuple:

        try:
            print(trademark_name)
            data = trademark_name
            resp_dict = {}

            for i in data.split(" "):
                resp_dict[i] = KnowledgeGraph(i).run()
        except Exception as e:
            return something_went_wrong()
    
        marks = trademark_name.split()
        results = []
        total_cnt = 0

        for mark in marks:
            
            #__import__('pprint').pprint(resp_dict[mark])
    

            for item in resp_dict[mark]["itemListElement"]:
                #__import__('pprint').pprint(item)
                total_cnt +=1

                try:    
                    if "Person" in item["result"]["@type"]:
                    
                        results.append(item["result"]["name"])
                except:
                    pass
                    
    
        score = 1
        if len(results) > 4:
            score = 0
        elif len(results) >= 1 and len(results) <= 4:
            score = 0.25
        # elif len(results) == 0 and total_cnt > 0:
        #     score = 0.5
        else:
            score = 1
        
        return score, results
    

    def get_geographic_distinctiveness_and_genericness_score(self,request,no_of_classes):

        try:
            mark_name = request
            response = registrability_mark_name(mark_name)
        
        except Exception as e:
            return e
        
        expected_classes = no_of_classes
        results = {}
        
        results["geo_sequences"] = response["geo_sequences"]
    
        if(len(response["geo_sequences"])) > 0:
            results["geographic_distinctiveness"] = 0
        else:
            results["geographic_distinctiveness"] = 1
        
        res = response["generic_terms"]
        
        if len(res) == 0:
            return 1
        
        label_cnt = 0

        generic_words = []
        for item in res:
            data = res[item]
            if (
                (data["label"] == "RB")
                or (data["label"] == "JJ")
                or (data["label"][0] == "V")
            ):
                generic_words.append(item)
                label_cnt += 1

        if label_cnt == 0:
            class_cnt = 0
            for item in res:
                data = res[item]["scores"]
                try:
                    for x in data:
                        if x["class_id"] in expected_classes:
                            generic_words.append(item)
                            class_cnt += 1
                except:
                    pass

            results["genericness"] = 1 - class_cnt / len(res)

        results["genericness"] = 1 - label_cnt / len(res)
        results["generic_words"] = generic_words
        return results

    @staticmethod
    def get_merely_descriptive(mark_name, expected_classes, description):

        class_words_dict = {}
        generated_classes = []

        for word in mark_name.lower().split():
            _classes = [x["class_id"] for x in classifier_infer(word)]
            for _class in _classes:
                class_words_dict[_class] = list(
                    set(class_words_dict.get(_class, []) + [word])
                )
            generated_classes.extend(_classes)

        generated_classes = list(set(generated_classes))

        affecting_words = []
        cnt = 0
        for _class in expected_classes:
            if _class in generated_classes:
                affecting_words.extend(class_words_dict[_class])
                cnt += 1

        return {
            "score": 1 - (cnt / len(expected_classes)),
            "words": list(set(affecting_words)),
        }




                

    def  registrability_params(self,request: RegistrabilityRequest):
        mark_name = request.mark_name
        description = request.description
        selected_classes = request.selected_classes
      
        with ThreadPoolExecutor(max_workers=3) as exector:
            t1 = exector.submit(self.get_famous_marks, mark_name)
            t2 = exector.submit(self.get_famous_personality, request.request)
            t3 = exector.submit(self.get_geographic_distinctiveness_and_genericness_score,request.request,request.selected_classes)
            t4 = exector.submit(self.get_merely_descriptive,mark_name,selected_classes,description)

        famous_marks, famous_mark_list = t1.result()
        interim = t2.result()
        famous_personality, famous_personality_list = interim
        genericness = t3.result()["genericness"]
        geographic_distinctiveness = t3.result()
        merely_descriptive = t4.result()     

        
        results = {
            "metric":{
                "famous_marks_score" : famous_marks,
                "genericness": genericness,
                "merely_descriptive": merely_descriptive["score"],
                "famous_personality": famous_personality,
                "geographic_distinctiveness": geographic_distinctiveness[
                    "geographic_distinctiveness"
                ],
                
             
            },
            "meta":{
                "famous_marks": famous_mark_list,
                "famous_personality": list(set(famous_personality_list)),
                "geo_sequences": geographic_distinctiveness["geo_sequences"],
                "merely_descriptive": merely_descriptive["words"],
                "generic_words": geographic_distinctiveness["generic_words"],
            }
        }

        return results




if __name__ == '__main__':
   feature_params = FeatureParams() 
   score, result  = feature_params.get_famous_personality("Gucci")
   

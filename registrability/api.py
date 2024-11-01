import json, random
from Levenshtein import distance
from dotenv import load_dotenv, dotenv_values
from registrability.knowledge_graph import KnowledgeGraph 
import os
from concurrent.futures import ThreadPoolExecutor
from models import RegistrabilityRequest
from classifier import registrability_mark_name

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
    
    def get_famous_personality(slef,trademark_name : str) -> tuple:

        try:
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
           
            for item in resp_dict[mark]["itemListElement"]:
    
                total_cnt +=1

                try:
                    if "Person" in item["result"]["@type"] and mark.lower() in [
                        x.lower()
                        for x in re.sub(r"[:,.-]", "", item["result"]["name"]).split(
                            " "
                        )
                    ]:
                        print(item["result"]["names"])
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
            return something_went_wrong()
        
        expected_classes = no_of_classes
        results = {}
        results["geo_sequences"] = response.data.get("expected_classes")

        if(len(response["geo_sequence"])) > 0:
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


                

    def  registrability_params(self,request: RegistrabilityRequest):
        mark_name = request.mark_name
        description = request.description
        selected_classes = request.selected_classes
      
        with ThreadPoolExecutor(max_workers=3) as exector:
            t1 = exector.submit(self.get_famous_marks, mark_name)
            t2 = exector.submit(self.get_famous_personality, request.request)
            t3 = exector.submit(self.get_geographic_distinctiveness_and_genericness_score,request.request,request.selected_classes)

        famous_marks, famous_mark_list = t1.result()
        interim = t2.result()
        famous_personality, famous_personality_list = interim
        merely_descriptive = t3.result()

        results = {
            "metric":{
                "famous_marks_score" : famous_marks,
                "famous_marks_list" : famous_mark_list,
                "famous_personality_score": famous_personality,
                "famous_personality_list" : famous_personality_list,
                "merely_descriptive": merely_descriptive["score"],
            }
        }

        return results




if __name__ == '__main__':
   feature_params = FeatureParams() 
   score, result  = feature_params.get_famous_personality("Gucci")
   

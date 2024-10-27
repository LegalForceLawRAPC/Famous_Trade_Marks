import json, random
from Levenshtein import distance

def get_famous_marks(mark_name: str):

    mark_name = mark_name.lower()
    mark_name = mark_name.replace("d","b")
    mark_name = mark_name.replace("p","q")
    data = json.load(open("../json/trademark_data.json"))

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

    print(most_similar_trademarks)
            




if __name__ == '__main__':
   get_famous_marks("")
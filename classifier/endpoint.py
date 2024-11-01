from typing import OrderedDict
from utils.ai_sagemaker_connector import query_ai_webservice

def decompose(sentence: str):
    return query_ai_webservice(
        {"model_name": "flair_pos_tagger", "model_input": {"text": sentence}}
    )


def classifier_infer(infer_str: str):
    return query_ai_webservice(
        {
            "model_name": "distilbert_classifier",
            "model_input": {"text": infer_str, "filter_topk": True, "topk": 3},
        }
    )
    

def registrability_mark_name(infer_str: str):
    """
    Accepts an input string and decomposes it into words and runs classifier individually
    """

    nltk_out = decompose(infer_str)

    tokens = [x[0] for x in nltk_out]
    labels = [x[1] for x in nltk_out]

    registrability = dict()

    final_output = OrderedDict()
    for i, token in enumerate(tokens):
        if labels[i] in ["NN", "NNS", "NNP", "JJ", "JJR", "JJS"]:
            infer_out = classifier_infer(token)

            final_output[token] = {"scores": infer_out, "label": labels[i]}
        else:
            final_output[token] = {"scores": None, "label": labels[i]}

    registrability["generic_terms"] = final_output

    geo_sequences = []

    for window_length in range(1, 3):
        if window_length > len(tokens):
            break
        for i in range(len(tokens) - window_length + 1):
            sequence = " ".join(tokens[i : i + window_length])
            # print(sequence)
            if sequence.lower() in geo_names:
                geo_sequences.append(sequence)
        # if len(geo_sequences)>0 :
        #    break

    surname_snippets = []
    for token in tokens:
        if token.lower() in surnames:
            surname_snippets.append(token)

    registrability["geo_sequences"] = geo_sequences
    registrability["surnames_sequences"] = surname_snippets

    return registrability
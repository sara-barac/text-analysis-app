from pathlib import Path
from typing import Iterable
import spacy
import pandas as pd
import numpy as np  


#funkcije za učitavanje spacy modela, sa opcijom isključivanja komponenti zarad neopterećivanja radne memorije
def load_nlp_small(model: str, disable: list[str] | None = None):
    return spacy.load(model, disable=disable or [])

def load_nlp_medium(model: str, disable: list[str] | None = None):
    return spacy.load(model, disable=disable or [])


#----funkcija za učitavanje excel fajlova iz input direktorijuma -----
# rezultat funkcije: path pojedinacnog fajla odakle je izvlačen tekst i sam tekst sa odgovarajućim naslovima

def iter_excels(input_dir: Path) -> Iterable[tuple[Path, pd.DataFrame]]:
    for p in sorted(Path(input_dir).glob('*.xlsx')):
        try:
            df = pd.read_excel(p, engine = 'openpyxl', header = 1, usecols= ['title', 'context'])

            #uklanjanje duplikata u koloni context, tako da se svaki deo konteksta pojavljuje samo 
            #jednom, gde se njemu odgovarajući naslov nalazi u koloni "title", nužno ponovljen
            df = df.drop_duplicates(subset=['context'])

        except Exception as e:
            print(f'Error reading {p}: {e}')
            continue 
        yield p, df


#----funkcija za spajanje svih tekstova u objedinjeni DataFrame -----
# rezultat funkcije: jedan  DataFrame sa svim naslovima i kontekstima iz svih fajlova

def gather_doc(gen: Iterable[tuple[Path, pd.DataFrame]]) -> pd.DataFrame:
    
    dfss = [df for (_, df) in gen]   #uzimamo pojedinačni DataFrame za svaki fajl iz objekta-generatora, rezultata prethodne funkcije
    big_df = pd.concat(dfss, ignore_index=True)
    return big_df


#----funkcija za razdvajanje tema i njima odgovarajućih tekstova-----
# rezultat funkcije:  jedan rečnik gde su ključevi naslovi, a vrednosti ključeva konkateniran sav 
# jedinstveni tekst koji se odnosi na taj naslov

def separate_topics (df: pd.DataFrame) -> dict[str, str]:
    
    topics_list = set(df['title'].tolist())

    dict_of_texts = {}

    for topic in topics_list:
        conc_contx = df.loc[df['title'] == topic, 'context'].tolist()

        dict_of_texts[topic] = ' '.join(conc_contx)

    return dict_of_texts



#----funkcija za analizu rečnika tekstova po temama-----
# rezultat funkcije: rečnik gde su ključevi naslovi tekstova, a vrednosti rečnici (1)tokena u tekstu i njihov broj, (2)frekvencijski rečnik vrsta reči u tekstu, 
# (3) Type-Token Ratio (TTR) vrednost za dati tekst
def analyze_docs(docs: dict[str, str], nlp) -> dict[str, list]:

    dict_of_tokens = {}
    dict_of_pos = {}
    ttr = {}
    final_analyzed_dict = {}


    for key, value in docs.items():
        doc = nlp(value)
        #izdvajanje tokena koji nisu stop reči ili znaci interpunkcije
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        #tipovi u svakom tekstu
        types = set(tokens)
        dict_of_tokens[key] = tokens

        ttr_value = len(types) / len(tokens) if len(tokens) > 0 else 0
        ttr[key] = ttr_value

        #frekvencijski recnik vrsta reči u svakom tekstu
        pos_counts = {}
        for t in doc:
            pos_counts[t.pos_] = pos_counts.get(t.pos_, 0) + 1

        dict_of_pos[key] = pos_counts

        final_analyzed_dict[key] = {
            
            'num_tokens' : len(tokens),
            'tokens' : tokens, 
            'ttr' : ttr_value,
            'pos_counts' : pos_counts
        }

    return final_analyzed_dict


#----funkcija za izvlačenje imenovanih entiteta iz rečnika [naslov: tekst]-----
#rezultat funkcije: rečnik gde su ključevi naslovi, odnosno teme, a vrednosti rečnici imenovanih entiteta oblika  [tip entiteta: lista pojedinačnih javljenih entiteta]

def entity_analysis(docs: dict[str, str], nlp) -> dict[str, dict[str, list[str]]]:

    entities_results = {}

    for key, value in docs.items():
        doc = nlp(value)
        entities= [(ent.label_, ent.text) for ent in doc.ents]

        entity_dict = {}

        for label, text in entities:
            entity_dict.setdefault(label, []).append(text)

        #uklanjanje duplikata iz listi entitera za svaki tip entiteta
        for label in entity_dict:
            entity_dict[label] = list(set(entity_dict[label]))

        entities_results[key] = entity_dict

    return entities_results


#----funkcija za računanje vektorske sličnosti među tekstovima-----
#rezultat funkcije: DataFrame sa matricom vektorske sličnosti među tekstovima, DataFrame sa najvišom i najnižom sličnošću

def text_similarity_matrix(docs: dict[str, str], nlp) -> tuple[pd.DataFrame, pd.DataFrame]:
        
    docs = {topic: nlp(text) for topic, text in docs.items()}


    topics = list(docs.keys())
    similarity_matrix = pd.DataFrame(index=topics, columns=topics, dtype=float)

    for t1, doc1 in docs.items():
        for t2, doc2 in docs.items():
            similarity_matrix.loc[t1, t2] = doc1.similarity(doc2)

    # isključivanje vrednosti glavne dijagonale matrice kako bi se našle granične vrednosti
    stacked = similarity_matrix.where(~np.eye(len(similarity_matrix), dtype=bool)).stack()
    most_similar_pair = stacked.idxmax()
    highest_score = stacked.max()
    least_similar_pair = stacked.idxmin()
    lowest_score = stacked.min()

    #kreiranje DataFrame-a sa najvišom i najnižom sličnosti
    summary_df = pd.DataFrame({
        "Most similar pair": [f"{most_similar_pair}"],
        "Highest score": [highest_score],
        "Least similar pair": [f"{least_similar_pair}"],
        "Lowest score": [lowest_score]
    })

    return similarity_matrix, summary_df





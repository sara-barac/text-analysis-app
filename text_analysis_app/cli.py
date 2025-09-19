import typer
import yaml
from pathlib import Path
import pandas as pd
import json

# uvoz funkcija iz skripte za analizu teksta
from .processing import (
    load_nlp_small, 
    load_nlp_medium, 
    iter_excels,
    gather_doc,
    separate_topics,
    analyze_docs,
    entity_analysis,
    text_similarity_matrix
)



app = typer.Typer()

@app.command()
def process(config: str = "conf/config.yaml"):
    #ucitavanje konfiguracionog fajla sa informacijama o ulaznom, izlaznom folderu i spacy modelima
    cfg = yaml.safe_load(Path(config).read_text(encoding="utf-8"))

    #pozivanje spacy modela, dveju veličina spram različitih upotreba u različitim funkcijama 
    nlp_small = load_nlp_small(cfg["spacy_model_small"])
    nlp_medium = load_nlp_medium(cfg["spacy_model_medium"])
    
    #kreiranje putanja-objekata ka folderu sa ulaznim podacima i onom gde se pohranjuju rezultati analize
    input_dir = Path(cfg["input_dir"])
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    

    #pozivanje funkcija za obradu i analizu teksta
    gen = iter_excels(input_dir)
    big_df = gather_doc(gen)
    dict_of_texts = separate_topics(big_df)
    final_analyzed_dict = analyze_docs(dict_of_texts, nlp_small)

    #kreiranje prvog izlaznog fajla: osnovna analiza teksta (broj tokena, vrsta reči, TTR)
    out_file_first = output_dir / "basic_data_analysis.json"
    with out_file_first.open("w", encoding="utf-8") as f:
        json.dump(final_analyzed_dict, f, ensure_ascii=False, indent=2)

    typer.echo(f"✅ Analysis saved to {out_file_first}")

    #kreiranje drugog izlaznog fajla: analiza imenovanih entiteta

    entities = entity_analysis(dict_of_texts, nlp_medium)
    out_file_entities = output_dir / "entity_analysis.json"
    with out_file_entities.open('w', encoding = 'utf-8') as f:
        json.dump(entities, f , ensure_ascii=False, indent=2)

    typer.echo(f"✅ Entity analysis saved to {out_file_entities}")

    #kreiranje trećeg izlaznog fajla: matrica vektorske sličnosti među tekstovima, ovoga puta u excel formatu

    sim_matrix, summary_df = text_similarity_matrix(dict_of_texts, nlp_medium)
    sim_out = output_dir / "similarity_matrix.xlsx"
    with pd.ExcelWriter(sim_out, engine="openpyxl") as writer:
        sim_matrix.to_excel(writer, sheet_name="Similarity_Matrix")
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    typer.echo(f"✅ Similarity results saved to {sim_out}")


if __name__ == "__main__":
    app()


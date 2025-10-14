import os
import json
import argparse


def research_background_to_json(research_background_file_path):
    # YOUR RESEARCH QUESTION HERE
    research_question = \
'''
How can we build a generative model based on Wyckoff positions that will faithfully reproduce the distribution of symmetry space groups and outperform the SOTA models in terms of stability, uniqueness, and novelty?
'''

    # YOUR BACKGROUND SURVEY HERE
    background_survey = \
'''
1. SOTA diffusion models for solid state materials produce an abnormally high fraction of materials lacking symmetry. In the MP-20 dataset more than 98% of materials  have internal symmetry, while only ~70% produced by DiffCSP & FlowMM do.
2. Most atoms in stable materials occupy special Wyckoff positions, allowing encoding the crystal structure based on Wyckoff positions.
3. Wyckoff positions are discrete, and can be represented as categorical variables.
4. Existing generative models based on Wyckoff positions underperform the SOTA models in terms of stability, uniqueness, and novelty.
5. Existing generative models based on Wyckoff positions build their representation using Wyckoff letters and don't take into account the possible existence of multiple equvalent Wyckoff representations for the same crystal structure.
'''

    # Save the research question and background survey to a JSON file
    with open(research_background_file_path, "w", encoding="utf-8") as f:
        json.dump([research_question.strip(), background_survey.strip()], f, indent=4)
    print("Research background saved to", research_background_file_path)


def write_hypothesis_to_txt(eval_file_path, output_dir):
    # Load the JSON file
    with open(eval_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    research_question = list(data[0].keys())[0]

    with open(output_dir, "w", encoding="utf-8") as f:
        for cur_id in range(len(data[0][research_question])):
            cur_hypothesis = data[0][research_question][cur_id][0]
            cur_score = data[0][research_question][cur_id][1]
            f.write("Hypothesis ID: " + str(cur_id) + "\n")
            f.write("Averaged Score: " + str(cur_score) + "; ")
            f.write("Scores: " + str(data[0][research_question][cur_id][2]) + "\n")
            f.write("Number of rounds: " + str(data[0][research_question][cur_id][4]) + "\n")
            f.write(cur_hypothesis + "\n")
            f.write("\n\n")
    # print("len(data):", len(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--io_type", type=int, default=1, help="0: dumping input to json for MOOSE-Chem to load; 1: displaying output to txt for human reading")
    parser.add_argument("--custom_research_background_path", type=str, default="./custom_research_background.json", help="the path to the research background file. The format is [research question, background survey], and saved in a json file. ")
    parser.add_argument("--evaluate_output_dir", type=str, default="./Checkpoints/evaluation_GPT4o-mini_updated_prompt_apr_14.json", help="the path to the output file of evaluate.py")
    parser.add_argument("--display_dir", type=str, default="./hypothesis.txt", help="the path to the output file for displaying the hypothesis to human readers")
    args = parser.parse_args()

    assert args.io_type in [0, 1], "args.io_type should be either 0 or 1"

    if args.io_type == 0:
        research_background_to_json(args.custom_research_background_path)
    elif args.io_type == 1:
        assert os.path.exists(args.evaluate_output_dir), "The evaluate output file does not exist."
        write_hypothesis_to_txt(args.evaluate_output_dir, args.display_dir)
    else:
        raise ValueError("args.io_type should be either 0 or 1")


if __name__ == "__main__":
    main()
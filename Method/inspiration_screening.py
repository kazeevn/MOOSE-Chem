import os, sys, argparse, json, builtins
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from openai import OpenAI, AzureOpenAI
from google import genai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Method.utils import instruction_prompts, load_chem_annotation, organize_raw_inspirations, load_dict_title_2_abstract, recover_generated_title_to_exact_version_of_title, llm_generation_structured, exchange_order_in_list


class Inspiration(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(..., description="Title of the inspiration paper")
    reason: str = Field(..., description="Reason for selecting this paper")

class SelectedInspirations(BaseModel):
    inspirations: list[Inspiration] = Field(
        default_factory=list,
        description="List of selected inspiration papers"
    )


# Coarse grained inspiration screening
class Screening(object):
    # custom_rq (text) and custom_bs (text) are used when the user has their own research question and background survey to work on (but not those in the Tomato-Chem benchmark), and leverage MOOSE-Chem for inference
    def __init__(self, args, custom_rq=None, custom_bs=None):
        self.args = args
        self.custom_rq = custom_rq
        self.custom_bs = custom_bs
        ## Set API client
        # openai client
        if args.api_type == 0:
            self.client = OpenAI(api_key=args.api_key, base_url=args.base_url)
        # azure client
        elif args.api_type == 1:
            self.client = AzureOpenAI(
                azure_endpoint = args.base_url,
                api_key=args.api_key,
                api_version="2024-06-01"
            )
        elif args.api_type == 2:
            self.client = genai.Client(api_key=args.api_key)
        else:
            raise NotImplementedError
        ## Load research background: Use the research question and background survey in Tomato-Chem or the custom ones from input
        if custom_rq is None and custom_bs is None:
            # annotated bkg research question and its annotated groundtruth inspiration paper titles
            self.bkg_q_list, self.dict_bkg2insp, self.dict_bkg2survey, self.dict_bkg2groundtruthHyp, self.dict_bkg2note, \
                self.dict_bkg2idx, self.dict_idx2bkg, self.dict_bkg2reasoningprocess = load_chem_annotation(
                    args.chem_annotation_path, self.args.if_use_strict_survey_question, self.args.if_use_background_survey)
        else:
            print("INFO: Using custom_rq and custom_bs.")
            assert custom_rq is not None
            self.bkg_q_list = [custom_rq]
            self.dict_bkg2survey = {custom_rq: custom_bs}
            self.dict_idx2bkg = {0: custom_rq} 
        ## Load inspiration corpus (by default is the groundtruth inspiration papers and random high-quality papers)
        # title_abstract_collector: [[title, abstract], ...]
        # dict_title_2_abstract: {'title': 'abstract', ...}
        self.title_abstract_collector, self.dict_title_2_abstract = load_dict_title_2_abstract(
            title_abstract_collector_path=args.custom_inspiration_corpus_path)


    # The main function to run coarse-grained inspiration screening. Multiple rounds of screening for each background research question supported.
    def run(self):
        # Dict_bkg_q_2_screen_results: {'bq': [screen_results_round1, screen_results_round2, ...], ...}
        Dict_bkg_q_2_screen_results = {}
        # Dict_bkg_q_2_ratio_hit: {'bq': [ratio_hit_round1, ratio_hit_round2, ...], ...}
        # ratio_hit_round1/2/..: [ratio_hit_in_top1, ratio_hit_in_top3]
        Dict_bkg_q_2_ratio_hit = {}
        # initialize Screening
        full_bkg_questions = self.bkg_q_list
        # looping around research backgrounds to find coarse-grained inspirations
        for cur_bkg_q_id, cur_bkg_q in enumerate(full_bkg_questions):
            if self.args.background_question_id not in (-1, cur_bkg_q_id):
                continue
            print(f"\nID: {cur_bkg_q_id}; bkg_q: {cur_bkg_q}")
            # screen_results for multiple rounds
            for cur_screen_round in range(self.args.num_round_of_screening):
                if cur_screen_round == 0:
                    # first round of screening, inspiration_candidates are the full inspirations corpus
                    cur_next_round_inspiration_candidates = self.title_abstract_collector
                print(f"\nScreening Round: {cur_screen_round}; Number of inspiration candidates: {len(cur_next_round_inspiration_candidates)}")
                screen_results, cur_next_round_inspiration_candidates = self.one_round_screening(cur_bkg_q, cur_next_round_inspiration_candidates)
                print(f"Screening Round: {cur_screen_round}; len(screen_results): {len(screen_results)}")
                # ratio_hit: [ratio_hit_in_top1, ratio_hit_in_top3]
                # when using custom_rq, we don't know the groundtruth insp to check ratio hit
                if self.custom_rq is None:
                    ratio_hit = self.check_how_many_hit_groundtruth_insp(cur_bkg_q, screen_results)
                if cur_screen_round == 0:
                    assert cur_bkg_q not in Dict_bkg_q_2_screen_results
                    assert cur_bkg_q not in Dict_bkg_q_2_ratio_hit
                    Dict_bkg_q_2_screen_results[cur_bkg_q] = [screen_results]
                    if self.custom_rq is None:
                        Dict_bkg_q_2_ratio_hit[cur_bkg_q] = [ratio_hit]
                else:
                    Dict_bkg_q_2_screen_results[cur_bkg_q].append(screen_results)
                    if self.custom_rq is None:
                        Dict_bkg_q_2_ratio_hit[cur_bkg_q].append(ratio_hit)
                
        # organize raw inspirations
        # Dict_bkg_q_2_screen_results: {'bq': [screen_results_round1, screen_results_round2, ...], ...}
        #   screen_results_round1: [[[title, reason], [title, reason]], [[title, reason], [title, reason]], ...]
        # organized_Dict_bkg_q_2_screen_results: {'bq': [screen_results_round1_org, screen_results_round2_org, ...]}
        #   screen_results_round1_org: [[title, reason], [title, reason], ...]
        organized_Dict_bkg_q_2_screen_results = organize_raw_inspirations(Dict_bkg_q_2_screen_results)
        
        # save files
        if self.args.if_save:
            with open(self.args.output_dir, 'w') as f:
                json.dump([organized_Dict_bkg_q_2_screen_results, Dict_bkg_q_2_ratio_hit], f)
            print("\nSaved to: ", self.args.output_dir)
        else:
            print("\nNot saved.")


    ## Function
    #   one round of screening, select args.num_screening_keep_size inspiration papers from args.num_screening_window_size inspiration candidates
    ## Input
    #   bkg_research_question: background research question (text)
    #   inspiration_candidates: inspiration corpus to select matched ones with the background: [[title, abstract], [title, abstract], ...]
    ## Output
    #   screen_results: [[[title, reason], [title, reason]], [[], []], ...]
    #   next_round_inspiration_candidates: [[title, abstract], [title, abstract], ...]
    def one_round_screening(self, bkg_research_question, inspiration_candidates=None):
        # when self.custom_rq is not None, we don't need to check this (and also we won't initialize self.dict_bkg2insp)
        if self.custom_rq is None:
            assert bkg_research_question in self.dict_bkg2insp
        # backgroud_survey
        backgroud_survey = self.dict_bkg2survey[bkg_research_question]
        # print("Current background research question: ", bkg_research_question)
        # get instruction prompts
        if self.args.if_select_based_on_similarity == 0:
            prompts = instruction_prompts("first_round_inspiration_screening")
        elif self.args.if_select_based_on_similarity == 1:
            print("Warning: We are using semantic similarity to select inspirations.")
            prompts = instruction_prompts("first_round_inspiration_screening_only_based_on_semantic_similarity")
        else:
            raise NotImplementedError
        assert len(prompts) == 4
        # screen_results
        screen_results = []
        # next_round_inspiration_candidates: [[title, abstract], [title, abstract], ...], the ones that are selected this round, to be used to more fine-grained screening in the next round
        next_round_inspiration_candidates = []
        # select title_abstract for screening: [start_id, end_id) (not including end_id); start_id starts from id: 0 every time use self.one_round_screening()
        start_id = 0
        end_id = min(start_id + self.args.num_screening_window_size, len(inspiration_candidates))
        # begin screening loop
        while start_id < len(inspiration_candidates):
            print(f"start_id: {start_id}; end_id: {end_id}")
            # select title_abstract pairs for screening
            cur_title_abstract_pairs = inspiration_candidates[start_id:end_id]
            if len(cur_title_abstract_pairs) > self.args.num_screening_keep_size:
                # transfer selected title_abstract pairs to prompt
                cur_title_abstract_pairs_prompt = ""
                for cur_ta_id, cur_ta in enumerate(cur_title_abstract_pairs):
                    cur_ta_prompt = f"Next we will introduce inspiration candidate {cur_ta_id}. Title: {cur_ta[0]}; Abstract: {cur_ta[1]}. The introduction of inspiration candidate {cur_ta_id} has come to an end.\n"
                    cur_title_abstract_pairs_prompt += cur_ta_prompt
                # add instruction prompts
                full_prompt = prompts[0] + bkg_research_question + prompts[1] + backgroud_survey + prompts[2] + cur_title_abstract_pairs_prompt + prompts[3]
                # cur_structured_gene: [[Title, Reason], [Title, Reason], ...]
                # Use zero temperature to escavate heuristics in the model the most
                cur_structured_gene = llm_generation_structured(full_prompt, self.args.model_name, self.client, template=SelectedInspirations,
                    temperature=0, api_type=self.args.api_type)
                # cur_structured_gene = exchange_order_in_list(cur_structured_gene)
                for cur_selected_insp_id, cur_selected_insp in enumerate(cur_structured_gene.inspirations):
                    # here the cur_selected_insp_title should have been recovered to the exact version of title
                    cur_selected_insp_title = recover_generated_title_to_exact_version_of_title(
                        list(self.dict_title_2_abstract.keys()), cur_selected_insp.title)
                    cur_selected_insp_abstract = self.dict_title_2_abstract[cur_selected_insp.title]
                    next_round_inspiration_candidates.append([cur_selected_insp_title, cur_selected_insp_abstract])
                    # update cur_selected_insp to the exact version of title
                    cur_structured_gene.inspirations[cur_selected_insp_id].title = cur_selected_insp_title
            else:
                cur_structured_gene = [[cur_title_abstract_pairs[cur_ta_id][0], "Less than num_screening_keep_size, so keep them without screening."] for cur_ta_id in range(len(cur_title_abstract_pairs))]
            # update next_round_inspiration_candidates
            # update screen_results: now the cur_structured_gene uses the exact version of title
            if isinstance(cur_structured_gene, SelectedInspirations):
                screen_results.append(
                    [[cur_structured_gene.title, cur_structured_gene.reason] for cur_structured_gene in cur_structured_gene.inspirations])
            else:
                screen_results.append(cur_structured_gene)
            # update start_id & end_id
            start_id = end_id
            end_id = min(start_id + self.args.num_screening_window_size, len(inspiration_candidates))
        print(screen_results)
        print(next_round_inspiration_candidates)
        return screen_results, next_round_inspiration_candidates


    # obtain ratio_hit_in_top1 and ratio_hit_in_top3
    def check_how_many_hit_groundtruth_insp(self, bkg_research_question, screen_results):
        all_extracted_titles = []
        top1_extracted_titles = []
        # obtain all_extracted_titles and top1_extracted_titles
        for cur_sr in screen_results:
            for cur_extracted_insp_id, cur_extracted_insp in enumerate(cur_sr):
                cur_extracted_insp_title = cur_extracted_insp[0]
                # here the cur_extracted_insp_title should have been recovered to the exact version of title
                cur_extracted_insp_title = recover_generated_title_to_exact_version_of_title(list(self.dict_title_2_abstract.keys()), cur_extracted_insp_title)
                all_extracted_titles.append(cur_extracted_insp_title)
                if cur_extracted_insp_id == 0:
                    top1_extracted_titles.append(cur_extracted_insp_title)
        # check whether the groundtruth title is in the extracted titles
        gdth_insp = self.dict_bkg2insp[bkg_research_question]
        # recover the groundtruth inspirations to the exact version of title (the ones in title_abstract.json, even chem_research_2024.xlsx is not counted as groundtruth here, since title_abstract.json might have conflicts with chem_research_2024.xlsx, and title_abstract.json is more complete, so we choose title_abstract.json as the groundtruth, although chem_research_2024.xlsx is our benchmark and title_abstract.json is only a processed intermediate file) 
        gdth_insp = [recover_generated_title_to_exact_version_of_title(list(self.dict_title_2_abstract.keys()), cur_gdth_insp) for cur_gdth_insp in gdth_insp]
        # print("gdth_insp: ", gdth_insp)
        # The groundtruth inspirations collected so far all have more than or equal with 1 items
        assert len(gdth_insp) >= 1

        # print("all_extracted_titles: ", all_extracted_titles)
        hit_in_top1, hit_in_top3 = 0, 0
        for cur_gdth_insp in gdth_insp:
            if cur_gdth_insp in top1_extracted_titles:
                hit_in_top1 += 1
                hit_in_top3 += 1
            elif cur_gdth_insp in all_extracted_titles:
                hit_in_top3 += 1
            
            if cur_gdth_insp in all_extracted_titles:
                index_cur_gdth_insp = all_extracted_titles.index(cur_gdth_insp)
                print(f"index_cur_gdth_insp: {index_cur_gdth_insp}; insp title: {cur_gdth_insp}")
        # ratio_hit_in_top1 & ratio_hit_in_top3
        ratio_hit_in_top1 = hit_in_top1 / len(gdth_insp)
        ratio_hit_in_top3 = hit_in_top3 / len(gdth_insp)
        print(f"len(gdth_insp): {len(gdth_insp)}; len(all_extracted_titles): {len(all_extracted_titles)}; ratio_hit_in_top1: {ratio_hit_in_top1}; ratio_hit_in_top3: {ratio_hit_in_top3}")
        return [ratio_hit_in_top1, ratio_hit_in_top3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="chatgpt", help="model name: gpt4/chatgpt/chatgpt16k/claude35S/gemini15P/llama318b/llama3170b/llama31405b")
    parser.add_argument("--api_type", type=int, default=1, help="0: openai's API toolkit; 1: azure's API toolkit")
    parser.add_argument("--api_key", type=str, default="")
    parser.add_argument("--base_url", type=str, default="https://api.claudeshop.top/v1", help="base url for the API")
    parser.add_argument("--num_screening_window_size", type=int, default=10,
        help="How many abstract to use in a single inference of LLM to screen the inspiration candidates")
    parser.add_argument("--num_screening_keep_size", type=int, default=3, help="How many abstract to keep during one screening window")
    parser.add_argument("--chem_annotation_path", type=Path, default="./Data/chem_research_2024.xlsx")
    parser.add_argument("--if_use_strict_survey_question", type=int, default=1, help="whether to use the strict version of background survey and background question. strict version means the background should not have any close information to inspirations and the hypothesis, even if the close information is a commonly used method in that particular background question domain.")
    parser.add_argument("--custom_research_background_path", type=str, default="", help="the path to the research background file. The format is [research question, background survey], and saved in a json file. ")
    parser.add_argument("--custom_inspiration_corpus_path", type=str, default="", help="store title and abstract of the inspiration corpus; Should be a json file in a format of [[title, abstract], ...]; It will be automatically assigned with a default value if it is not assigned by users. The default value is './Data/Inspiration_Corpus_{}.json'.format(args.corpus_size). (The default value is the groundtruth inspiration papers for the Tomato-Chem Benchmark and random high-quality papers)")
    parser.add_argument("--background_question_id", type=int, default=-1, help="The background question id in background literatures. Since running for one background costs enough api callings, we only run for one background question at a time.")
    parser.add_argument("--output_dir", type=str, default="~/Checkpoints/test.json")
    parser.add_argument("--if_save", type=int, default=0, help="Whether save screening results")
    parser.add_argument("--if_select_based_on_similarity", type=int, default=0, help="whether select based on similarity; 0: select based on potential as inspirations; 1: select based on semantical similarity")
    parser.add_argument("--if_use_background_survey", type=int, default=1, help="Whether to use background survey. 0: not use (replace the survey as 'Survey not provided. Please overlook the survey.'); 1: use")
    parser.add_argument("--num_round_of_screening", type=int, default=1, help="how many rounds of screening we use. For each round, we use the selected inspirations from the previous round to screen the next round.")
    parser.add_argument("--corpus_size", type=int, default=300, help="The number of total inspirations (paper) corpus (both groundtruth insp papers and non-groundtruth insp papers)")
    args = parser.parse_args()

    assert args.api_type in [0, 1, 2]
    # assert args.if_save in [0, 1]
    assert args.num_screening_window_size >= 10
    # currently cannot adjust corresponding prompts by args.num_screening_keep_size (default prompt is three, else need to change the prompt)
    assert args.num_screening_keep_size in [3]
    assert args.if_use_strict_survey_question in [0, 1]
    assert args.if_save in [0, 1]
    assert args.if_select_based_on_similarity in [0, 1]
    assert args.if_use_background_survey in [0, 1]
    assert args.num_round_of_screening >= 1 and args.num_round_of_screening <= 4
    # args.output_dir = os.path.abspath(args.output_dir)

    ## initialize research question and background survey to text to use them for inference (by default they are set to those in the Tomato-Chem benchmark)
    if args.custom_research_background_path.strip() == "":
        custom_rq, custom_bs = None, None
        print("Using the research background in the Tomato-Chem benchmark.")
    else:
        assert os.path.exists(args.custom_research_background_path), f"The research background file does not exist: {args.custom_research_background_path}"
        with open(args.custom_research_background_path, 'r') as f:
            research_background = json.load(f)
        # research_background: [research question, background survey]
        assert len(research_background) == 2
        assert isinstance(research_background[0], str) and isinstance(research_background[1], str)
        custom_rq = research_background[0]
        custom_bs = research_background[1]
        print(f"Using custom research background. \nResearch question: \n{custom_rq}; \n\nBackground survey: \n{custom_bs}")

    ## change inspiration corpus path to the default corpus if it is not assigned by users
    if args.custom_inspiration_corpus_path.strip() == "":
        args.custom_inspiration_corpus_path = f'./Data/Inspiration_Corpus_{args.corpus_size}.json'
        print(f"Using the default inspiration corpus: {args.custom_inspiration_corpus_path}")
    else:
        assert os.path.exists(args.custom_inspiration_corpus_path), f"The inspiration corpus file does not exist: {args.custom_inspiration_corpus_path}"
        print(f"Using custom inspiration corpus: {args.custom_inspiration_corpus_path}")

    print("args: ", args)

    # run Screening
    if os.path.exists(args.output_dir):
        print("Warning: The output_dir already exists. Will skip this retrival.")
    else:
        screening = Screening(args, custom_rq=custom_rq, custom_bs=custom_bs)
        screening.run()

    print("Finished!")

if __name__ == '__main__':
    main()

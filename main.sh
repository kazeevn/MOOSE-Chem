#!/bin/bash
# sets api_type, api_key, base_url
source .env

# Function to display usage
usage() {
    echo "Usage: $0 [STEP] [OPTIONS]"
    echo ""
    echo "STEPS:"
    echo "  background       Step 1: Custom Research Background Dumping"
    echo "  corpus           Step 2: Custom Inspiration Corpus Construction" 
    echo "  retrieval        Step 3: Inspiration Retrieval"
    echo "  generation       Step 4: Hypothesis Composition"
    echo "  ranking          Step 5: Hypothesis Ranking"
    echo "  display          Step 6: Hypothesis Display"
    echo "  analysis         Step 7: Analysis (Groundtruth Hypothesis Ranking)"
    echo "  all              Run all steps sequentially"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 retrieval     # Run only inspiration retrieval"
    echo "  $0 all          # Run all steps"
    echo "  $0 generation   # Run only hypothesis composition"
    exit 1
}

# Parse command line arguments
STEP=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        background|corpus|retrieval|generation|ranking|display|analysis|all)
            STEP="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# If no step specified, show usage
if [[ -z "$STEP" ]]; then
    usage
fi

model_name_insp_retrieval="gpt-4.1-nano-2025-04-14"
model_name_gene="gpt-4.1-nano-2025-04-14"
model_name_eval="gpt-4.1-nano-2025-04-14"

experiment_name="wyformer_v0.1"
checkpoint_root_dir="./Checkpoints/"${experiment_name}
mkdir -p ${checkpoint_root_dir}
display_txt_file_path="hypothesis/"${experiment_name}".txt"
mkdir -p hypothesis
output_dir_postfix="output_dir_postfix"

# custom_research_background_path: set to "" if you want to use the default research background in TOMATO-Bench
custom_research_background_path=""
# custom_raw_inspiration_data_dir: raw custom inspiration data to process to inspiration corpus
custom_raw_inspiration_data_dir=""
# custom_inspiration_corpus_path: set to "" if you want to use the default inspiration corpus in TOMATO-Bench
custom_inspiration_corpus_path=""


# Function definitions for each step
run_background() {
    echo "=== Step 1: Custom Research Background Dumping ==="
    echo "NOTE: Modify 'research_question' and 'background_survey' in research_background_to_json() function"
    echo "      in ./Preprocessing/custom_research_background_dumping_and_output_displaying.py before running"
    python -u ./Preprocessing/custom_research_background_dumping_and_output_displaying.py --io_type 0 \
            --custom_research_background_path ${custom_research_background_path}
}

run_corpus() {
    echo "=== Step 2: Custom Inspiration Corpus Construction ==="
    python -u ./Preprocessing/construct_custom_inspiration_corpus.py \
            --raw_data_dir ${custom_raw_inspiration_data_dir} \
            --custom_inspiration_corpus_path ${custom_inspiration_corpus_path}
}

run_retrieval() {
    echo "=== Step 3: Inspiration Retrieval ==="
    python -u ./Method/inspiration_screening.py --model_name ${model_name_insp_retrieval} \
            --api_type ${api_type} --api_key ${api_key} --base_url ${base_url} \
            --chem_annotation_path ./Data/chem_research_2024.xlsx \
            --output_dir ${checkpoint_root_dir}/coarse_inspiration_search_${model_name_insp_retrieval}_${output_dir_postfix}.json \
            --corpus_size 150 --if_use_background_survey 1 --if_use_strict_survey_question 1 \
            --num_screening_window_size 15 --num_screening_keep_size 3 --num_round_of_screening 4 \
            --if_save 1 --background_question_id 0 --if_select_based_on_similarity 0 \
            --custom_research_background_path ${custom_research_background_path} \
            --custom_inspiration_corpus_path ${custom_inspiration_corpus_path}
}

run_generation() {
    echo "=== Step 4: Hypothesis Composition ==="
    python -u ./Method/hypothesis_generation.py --model_name ${model_name_gene} \
            --api_type ${api_type} --api_key ${api_key} --base_url ${base_url} \
            --chem_annotation_path ./Data/chem_research_2024.xlsx --corpus_size 150 --if_use_strict_survey_question 1 --if_use_background_survey 1 \
            --inspiration_dir ${checkpoint_root_dir}/coarse_inspiration_search_${model_name_insp_retrieval}_${output_dir_postfix}.json \
            --output_dir ${checkpoint_root_dir}/hypothesis_generation_${model_name_gene}_${output_dir_postfix}.json \
            --if_save 1 --if_load_from_saved 0 \
            --if_use_gdth_insp 0 --idx_round_of_first_step_insp_screening 2 \
            --num_mutations 3 --num_itr_self_refine 3  --num_self_explore_steps_each_line 3 --num_screening_window_size 12 --num_screening_keep_size 3 \
            --if_mutate_inside_same_bkg_insp 1 --if_mutate_between_diff_insp 1 --if_self_explore 0 --if_consider_external_knowledge_feedback_during_second_refinement 0 \
            --inspiration_ids -1  --recom_inspiration_ids  --recom_num_beam_size 5  --self_explore_inspiration_ids   --self_explore_num_beam_size 5 \
            --max_inspiration_search_steps 3 --background_question_id 0 \
            --custom_research_background_path ${custom_research_background_path} \
            --custom_inspiration_corpus_path ${custom_inspiration_corpus_path}
}

run_ranking() {
    echo "=== Step 5: Hypothesis Ranking ==="
    python -u ./Method/evaluate.py --model_name ${model_name_eval} \
            --api_type ${api_type} --api_key ${api_key} --base_url ${base_url} \
            --chem_annotation_path ./Data/chem_research_2024.xlsx --corpus_size 150 \
            --hypothesis_dir ${checkpoint_root_dir}/hypothesis_generation_${model_name_gene}_${output_dir_postfix}.json \
            --output_dir ${checkpoint_root_dir}/evaluation_${model_name_eval}_${output_dir_postfix}.json \
            --if_save 1 --if_load_from_saved 0 \
            --if_with_gdth_hyp_annotation 0 \
            --custom_inspiration_corpus_path ${custom_inspiration_corpus_path}
}

run_display() {
    echo "=== Step 6: Hypothesis Display ==="
    python -u ./Preprocessing/custom_research_background_dumping_and_output_displaying.py --io_type 1 \
            --evaluate_output_dir ${checkpoint_root_dir}/evaluation_${model_name_eval}_${output_dir_postfix}.json \
            --display_dir ${display_txt_file_path}
}

run_analysis() {
    echo "=== Step 7: Analysis (Groundtruth Hypothesis Ranking) ==="
    python -u ./Analysis/groundtruth_hyp_ranking.py --model_name ${model_name_eval} \
            --api_type ${api_type} --api_key ${api_key} --base_url ${base_url} \
            --evaluate_result_dir ${checkpoint_root_dir}/evaluation_${model_name_eval}_corpus_150_survey_1_gdthInsp_1_intraEA_1_interEA_1_bkgid_ \
            --if_save 1 --output_dir ${checkpoint_root_dir}/groundtruth_hypothesis_automatic_scores_four_aspects_${model_name_eval}.json
}

# Execute based on selected step
case $STEP in
    background)
        run_background
        ;;
    corpus)
        run_corpus
        ;;
    retrieval)
        run_retrieval
        ;;
    generation)
        run_generation
        ;;
    ranking)
        run_ranking
        ;;
    display)
        run_display
        ;;
    analysis)
        run_analysis
        ;;
    all)
        echo "Running all steps sequentially..."
        echo "Note: Steps 1 and 2 (background and corpus) are typically optional"
        echo "Starting with Step 3: Inspiration Retrieval"
        run_retrieval
        run_generation
        run_ranking
        run_display
        echo "=== All steps completed ==="
        ;;
esac




#!/bin/bash

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -m|--model)
            model="$2"
            shift
            ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
    shift
done

# Set default model if not provided
model="${model:-llama3-tl-q6k}"
echo "Model: $model"

# Define commands based on the model
case "$model" in
    llama3-tl-q4km)
        create_command="ollama create llama3-tl-q4km -f /Users/jethroestrada/Desktop/External_Projects/GPT/ResumeChatbot/open-webui/jet-modelfiles/llama3-8b/llama3-tl-q4km-8b-mradermacher-modelfile"
        run_command="ollama run llama3-tl-q4km"
        ;;
    llama3-tl-q6k)
        create_command="ollama create llama3-tl-q6k -f /Users/jethroestrada/Desktop/External_Projects/GPT/ResumeChatbot/open-webui/jet-modelfiles/llama3-8b/llama3-tl-q6k-8b-mradermacher-modelfile"
        run_command="ollama run llama3-tl-q6k"
        ;;
    llama3-tl-q8)
        create_command="ollama create llama3-tl-q8 -f /Users/jethroestrada/Desktop/External_Projects/GPT/ResumeChatbot/open-webui/jet-modelfiles/llama3-8b/llama3-tl-q8-8b-mradermacher-modelfile"
        run_command="ollama run llama3-tl-q8"
        ;;
    seallm-7b)
        pull_command="ollama pull adwidianjaya/seallm-7b-v2.5"
        create_command="ollama create seallm-7b-chat -f /Users/jethroestrada/Desktop/External_Projects/GPT/ResumeChatbot/open-webui/jet-modelfiles/seallm-7b/seallm-7b-v2.5-adwidianjaya-gemma-modelfile"
        run_command="ollama run seallm-7b-chat"
        ;;
    seallm-7b-chatml)
        create_command="ollama create seallm-7b-chatml -f /Users/jethroestrada/Desktop/External_Projects/GPT/ResumeChatbot/open-webui/jet-modelfiles/seallm-7b/seallm-7b-v2.5-chatml-q4km-modelfile"
        run_command="ollama run seallm-7b-chatml"
        ;;
    mistral)
        pull_command="ollama pull mistral:latest"
        create_command="ollama create jetresumemistral -f /Users/jethroestrada/Desktop/External_Projects/GPT/xturing-jet-examples/libs/ollama/modelfile-jet-resume/Modelfile"
        run_command="ollama run jetresumemistral"
        ;;
    gemma)
        pull_command="ollama pull gemma:2b"
        create_command="ollama create jetresumegemma -f /Users/jethroestrada/Desktop/External_Projects/GPT/xturing-jet-examples/libs/ollama/modelfile-jet-resume/Modelfile"
        run_command="ollama run jetresumegemma"
        ;;
    *)
        echo "Invalid model specified. Please specify 'mistral' or 'gemma'."
        exit 1
        ;;
esac

# Execute commands
# eval "$pull_command"
eval "$create_command"
echo "Running $model model on port 11434"
eval "$run_command"

# Usage:
# source create_model.sh --model llama3-tl-q6k

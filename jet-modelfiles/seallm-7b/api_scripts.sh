curl http://localhost:11434/api/generate -d '{
  "model": "seallm-7b-chatml",
  "prompt": "Paano magapply ng driver's license sa Las Piñas?",
  "stream": true,
  "options": {
    "num_ctx": 2048,
    "num_predict": 128,
    "repeat_last_n": 128,
    "repeat_penalty": 1.2,
    "temperature": 0.8,
    "seed": 0,
    "tfs_z": 1.2,
    "top_k": 20,
    "top_p": 0.7,
    "num_keep": 24,
    "stop": ["system\n", "user\n", "assistant\n", "<eos>"]
  }
}'
